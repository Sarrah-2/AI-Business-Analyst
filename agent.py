import os
import re
import sqlite3
import json

import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import matplotlib.pyplot as plt

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Keep this model name aligned with a model available to your Google AI Studio key.
model = genai.GenerativeModel("gemini-3.8-flash")

SCHEMA = """
Tables in the database:

products(product_id, name, category, price)
customers(customer_id, name, region, signup_date)
orders(order_id, customer_id, product_id, quantity, discount, order_date)

Notes:
- order_date is text in 'YYYY-MM-DD' format.
- To get revenue for an order: price * quantity * (1 - discount).
- Join orders to products via product_id, and to customers via customer_id.
- Use strftime('%Y-%m', order_date) to group by month.
"""


def build_schema_from_db(db_path):
    """Inspect a SQLite database and describe its tables and columns."""
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        lines = ["Tables in the database:"]
        for table in tables:
            # Table names come from SQLite's own metadata and are quoted.
            cursor.execute(f'PRAGMA table_info("{table}")')
            columns = [row[1] for row in cursor.fetchall()]
            lines.append(f'"{table}"({", ".join(columns)})')

    if len(lines) == 1:
        return "No user tables found in the database."
    return "\n".join(lines)


def clean_sql(text):
    """Remove markdown fences and whitespace from model output."""
    text = text.strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_sql(question, error_context=None, schema=SCHEMA):
    """Generate a query using only the supplied schema, or flag unsupported asks."""
    if error_context is None:
        prompt = f"""
You are a careful analytics assistant working with SQLite.

ACTUAL DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

Before writing SQL, decide whether the requested answer can be derived from
the listed tables and columns.

Rules:
- Use only the tables and columns in the actual schema above.
- Never invent a table, column, metric, or business fact.
- A revenue question requires a revenue field or enough fields to calculate it,
  such as price and quantity.
- A question about revenue by region also requires a region field or a valid
  join to a table containing region.
- A reviews dataset with only review IDs, dates, product IDs, ratings, and
  review text cannot answer sales or revenue questions.
- If the question cannot be answered, return exactly:
  UNSUPPORTED: <brief explanation of the missing data>
- Otherwise return one read-only SQLite SELECT query.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, REPLACE, ATTACH,
  DETACH, CREATE, or other database-modifying statements.
- Return only SQL or the UNSUPPORTED message, without markdown or code fences.
"""
    else:
        prompt = f"""
You are a careful SQLite expert.

ACTUAL DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

PREVIOUS SQL:
{error_context['sql']}

DATABASE ERROR:
{error_context['error']}

Correct the query using only the actual schema. Return one read-only SQLite
SELECT query. If the question cannot be answered from the schema, return:
UNSUPPORTED: <brief explanation of the missing data>
Return only SQL or the UNSUPPORTED message, without markdown.
"""

    response = model.generate_content(prompt)
    return clean_sql(response.text or "")


def _is_read_only_query(sql):
    """Basic query-shape validation before the SQLite authorizer runs."""
    cleaned = sql.strip()
    if not cleaned:
        return False

    # Permit a single statement only; strip a single trailing semicolon first.
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
    if ";" in cleaned:
        return False

    return cleaned.lower().startswith(("select ", "with "))


def run_sql(sql, db_path="store.db"):
    """Run a single read-only query, blocking database modifications."""
    if not _is_read_only_query(sql):
        raise ValueError("Only one read-only SELECT query is allowed.")

    blocked_actions = {
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_PRAGMA,
    }

    def authorizer(action, arg1, arg2, database_name, trigger_name):
        if action in blocked_actions:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    with sqlite3.connect(db_path) as connection:
        connection.set_authorizer(authorizer)
        try:
            return pd.read_sql_query(sql, connection)
        finally:
            connection.set_authorizer(None)


def ask_agent(question, max_attempts=3, schema=SCHEMA, db_path="store.db"):
    """Generate, validate, and execute SQL with limited error-recovery attempts."""
    error_context = None

    for _ in range(max_attempts):
        try:
            sql = generate_sql(question, error_context, schema)
        except Exception as error:
            return None, f"Could not generate a query: {error}"

        if not sql:
            return None, "The model returned an empty response. Please try again."

        if sql.upper().startswith("UNSUPPORTED:"):
            explanation = sql.split(":", 1)[1].strip()
            return None, explanation or "The uploaded dataset lacks required information."

        if not _is_read_only_query(sql):
            return None, (
                "The generated query was not a single read-only SELECT query, "
                "so it was blocked."
            )

        try:
            result = run_sql(sql, db_path)

            if result.empty:
                return None, (
                    "The query ran but returned no matching rows. "
                    "This is not the same as a numeric result of zero. "
                     "Try rephrasing the question or checking the available data."
                )

            return result, sql

        except Exception as error:
            error_context = {"sql": sql, "error": str(error)}

    return None, (
        "I couldn't generate a valid query after several attempts. "
        "Check the available columns or try rephrasing your question."
    )


def describe_table(table_name, db_path):
    """Create a plain-English overview of a selected table."""
    with sqlite3.connect(db_path) as connection:
        # table_name comes from the database's own table list in the UI.
        safe_name = table_name.replace('"', '""')
        sample = pd.read_sql_query(
            f'SELECT * FROM "{safe_name}" LIMIT 15',
            connection,
        )
        row_count = pd.read_sql_query(
            f'SELECT COUNT(*) AS n FROM "{safe_name}"',
            connection,
        )["n"].iloc[0]

    columns = list(sample.columns)
    sample_text = sample.to_string(index=False)

    prompt = f"""
You are a data analyst helping a colleague understand a dataset.

Table name: {table_name}
Total rows: {row_count}
Columns: {columns}

Sample data:
{sample_text}

Write a clear, friendly overview in 4-6 sentences covering what the dataset
appears to contain, what the columns mean, any obvious patterns, and example
questions it can support. Use plain business English. Do not write SQL.
Do not claim that the sample proves facts that are not visible in the data.
"""
    response = model.generate_content(prompt)
    return (response.text or "No overview was generated.").strip()


def explain_result(question, sql, result_df):
    """Explain the actual query result without inventing unsupported findings."""
    if result_df is None or result_df.empty:
        return "There are no result rows to interpret."

    # Keep prompt size manageable for larger query results.
    data_text = result_df.head(30).to_string(index=False)

    prompt = f"""
You are a careful business analyst.

User question:
{question}

SQL executed:
{sql}

Actual query results (up to 30 rows):
{data_text}

Write a short business insight in 3-5 sentences:
- Describe only findings supported by the result rows.
- Do not invent causes, numbers, regions, products, or trends.
- If the results do not establish a cause, describe it as a possibility,
  not a fact.
- Suggest one practical next step only if relevant.
"""
    response = model.generate_content(prompt)
    return (response.text or "No insight was generated.").strip()


def make_chart(question, result_df):
    """Optional command-line chart helper using actual query result columns."""
    if result_df is None or result_df.empty or result_df.shape[0] < 2:
        print("Not enough result data to create a chart.")
        return

    x_column = result_df.columns[0]
    numeric_columns = [
        column
        for column in result_df.select_dtypes(include="number").columns
        if column != x_column
    ]
    if not numeric_columns:
        print("No separate numeric measure is available for charting.")
        return

    y_column = numeric_columns[0]
    plt.figure(figsize=(9, 5))
    plt.bar(result_df[x_column].astype(str), result_df[y_column])
    plt.title(question)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("=" * 55)
    print("AI Business Analyst — ask about your store data")
    print("Type your question, or 'quit' to exit.")
    print("=" * 55)

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue

        result, sql_or_message = ask_agent(question)

        if result is None:
            print(f"\nUnable to answer: {sql_or_message}")
            continue

        print("\n=== SQL ===")
        print(sql_or_message)
        print("\n=== Data ===")
        print(result)
        print("\n=== AI Insight ===")
        try:
            print(explain_result(question, sql_or_message, result))
        except Exception as error:
            print(f"Could not generate an insight: {error}")
        print("\n=== Chart ===")
        make_chart(question, result)

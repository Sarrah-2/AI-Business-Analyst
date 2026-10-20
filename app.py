import os
import sqlite3
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

if not os.path.exists("store.db"):
    import create_database  # Creates the built-in demo database.

from agent import (
    SCHEMA,
    ask_agent,
    build_schema_from_db,
    describe_table,
    explain_result,
)

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 2.5rem; }
        div[data-testid="stChatInput"] textarea { font-size: 1rem; }
        .hero { font-size: 2.3rem; font-weight: 800; margin-bottom: .2rem; }
        .sub { color: #8b92a8; margin-top: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None


def clean_columns(dataframe):
    """Normalize column names so they are easier to use in SQL."""
    dataframe = dataframe.copy()
    dataframe.columns = (
        dataframe.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )
    return dataframe


def safe_table_name(name):
    """Convert a sheet name into a safe SQLite table name."""
    table = name.strip().lower().replace(" ", "_").replace("-", "_")
    return "".join(c for c in table if c.isalnum() or c == "_") or "sheet"


def list_tables(db_path):
    """Return table names in a SQLite database."""
    with sqlite3.connect(db_path) as connection:
        return [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        ]


# ---------------- Sidebar / data source ----------------
with st.sidebar:
    st.header("📁 Data Source")
    uploaded = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
    )

    active_db = "store.db"
    active_schema = SCHEMA

    if uploaded is not None:
        # A temporary SQLite database is used for the uploaded dataset.
        tmp_db = os.path.join(tempfile.gettempdir(), "uploaded_business_analyst.db")

        try:
            if uploaded.name.lower().endswith((".xlsx", ".xls")):
                excel_file = pd.ExcelFile(uploaded)
                sheet_info = []

                with sqlite3.connect(tmp_db) as connection:
                    for sheet_name in excel_file.sheet_names:
                        dataframe = clean_columns(
                            pd.read_excel(excel_file, sheet_name=sheet_name)
                        )
                        table_name = safe_table_name(sheet_name)
                        dataframe.to_sql(
                            table_name,
                            connection,
                            if_exists="replace",
                            index=False,
                        )
                        sheet_info.append(
                            (sheet_name, table_name, dataframe.shape[0], dataframe.shape[1])
                        )

                active_db = tmp_db
                active_schema = build_schema_from_db(tmp_db)
                st.success(f"Loaded {len(sheet_info)} sheet(s).")

                with st.expander("Sheets / tables"):
                    for original, table, rows, columns in sheet_info:
                        st.write(f"**{original}** → `{table}` · {rows} × {columns}")

            else:
                try:
                    dataframe = pd.read_csv(uploaded)
                except UnicodeDecodeError:
                    uploaded.seek(0)
                    dataframe = pd.read_csv(uploaded, encoding="latin-1")

                dataframe = clean_columns(dataframe)

                if dataframe.empty or len(dataframe.columns) == 0:
                    st.error("The uploaded CSV contains no usable data.")
                else:
                    with sqlite3.connect(tmp_db) as connection:
                        dataframe.to_sql(
                            "data",
                            connection,
                            if_exists="replace",
                            index=False,
                        )

                    active_db = tmp_db
                    active_schema = build_schema_from_db(tmp_db)
                    st.success(
                        f"Loaded {dataframe.shape[0]} rows, "
                        f"{dataframe.shape[1]} columns."
                    )
                    with st.expander("Columns"):
                        st.write(list(dataframe.columns))

        except Exception as error:
            st.error(f"Could not load this file: {error}")
            uploaded = None

    else:
        st.caption("Using the built-in demo store database.")

    st.divider()
    st.header("🕘 History")
    if st.session_state.history:
        for index, past_question in enumerate(reversed(st.session_state.history)):
            if st.button(past_question, key=f"history_{index}", width="stretch"):
                st.session_state.pending = past_question
    else:
        st.caption("Past questions appear here.")


# ---------------- Header ----------------
st.markdown(
    '<p class="hero">📊 AI Business Analyst</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub">Ask anything about your data — in plain English.</p>',
    unsafe_allow_html=True,
)

try:
    mode = (
        st.segmented_control(
            "Mode",
            ["Ask", "Explore"],
            default="Ask",
            label_visibility="collapsed",
        )
        or "Ask"
    )
except Exception:
    mode = st.radio(
        "Mode",
        ["Ask", "Explore"],
        horizontal=True,
        label_visibility="collapsed",
    )


# =========================================================
# EXPLORE MODE
# =========================================================
if mode == "Explore":
    tables = list_tables(active_db)
    if not tables:
        st.info("Upload a file to explore it.")
        # =========================================================
# ASK MODE
# =========================================================
else:
    if not st.session_state.history:
        st.caption("Try one of these:")

        if uploaded is None:
            col1, col2, col3 = st.columns(3)
            if col1.button("Revenue by month", width="stretch"):
                st.session_state.pending = (
                    "What is the total revenue for each month?"
                )
            if col2.button("Biggest revenue drop", width="stretch"):
                st.session_state.pending = (
                    "Which product category had the biggest revenue drop "
                    "from May to June 2026?"
                )
            if col3.button("Revenue by region", width="stretch"):
                st.session_state.pending = "How much revenue came from each region?"
        else:
            st.caption(
                "Ask questions about the columns in your uploaded dataset. "
                "Unsupported questions will be explained."
            )

    typed_question = st.chat_input("Ask a question about your data…")
    question = typed_question or st.session_state.pending
    st.session_state.pending = None

    if question:
        if question not in st.session_state.history:
            st.session_state.history.append(question)

        st.markdown(f"**❓ {question}**")

        with st.spinner("Generating SQL and querying the database…"):
            result, sql_or_message = ask_agent(
                question,
                schema=active_schema,
                db_path=active_db,
            )

        if result is None:
            st.warning("I couldn't answer this question using the available data.")
            st.info(
                sql_or_message
                or "Try rephrasing the question or inspect the dataset in Explore mode."
            )
        else:
            sql = sql_or_message

            with st.expander("View the SQL the AI generated"):
                st.code(sql, language="sql")

            left, right = st.columns([1, 1])

            with left:
                st.subheader("Data")
                st.dataframe(result, width="stretch", height=300)
                st.download_button(
                    "⬇️ Download CSV",
                    result.to_csv(index=False).encode("utf-8"),
                    "analysis.csv",
                    "text/csv",
                )

            with right:
                if result.empty:
                    st.caption("No chart available because the query returned no data.")
                elif result.shape[0] < 2 or result.shape[1] < 2:
                    st.caption("Not enough data to create a chart.")
                else:
                    x_column = result.columns[0]
                    numeric_columns = [
                        column
                                  for column in result.select_dtypes(include="number").columns
                        if column != x_column
                    ]

                    if not numeric_columns:
                        st.caption(
                            "No separate numeric measure is available for charting."
                        )
                    else:
                        y_column = numeric_columns[0]
                        st.subheader("Chart")
                        figure, axis = plt.subplots(figsize=(6, 4))
                        axis.bar(
                            result[x_column].astype(str),
                            result[y_column],
                        )
                        axis.set_xlabel(x_column)
                        axis.set_ylabel(y_column)
                        axis.set_title(f"{y_column} by {x_column}")
                        plt.xticks(rotation=45, ha="right")
                        plt.tight_layout()
                        st.pyplot(figure)
                        plt.close(figure)

            with st.spinner("Writing the business insight…"):
                try:
                    insight = explain_result(question, sql, result)
                    st.subheader("💡 Insight")
                    st.info(insight)
                except Exception as error:
                    st.warning(
                        "The query ran successfully, but the AI insight could "
                        f"not be generated: {error}"
                    )

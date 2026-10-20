# 📊 AI Business Analyst

**Ask questions about your business data in plain English and get SQL-backed results.**

AI Business Analyst is a Python and Streamlit application that makes structured data easier to explore. Upload a CSV or Excel file, ask a question in natural language, and view database query results without writing SQL manually.

The application uses Google Gemini to help generate SQL queries and explain query results. It inspects the uploaded dataset and builds a schema description so the model can work with the available tables and columns.

## 💡 Why this project?

Answering business questions often requires someone to understand the data, write SQL, run the query, and interpret the output. This project aims to simplify that workflow.

Example questions:

- What is the average customer rating?
- Which products have the lowest ratings?
- How much revenue came from each region?
- What was the total revenue for each month?

A question can only be answered when the uploaded data contains the necessary fields. For example, a customer-review file containing only review dates, product IDs, ratings, and review text cannot provide revenue figures unless the required sales information is also available.

## ✨ Features

| Feature | Description |
|---|---|
| 📂 CSV and Excel upload | Load structured datasets for analysis. |
| 🔎 Automatic schema inspection | Read table and column names from the SQLite database. |
| 💬 Natural-language analytics | Ask questions in everyday English and generate SQL for supported questions. |
| 🗄️ SQLite query execution | Execute read-only queries against the active database. |
| 🔁 SQL error recovery | Retry query generation when SQL execution fails, where supported by the implementation. |
| 📊 Result charts | Display a basic chart when the returned results contain suitable columns. |
| 📥 CSV export | Download query results for further analysis. |
| 💡 AI-generated insights | Produce a short business explanation based on the query and its results. |
| 🧭 Explore mode | Preview tables and request a plain-English overview. |
| 🕘 Query history | Revisit questions asked during the current session. |

> Features depend on the current code and should be tested locally. Chart selection is basic and may need improvement for different result shapes.

## 🧠 How it works

```text
Upload a CSV or Excel file
          ↓
Read the data and clean column names
          ↓
Load the data into a SQLite table
          ↓
Build a schema description from available columns
          ↓
Ask a question in natural language
          ↓
Gemini generates a SQL query
          ↓
Validate and execute the query
          ↓
Display results, a chart, and an AI-generated insight
```

For unsupported questions, the application should explain when the schema does not contain the information needed. For example, it should not calculate revenue from a reviews-only dataset with no revenue, price, or quantity fields.

## 🛠️ Technology stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Google Gemini |
| Interface | Streamlit |
| Database | SQLite |
| Data handling | pandas |
| Charts | matplotlib |
| Configuration | python-dotenv |

## 🚀 Getting started

### 1. Clone the repository

Replace the URL below with your actual GitHub repository URL:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create and activate a virtual environment

**Windows (Command Prompt):**

```bat
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

If the repository contains `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

Otherwise, install the main packages used by the project:

```bash
pip install streamlit pandas matplotlib python-dotenv google-generativeai openpyxl
```

For legacy `.xls` Excel files, you may also need:

```bash
pip install xlrd
```

### 4. Configure your Gemini API key

Create a file named `.env` in the project root with the following line:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Get an API key from [Google AI Studio](https://aistudio.google.com/). Confirm that the model name configured in `agent.py` is supported by your API key and installed SDK.

**Security:** Never commit `.env` or your actual API key to GitHub. Add `.env` to `.gitignore`.

### 5. Run the application

```bash
streamlit run app.py
```

If your version of the application uses a demo database initialized by `create_database.py`, make sure that file exists and correctly creates `store.db`. If the app uses only uploaded datasets, follow the workflow implemented in your current code instead.

## 🧪 Try it with a sample dataset

You can test the app with a CSV containing customer reviews, for example:

```csv
review_id,review_date,product_id,rating_1_to_5,review_text
1,2026-01-04,P001,5,"Leaves my skin soft and hydrated."
2,2026-01-09,P002,2,"The shampoo made my hair feel dry."
3,2026-01-15,P003,4,"Absorbs quickly and feels lightweight."
```

Try questions such as:

1. `What is the average rating?`
2. `Show the reviews with ratings below 3.`
3. `Which product IDs have the lowest average ratings?`
4. `Find the revenue.`

For the last question, a reviews-only dataset should report that revenue data is missing. To analyze revenue, upload a dataset containing revenue directly or fields such as price and quantity. Include a region column if you want to analyze revenue by region.

## 🔐 Reliability and data safety

- Upload only data you are permitted to use.
- Avoid uploading sensitive customer or company data unless your organization's policies permit sending relevant schema or query information to an external LLM provider.
- Generated SQL is intended to be read-only, but review and test the query-validation safeguards before using the app with important databases.
- Verify AI-generated explanations against the returned data before using them for business decisions.
- Test the application with known questions and expected answers to check query accuracy.
- Clearly label synthetic demo data; do not present it as real company data.

## 🔭 Possible future improvements

- More reliable chart selection based on query intent and result types
- A benchmark of natural-language questions with expected SQL and results
- Better support for follow-up questions and conversational context
- Stronger SQL validation and database access controls
- Customer-review text analytics, including complaint themes and sentiment
- Downloadable reports with charts and executive summaries
- Automated data-quality checks and clearer error diagnostics

## 📁 Suggested project structure

The structure below is an example. Keep only files that actually exist in your repository.

```text
ai-business-analyst/
├── app.py
├── agent.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Include `create_database.py` or `store.db` only if your current implementation uses them. Do not commit credentials or sensitive data. Only include a database file if it contains safe sample data.

## 👩‍💻 About

AI Business Analyst is a portfolio project exploring how large language models can connect natural-language questions with SQL-based analysis and business reporting.

**Author:** Sarrah Sadriwala  
**GitHub:** [Sarrah-2](https://github.com/Sarrah-2)

> Before publishing, replace the clone URL above with your actual repository URL and verify that every feature described here matches the code in your repository.

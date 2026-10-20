📊 AI Business Analyst
Ask questions about your business data in plain English and get SQL-backed results.
AI Business Analyst is a Python and Streamlit application designed to
make structured data easier to explore. Users can upload CSV or Excel
files, ask questions in natural language, and view the results of
database queries without manually writing SQL.

The application uses Google Gemini to help generate SQL queries and
explain query results. Uploaded datasets are inspected to build a schema
description, helping the model work with the tables and columns that are
actually available.

💡 Why this project?
Answering business questions often requires a person to understand the
data, write SQL, run the query, and interpret the output. This project
aims to simplify that process.

Example questions include:
- What is the average customer rating?
- Which products have the lowest ratings?
- How much revenue came from each region?
- What was the total revenue for each month?
Questions are only answerable when the uploaded data contains the
necessary fields. For example, a customer-review file containing only
review dates, product IDs, ratings, and review text cannot provide
revenue figures unless the required sales information is also available.

✨ Features

  Feature                             Description
  📂 CSV and Excel upload             Load structured datasets for
                                      analysis.

  🔎 Automatic schema inspection      Read table and column names from
                                      the SQLite database.

  💬 Natural-language analytics       Ask questions in everyday English
                                      and generate SQL for supported
                                      questions.

  🗄️ SQLite query execution           Execute read-only queries against
                                      the active database.

  🔁 Limited SQL error recovery       Retry query generation when SQL
                                      execution fails.

  📊 Automatic result charts          Display a basic chart when the
                                      returned results have suitable
                                      columns.

  📥 CSV export                       Download query results for further
                                      analysis.

  💡 AI-generated insights            Produce a short business
                                      explanation based on the query and
                                      its results.

  🧭 Explore mode                     Preview tables and request a
                                       plain-English overview.

  🕘 Query history                    Revisit previously asked questions
                                       during the session.
Features depend on the current code and should be tested in your local
environment. Chart selection is currently basic and may need further
improvement for different result shapes.

🧠 How it works
User uploads a CSV or Excel file
              |
              v
      Read and clean columns
              |
              v
   Load data into a SQLite table
              |
              v
  Build schema from actual columns
              |
              v
      User asks a question
              |
              v
 Gemini generates a read-only SQL query
              |
              v
    Validate and execute the query
              |
              v
  Show results, chart, and AI insight

For unsupported questions, the application is designed to explain when
the available schema does not contain the information needed to answer.
For example, it should not calculate revenue from a reviews-only dataset
with no revenue, price, or quantity fields.

🛠️ Technology stack
  Component       Technology
  Language        Python
  LLM             Google Gemini
  Interface       Streamlit
  Database        SQLite
  Data handling   pandas
  Charts          matplotlib
  Configuration   python-dotenv

🚀 Getting started

1. Clone your repository
Replace the placeholder with your GitHub repository URL.
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>

2. Create and activate a virtual environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python -m venv venv
source venv/bin/activate

3. Install dependencies
If your repository contains requirements.txt, run:
pip install -r requirements.txt
If you do not have a dependency file yet, the main packages used by this
project include:
pip install streamlit pandas matplotlib python-dotenv google-generativeai openpyxl
For legacy .xls Excel files, you may also need:
pip install xlrd

4. Configure Gemini
Create a .env file in the project root:
GEMINI_API_KEY=your_gemini_api_key
Get an API key from Google AI
Studio. Confirm that the model name
configured in agent.py is currently supported by your API key.

Security: Never commit your .env file or API key to GitHub. Add
.env to .gitignore.

5. Run the app
streamlit run app.py
If the app relies on the built-in demo database, ensure that
create_database.py is present and correctly initializes store.db.

🧪 Try it with a sample dataset
You can test the app with a CSV containing customer reviews, for
example:

review_id,review_date,product_id,rating_1_to_5,review_text
1,2026-01-04,P001,5,"Leaves my skin soft and hydrated."
2,2026-01-09,P002,2,"The shampoo made my hair feel dry."
3,2026-01-15,P003,4,"Absorbs quickly and feels lightweight."

Try questions such as:
1. "What is the average rating?"
2. "Show the reviews with ratings below 3."
3. "Which product IDs have the lowest average ratings?"
4. "Find the revenue."

For the last question, a reviews-only dataset should produce a message
explaining that revenue data is missing. To analyze revenue, upload a
dataset with revenue directly or with fields such as price and quantity,
plus region if you want revenue by region.

🔐 Reliability and data safety
- Use only data you are permitted to upload and process.
- Avoid uploading sensitive customer or company data unless your
  organization's policies permit sending relevant schema or query
  information to an external LLM provider.
- The generated SQL is intended to be read-only; still, review and
  test the query-validation safeguards before using the app with
  important databases.
- Verify AI-generated explanations against the returned data before
  using them for business decisions.
- Test with known questions and expected answers to check query
  accuracy.
- Synthetic demo data is for testing and should not be described as
  real company data.

🔭 Possible future improvements
- More reliable chart selection based on query intent and result types
- A benchmark of natural-language questions with expected SQL and
  results
- Better support for follow-up questions and conversational context
- Stronger SQL validation and database access controls
- Text analytics for customer reviews, including complaint themes and
  sentiment
- Downloadable reports with charts and executive summaries
- Automated data-quality checks and clearer error diagnostics

📁 Suggested project structure
ai-business-analyst/
├── app.py
├── agent.py
├── create_database.py
├── store.db
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
This is an example structure. Include only files that actually exist in
your repository. Avoid committing real credentials or sensitive data;
decide whether to include store.db based on whether it contains safe
sample data.

👩‍💻 About
AI Business Analyst is a portfolio project exploring how large language
models can connect natural-language questions with SQL-based analysis
and business reporting.

Author: <Sarrah Sadriwala>

GitHub: <YOUR_GITHUB_REPOSITORY_URL>

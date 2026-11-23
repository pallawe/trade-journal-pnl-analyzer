Trade Journal & P&L Analyzer

A Python-based trading journal application built using Streamlit, Pandas, and Supabase PostgreSQL.

Features

- Add, edit, and delete trades
- Import trades using CSV files
- Calculate Profit & Loss (P&L)
- Track win rate and profit factor
- Calculate maximum drawdown
- View equity curve and drawdown charts
- Analyze monthly and symbol-wise performance
- Store trade data persistently using Supabase PostgreSQL

Technology Stack

- Python
- Streamlit
- Pandas
- PostgreSQL (Supabase)
- pg8000
- Pytest

Setup Instructions

1. Clone the repository.

2. Install dependencies:
   
   "pip install -r requirements.txt"

3. Configure your database connection using Streamlit secrets.
   
   Create ".streamlit/secrets.toml":
   
   "DATABASE_URL = "your_supabase_connection_string""

4. Run the application:
   
   "streamlit run app.py"

Testing

Run:

"python -m pytest -v"

Project Structure

- "app.py" – Application interface
- "storage.py" – Database operations
- "analytics.py" – P&L and performance calculations
- "tests/" – Unit tests
- "sample_trades.csv" – Sample trade dataset

Note

Never upload your database credentials or "secrets.toml" file to GitHub.
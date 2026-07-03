# Smart Expense Tracker

A simple web application to track daily expenses, built using **Python Flask**
and **SQLite**. Designed to be beginner-friendly and easy to explain in a
college viva/presentation.

## Tech Stack
- Python 3
- Flask (web framework)
- SQLite (database, via Python's built-in `sqlite3` module)
- HTML, CSS, Bootstrap 5 (frontend)
- Matplotlib (for the pie chart)

## Project Structure
```
SmartExpenseTracker/
│
├── app.py                  # Main Flask app - contains all routes
├── database.py              # All database (SQLite) related functions
├── templates/                # HTML pages (Jinja2 templates)
│   ├── base.html             # Common layout (navbar, Bootstrap links)
│   ├── home.html             # Welcome page
│   ├── dashboard.html        # Menu with all options
│   ├── add_expense.html      # Form to add a new expense
│   ├── view_expenses.html    # Table showing all expenses
│   ├── search_expense.html   # Search form + results
│   ├── category_report.html  # Category-wise totals
│   └── pie_chart.html        # Pie chart page
├── static/
│   └── style.css             # Custom CSS on top of Bootstrap
├── expense.db                 # SQLite database file (auto-created)
├── requirements.txt
└── README.md
```

## How to Run

1. **Install dependencies** (Python 3 must already be installed):
   ```
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

   The `expense.db` SQLite file and the `expenses` table are created
   automatically the first time the app runs (see `database.init_db()`
   in `app.py`).

## How the App Works (for Viva Explanation)

- **app.py** is the entry point. It defines Flask *routes* - each route is a
  URL (like `/add-expense`) mapped to a Python function that decides what
  HTML page to show or what action to perform.
- **database.py** contains all SQL code. It uses Python's built-in `sqlite3`
  module (no ORM like SQLAlchemy) so the SQL queries are visible and easy to
  explain line by line.
- **templates/** folder contains HTML files using **Jinja2** templating
  (the `{{ }}` and `{% %}` syntax) so we can reuse data from Python inside
  HTML, and reuse the layout (`base.html`) across pages.
- **Bootstrap 5** is used only for styling (buttons, tables, forms, navbar) -
  no custom JavaScript framework is used, only a small `confirm()` popup for
  delete confirmation.
- **Pie Chart**: The `/pie-chart-image` route uses **Matplotlib** to draw a
  pie chart in memory and sends it back as a PNG image, which is displayed
  using a normal `<img>` tag on the `pie_chart.html` page.

## Database Schema

Table: `expenses`

| Column      | Type    | Description                          |
|-------------|---------|---------------------------------------|
| id          | INTEGER | Primary key, auto-incremented         |
| amount      | REAL    | Expense amount                        |
| category    | TEXT    | One of: Food, Travel, Shopping, Bills, Others |
| description | TEXT    | Short description of the expense      |
| date        | TEXT    | Date of the expense (YYYY-MM-DD)      |

## Features Implemented
1. Home page with a button to the dashboard
2. Dashboard with menu options
3. Add Expense (form -> saved to SQLite)
4. View Expenses (table with delete button)
5. Delete Expense (with confirmation popup)
6. Search Expense (by category / date / description)
7. Category Report (total spent per category)
8. Pie Chart (visual breakdown by category, using Matplotlib)

## Features Intentionally NOT Included
(To keep the project simple, as required)
- Login / Register / Authentication
- Edit Expense
- Monthly Report
- Export to CSV
- Flask Blueprints or SQLAlchemy ORM

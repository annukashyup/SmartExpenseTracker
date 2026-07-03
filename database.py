"""
database.py
------------
This file contains all the code related to the SQLite database.
It has simple functions to:
    1. Create the database and table (if they don't already exist)
    2. Add a new expense
    3. Get all expenses
    4. Delete an expense
    5. Search expenses
    6. Get category-wise totals (for the report and pie chart)

We use Python's built-in sqlite3 module - no external ORM (like SQLAlchemy)
is used, to keep things simple for beginners.
"""

import sqlite3

# Name of our database file
DB_NAME = "expense.db"


def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    row_factory is set so that we can access columns by name
    (like row["amount"]) instead of only by index (like row[1]).
    """
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """
    Creates the 'expenses' table if it does not already exist.
    This function should be called once when the app starts.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_expense(amount, category, description, date):
    """
    Inserts a new expense record into the expenses table.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (amount, category, description, date)
        VALUES (?, ?, ?, ?)
    """, (amount, category, description, date))

    connection.commit()
    connection.close()


def get_all_expenses():
    """
    Returns a list of all expenses, newest date first.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
    expenses = cursor.fetchall()

    connection.close()
    return expenses


def delete_expense(expense_id):
    """
    Deletes an expense record using its ID.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    connection.commit()
    connection.close()


def search_expenses(category=None, date=None, description=None):
    """
    Searches expenses based on category, date, and/or description.
    Any field that is left empty is simply ignored in the search.
    Uses a simple dynamic WHERE clause built from the given filters.
    """
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if date:
        query += " AND date = ?"
        params.append(date)

    if description:
        # LIKE with % allows partial text matching
        query += " AND description LIKE ?"
        params.append(f"%{description}%")

    query += " ORDER BY date DESC, id DESC"

    cursor.execute(query, params)
    results = cursor.fetchall()

    connection.close()
    return results


def get_category_totals():
    """
    Returns the total amount spent in each category as a dictionary.
    Example: {"Food": 2500, "Travel": 1800, ...}
    Categories with no expenses will show a total of 0.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
    """)
    rows = cursor.fetchall()

    connection.close()

    # Start with all fixed categories set to 0
    categories = ["Food", "Travel", "Shopping", "Bills", "Others"]
    totals = {cat: 0 for cat in categories}

    # Fill in the actual totals from the database
    for row in rows:
        totals[row["category"]] = row["total"]

    return totals

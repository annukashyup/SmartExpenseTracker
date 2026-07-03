"""
app.py
------
This is the main Flask application file for the Smart Expense Tracker.
It contains all the routes (URLs) of the web app.

Routes:
    /                -> Home page
    /dashboard       -> Dashboard with menu options
    /add-expense     -> Add a new expense (GET shows form, POST saves data)
    /view-expenses   -> View all expenses in a table
    /delete-expense  -> Delete an expense by ID
    /search-expense  -> Search expenses by category/date/description
    /category-report -> Show total spending per category
    /pie-chart       -> Show a pie chart of expenses by category
    /pie-chart-image -> Generates and returns the actual pie chart image (PNG)
"""

import io
import matplotlib
# Use 'Agg' backend so matplotlib can run without a GUI (needed for Flask)
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, send_file

import database  # our custom database.py file

app = Flask(__name__)

# List of fixed categories used throughout the app
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Others"]


# ---------------------- HOME PAGE ----------------------
@app.route("/")
def home():
    """Displays the simple welcome/home page."""
    return render_template("home.html")


# ---------------------- DASHBOARD ----------------------
@app.route("/dashboard")
def dashboard():
    """Displays the dashboard with menu options."""
    return render_template("dashboard.html")


# ---------------------- ADD EXPENSE ----------------------
@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    """
    GET  -> Show the 'Add Expense' form.
    POST -> Save the submitted expense data into the database.
    """
    if request.method == "POST":
        # Get form data submitted by the user
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        # Save to database
        database.add_expense(amount, category, description, date)

        # After saving, redirect to the "View Expenses" page
        return redirect(url_for("view_expenses"))

    # If GET request, just show the empty form
    return render_template("add_expense.html", categories=CATEGORIES)


# ---------------------- VIEW EXPENSES ----------------------
@app.route("/view-expenses")
def view_expenses():
    """Displays all expenses in a table."""
    expenses = database.get_all_expenses()
    return render_template("view_expenses.html", expenses=expenses)


# ---------------------- DELETE EXPENSE ----------------------
@app.route("/delete-expense/<int:expense_id>")
def delete_expense(expense_id):
    """
    Deletes an expense using its ID.
    The confirmation ("Are you sure?") is handled on the front-end
    using a simple JavaScript confirm() dialog before this link is followed.
    """
    database.delete_expense(expense_id)
    return redirect(url_for("view_expenses"))


# ---------------------- SEARCH EXPENSE ----------------------
@app.route("/search-expense", methods=["GET", "POST"])
def search_expense():
    """
    GET  -> Show the search form.
    POST -> Run the search based on the filters given and show results.
    """
    results = []
    searched = False  # tells the template whether a search was performed

    if request.method == "POST":
        category = request.form.get("category")
        date = request.form.get("date")
        description = request.form.get("description")

        results = database.search_expenses(category, date, description)
        searched = True

    return render_template(
        "search_expense.html",
        categories=CATEGORIES,
        results=results,
        searched=searched
    )


# ---------------------- CATEGORY REPORT ----------------------
@app.route("/category-report")
def category_report():
    """Shows the total amount spent in each category."""
    totals = database.get_category_totals()
    return render_template("category_report.html", totals=totals)


# ---------------------- PIE CHART PAGE ----------------------
@app.route("/pie-chart")
def pie_chart():
    """Displays the pie chart page (the actual image comes from another route)."""
    return render_template("pie_chart.html")


# ---------------------- PIE CHART IMAGE ----------------------
@app.route("/pie-chart-image")
def pie_chart_image():
    """
    Generates a pie chart using Matplotlib based on category totals
    and returns it directly as a PNG image.
    """
    totals = database.get_category_totals()

    labels = list(totals.keys())
    values = list(totals.values())

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(6, 6))

    # If there is no data at all, show a placeholder message instead of a blank chart
    if sum(values) == 0:
        ax.text(0.5, 0.5, "No expense data available",
                ha="center", va="center", fontsize=12)
        ax.axis("off")
    else:
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Expenses by Category")

    # Save the chart to memory (instead of a file on disk)
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format="png", bbox_inches="tight")
    img_bytes.seek(0)
    plt.close(fig)  # free up memory

    return send_file(img_bytes, mimetype="image/png")


# ---------------------- RUN THE APP ----------------------
if __name__ == "__main__":
    database.init_db()   # make sure the table exists before starting
    app.run(debug=True)

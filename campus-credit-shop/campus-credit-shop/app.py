import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "campus_shop.db")

app = Flask(__name__)
app.secret_key = "campus-credit-shop-dev-secret"  # fine for a college project demo

ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

CATEGORIES = ["Stationery", "Books", "Lab Materials", "Canteen", "Merchandise"]
# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(reset=False):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    fresh = reset or not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            erp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            department TEXT,
            semester INTEGER,
            email TEXT,
            phone TEXT,
            credit_limit REAL DEFAULT 5000,
            credit_used REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            emoji TEXT DEFAULT '📦'
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            erp_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY (erp_id) REFERENCES students(erp_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            erp_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            qty INTEGER NOT NULL,
            amount REAL NOT NULL,
            billed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (erp_id) REFERENCES students(erp_id)
        );
        """
    )

    if fresh:
        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            students = [
                ("2420666", "Annu Kumari", "pass123", "AI & DS", 4, "annu@college.edu", "9876500001", 5000, 840),
                ("2420712", "Rohit Verma", "pass123", "CSE", 4, "rohit@college.edu", "9876500002", 5000, 0),
                ("2420788", "Simran Kaur", "pass123", "ECE", 2, "simran@college.edu", "9876500003", 3000, 1250),
                ("2420801", "Karan Mehta", "pass123", "AI & DS", 4, "karan@college.edu", "9876500004", 5000, 4850),
            ]
            cur.executemany(
                "INSERT INTO students (erp_id, name, password, department, semester, email, phone, credit_limit, credit_used) VALUES (?,?,?,?,?,?,?,?,?)",
                students,
            )

        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            products = [
                ("Notebook (200 pages)", "Stationery", 50, 120, "📓"),
                ("Blue Ball Pen", "Stationery", 10, 300, "🖊️"),
                ("Highlighter Set", "Stationery", 90, 40, "🖍️"),
                ("Data Structures Textbook", "Books", 650, 15, "📘"),
                ("Python Programming Guide", "Books", 480, 20, "📗"),
                ("Lab Coat", "Lab Materials", 650, 25, "🥼"),
                ("Safety Goggles", "Lab Materials", 220, 30, "🥽"),
                ("Digital Multimeter", "Lab Materials", 950, 10, "🔌"),
                ("Veg Sandwich", "Canteen", 60, 50, "🥪"),
                ("Cold Coffee", "Canteen", 70, 50, "🥤"),
                ("Samosa (2 pcs)", "Canteen", 30, 80, "🥟"),
                ("College Hoodie", "Merchandise", 899, 35, "🧥"),
                ("College Mug", "Merchandise", 199, 45, "☕"),
                ("Sticker Pack", "Merchandise", 49, 100, "🏷️"),
            ]
            cur.executemany(
                "INSERT INTO products (name, category, price, stock, emoji) VALUES (?,?,?,?,?)",
                products,
            )

        cur.execute("SELECT COUNT(*) FROM transactions")
        if cur.fetchone()[0] == 0:
            sample_tx = [
                ("2420666", "Notebook (200 pages)", 2, 100, 0, "2026-06-10 10:15"),
                ("2420666", "Blue Ball Pen", 4, 40, 0, "2026-06-10 10:15"),
                ("2420666", "Veg Sandwich", 1, 60, 0, "2026-06-18 13:02"),
                ("2420666", "Cold Coffee", 1, 70, 0, "2026-06-18 13:02"),
                ("2420666", "Sticker Pack", 1, 49, 0, "2026-06-20 09:40"),
                ("2420788", "Lab Coat", 1, 650, 0, "2026-06-05 11:00"),
                ("2420788", "Safety Goggles", 1, 220, 0, "2026-06-05 11:00"),
                ("2420788", "College Mug", 1, 199, 0, "2026-06-22 16:20"),
                ("2420788", "Data Structures Textbook", 0, 0, 0, "2026-06-25 12:00"),
                ("2420801", "College Hoodie", 1, 899, 0, "2026-06-01 10:00"),
                ("2420801", "Digital Multimeter", 1, 950, 0, "2026-06-02 15:30"),
                ("2420801", "Data Structures Textbook", 2, 1300, 0, "2026-06-08 09:10"),
                ("2420801", "Python Programming Guide", 3, 1440, 0, "2026-06-15 14:45"),
                ("2420801", "Lab Coat", 1, 650, 0, "2026-06-19 10:05"),
                ("2420801", "Samosa (2 pcs)", 2, 60, 0, "2026-06-27 13:15"),
                ("2420801", "Cold Coffee", 3, 210, 0, "2026-06-27 13:15"),
            ]
            # remove the zero-amount placeholder row
            sample_tx = [t for t in sample_tx if t[3] > 0]
            cur.executemany(
                "INSERT INTO transactions (erp_id, product_name, qty, amount, billed, created_at) VALUES (?,?,?,?,?,?)",
                sample_tx,
            )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def current_student():
    erp_id = session.get("erp_id")
    if not erp_id:
        return None
    db = get_db()
    return db.execute("SELECT * FROM students WHERE erp_id = ?", (erp_id,)).fetchone()


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("erp_id"):
            flash("Please log in with your ERP ID to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin login required.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_globals():
    return {"cart_count": get_cart_count(), "student": current_student()}


def get_cart_count():
    erp_id = session.get("erp_id")
    if not erp_id:
        return 0
    db = get_db()
    row = db.execute(
        "SELECT COALESCE(SUM(qty),0) AS c FROM cart_items WHERE erp_id = ?", (erp_id,)
    ).fetchone()
    return row["c"] or 0


# ---------------------------------------------------------------------------
# Public / Auth routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        erp_id = request.form.get("erp_id", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE erp_id = ?", (erp_id,)
        ).fetchone()
        if student is None or student["password"] != password:
            flash("Invalid ERP ID or password.", "error")
            return render_template("login.html")
        session.clear()
        session["erp_id"] = erp_id
        flash(f"Welcome back, {student['name'].split()[0]}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Student routes
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    student = current_student()
    db = get_db()
    recent = db.execute(
        "SELECT * FROM transactions WHERE erp_id = ? ORDER BY id DESC LIMIT 5",
        (student["erp_id"],),
    ).fetchall()
    available = student["credit_limit"] - student["credit_used"]
    return render_template("dashboard.html", student=student, recent=recent, available=available)


@app.route("/shop")
@login_required
def shop():
    db = get_db()
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if query:
        sql += " AND name LIKE ?"
        params.append(f"%{query}%")
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY category, name"

    products = db.execute(sql, params).fetchall()
    return render_template(
        "shop.html", products=products, categories=CATEGORIES, query=query, active_category=category
    )


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    db = get_db()
    erp_id = session["erp_id"]
    qty = max(1, int(request.form.get("qty", 1)))

    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("shop"))

    if product["stock"] < qty:
        flash(f"Only {product['stock']} unit(s) of {product['name']} left in stock.", "error")
        return redirect(url_for("shop"))

    existing = db.execute(
        "SELECT * FROM cart_items WHERE erp_id = ? AND product_id = ?", (erp_id, product_id)
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE cart_items SET qty = qty + ? WHERE id = ?", (qty, existing["id"])
        )
    else:
        db.execute(
            "INSERT INTO cart_items (erp_id, product_id, qty) VALUES (?,?,?)",
            (erp_id, product_id, qty),
        )
    db.commit()
    flash(f"Added {product['name']} to your cart.", "success")
    return redirect(url_for("shop"))


@app.route("/cart")
@login_required
def cart():
    db = get_db()
    erp_id = session["erp_id"]
    items = db.execute(
        """SELECT cart_items.id AS cart_id, cart_items.qty, products.*
           FROM cart_items JOIN products ON cart_items.product_id = products.id
           WHERE cart_items.erp_id = ?""",
        (erp_id,),
    ).fetchall()
    total = sum(item["price"] * item["qty"] for item in items)
    student = current_student()
    available = student["credit_limit"] - student["credit_used"]
    return render_template("cart.html", items=items, total=total, available=available)


@app.route("/cart/remove/<int:cart_id>", methods=["POST"])
@login_required
def remove_from_cart(cart_id):
    db = get_db()
    db.execute(
        "DELETE FROM cart_items WHERE id = ? AND erp_id = ?", (cart_id, session["erp_id"])
    )
    db.commit()
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    db = get_db()
    erp_id = session["erp_id"]
    student = current_student()

    items = db.execute(
        """SELECT cart_items.id AS cart_id, cart_items.qty, products.*
           FROM cart_items JOIN products ON cart_items.product_id = products.id
           WHERE cart_items.erp_id = ?""",
        (erp_id,),
    ).fetchall()

    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("shop"))

    total = sum(item["price"] * item["qty"] for item in items)
    available = student["credit_limit"] - student["credit_used"]

    if total > available:
        flash(
            f"Credit limit exceeded! Available credit is \u20b9{available:.0f}, "
            f"but this order totals \u20b9{total:.0f}. Please remove items or clear dues.",
            "error",
        )
        return redirect(url_for("cart"))

    for item in items:
        if item["stock"] < item["qty"]:
            flash(f"Insufficient stock for {item['name']}.", "error")
            return redirect(url_for("cart"))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for item in items:
        db.execute(
            "INSERT INTO transactions (erp_id, product_name, qty, amount, billed, created_at) VALUES (?,?,?,?,0,?)",
            (erp_id, item["name"], item["qty"], item["price"] * item["qty"], now),
        )
        db.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?", (item["qty"], item["id"])
        )

    db.execute(
        "UPDATE students SET credit_used = credit_used + ? WHERE erp_id = ?", (total, erp_id)
    )
    db.execute("DELETE FROM cart_items WHERE erp_id = ?", (erp_id,))
    db.commit()

    flash(f"Order placed! \u20b9{total:.0f} added to your Campus Credit Balance.", "success")
    return redirect(url_for("transactions"))


@app.route("/transactions")
@login_required
def transactions():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM transactions WHERE erp_id = ? ORDER BY id DESC",
        (session["erp_id"],),
    ).fetchall()
    return render_template("transactions.html", rows=rows)


@app.route("/semester-bill")
@login_required
def semester_bill():
    db = get_db()
    student = current_student()
    rows = db.execute(
        "SELECT * FROM transactions WHERE erp_id = ? AND billed = 0 ORDER BY created_at",
        (student["erp_id"],),
    ).fetchall()
    total = sum(r["amount"] for r in rows)
    available = student["credit_limit"] - student["credit_used"]
    return render_template(
        "semester_bill.html", rows=rows, total=total, student=student, available=available
    )


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", student=current_student())


# ---------------------------------------------------------------------------
# Admin / Shopkeeper routes
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip()
        password = request.form.get("password", "")
        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            flash("Welcome back, Admin.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    total_students = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    total_products = db.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    total_revenue = db.execute("SELECT COALESCE(SUM(amount),0) s FROM transactions").fetchone()["s"]
    pending_credit = db.execute("SELECT COALESCE(SUM(credit_used),0) s FROM students").fetchone()["s"]
    low_stock = db.execute("SELECT * FROM products WHERE stock <= 15 ORDER BY stock ASC").fetchall()
    recent_tx = db.execute(
        """SELECT transactions.*, students.name AS student_name
           FROM transactions JOIN students ON transactions.erp_id = students.erp_id
           ORDER BY transactions.id DESC LIMIT 8"""
    ).fetchall()
    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_products=total_products,
        total_revenue=total_revenue,
        pending_credit=pending_credit,
        low_stock=low_stock,
        recent_tx=recent_tx,
    )


@app.route("/admin/products", methods=["GET", "POST"])
@admin_required
def manage_products():
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            price = float(request.form.get("price", 0) or 0)
            stock = int(request.form.get("stock", 0) or 0)
            emoji = request.form.get("emoji", "📦").strip() or "📦"
            if name and category and price > 0:
                db.execute(
                    "INSERT INTO products (name, category, price, stock, emoji) VALUES (?,?,?,?,?)",
                    (name, category, price, stock, emoji),
                )
                db.commit()
                flash(f"Added product: {name}", "success")
            else:
                flash("Please fill in all product fields correctly.", "error")
        elif action == "update_stock":
            product_id = request.form.get("product_id")
            stock = int(request.form.get("stock", 0) or 0)
            db.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
            db.commit()
            flash("Stock updated.", "success")
        elif action == "delete":
            product_id = request.form.get("product_id")
            db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            db.commit()
            flash("Product deleted.", "success")
        return redirect(url_for("manage_products"))

    products = db.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    return render_template("manage_products.html", products=products, categories=CATEGORIES)


@app.route("/admin/students")
@admin_required
def manage_students():
    db = get_db()
    students = db.execute("SELECT * FROM students ORDER BY name").fetchall()
    return render_template("manage_students.html", students=students)


@app.route("/admin/students/bill/<erp_id>", methods=["POST"])
@admin_required
def generate_bill(erp_id):
    db = get_db()
    db.execute(
        "UPDATE transactions SET billed = 1 WHERE erp_id = ? AND billed = 0", (erp_id,)
    )
    db.execute("UPDATE students SET credit_used = 0 WHERE erp_id = ?", (erp_id,))
    db.commit()
    flash(f"Semester bill generated and credit balance cleared for {erp_id}.", "success")
    return redirect(url_for("manage_students"))


@app.route("/admin/reports")
@admin_required
def reports():
    db = get_db()
    by_category = db.execute(
        """SELECT products.category AS category, COALESCE(SUM(transactions.amount),0) AS total
           FROM transactions
           JOIN products ON products.name = transactions.product_name
           GROUP BY products.category
           ORDER BY total DESC"""
    ).fetchall()
    top_products = db.execute(
        """SELECT product_name, SUM(qty) AS units, SUM(amount) AS revenue
           FROM transactions GROUP BY product_name ORDER BY revenue DESC LIMIT 6"""
    ).fetchall()
    top_students = db.execute(
        "SELECT name, erp_id, credit_used FROM students ORDER BY credit_used DESC LIMIT 6"
    ).fetchall()
    return render_template(
        "reports.html", by_category=by_category, top_products=top_products, top_students=top_students
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Admin logged out.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()

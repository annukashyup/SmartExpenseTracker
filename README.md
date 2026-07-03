Campus Credit Shop
An ERP-linked campus shop where students log in with their existing ERP ID, buy items on credit, and settle everything in one consolidated bill at semester end.

Features
Student side: ERP ID login, product catalog with search/category filters, cart, credit-limit-aware checkout, transaction history, and a semester bill statement.
Admin / shopkeeper side: dashboard with revenue and low-stock alerts, product management (add / update stock / delete), student credit overview, semester bill generation (marks transactions billed and resets balance), and a simple reports page with a revenue-by-category chart.
Guardrails: checkout blocks any order that would exceed a student's credit limit, and blocks orders that exceed available stock.
Tech stack
Python 3 + Flask
SQLite (file-based, no server setup needed)
Jinja2 templates, vanilla CSS/JS, Chart.js (via CDN) for the reports page
Setup
cd campus-credit-shop
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
Then open http://127.0.0.1:5000 in your browser.

The SQLite database (database/campus_shop.db) is created automatically on first run and seeded with sample students, products, and transactions.

Demo logins
Students (password for all: pass123)

ERP ID	Name	Credit used / limit
2420666	Annu Kumari	₹840 / ₹5,000
2420712	Rohit Verma	₹0 / ₹5,000
2420788	Simran Kaur	₹1,250 / ₹3,000
2420801	Karan Mehta	₹4,850 / ₹5,000 (near limit — good for testing the credit-limit block)
Admin / shopkeeper

Admin ID: admin
Password: admin123
Resetting the demo data
Delete database/campus_shop.db and restart the app — it will be recreated and reseeded automatically.

Project structure
campus-credit-shop/
├── app.py                  # Flask routes + SQLite logic
├── requirements.txt
├── database/
│   └── campus_shop.db      # created automatically
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── images/
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html / admin_login.html
    ├── dashboard.html
    ├── shop.html / cart.html
    ├── transactions.html / semester_bill.html
    ├── profile.html
    ├── admin_dashboard.html
    ├── manage_products.html / manage_students.html
    └── reports.html
Where this fits with the real ERP
For this project, the ERP ID is only used to authenticate — student records live in this app's own database, seeded with sample data. In a real deployment, the "Generate bill" action in the admin panel is the hook point where the semester total would be pushed into the college's actual ERP fee portal instead of just being reset locally.

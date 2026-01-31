import os
import sys
import random
from datetime import datetime, timedelta
from urllib.parse import quote
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")
if not DB_URI:
    raise SystemExit("DB_URI not set in environment")

url = make_url(DB_URI)
username = url.username or ""
password = url.password or ""
host = url.host or "127.0.0.1"
port = url.port or 3306
dbname = url.database

if not dbname:
    raise SystemExit("Database name is missing in DB_URI")

# Server-level URI without database to create DB if missing
server_uri = f"mysql+pymysql://{quote(username)}:{quote(password)}@{host}:{port}/"
server_engine = create_engine(server_uri, pool_pre_ping=True)

print(f"Ensuring database exists: {dbname}")
with server_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))

# Connect to target DB
engine = create_engine(DB_URI, pool_pre_ping=True)

print("Creating tables if not exist...")
with engine.begin() as conn:
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(80) NOT NULL,
            budget DECIMAL(12,2) NOT NULL DEFAULT 0
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INT PRIMARY KEY AUTO_INCREMENT,
            department_id INT,
            first_name VARCHAR(60) NOT NULL,
            last_name VARCHAR(60) NOT NULL,
            email VARCHAR(120) UNIQUE,
            salary DECIMAL(12,2) DEFAULT 0,
            hired_at DATE,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(80) NOT NULL,
            description TEXT
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            company_name VARCHAR(120) NOT NULL,
            contact_email VARCHAR(120)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            category_id INT,
            supplier_id INT,
            name VARCHAR(120) NOT NULL,
            sku VARCHAR(64) UNIQUE,
            price DECIMAL(10,2) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INT PRIMARY KEY AUTO_INCREMENT,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            unit_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INT PRIMARY KEY AUTO_INCREMENT,
            order_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            method VARCHAR(40) NOT NULL,
            status VARCHAR(20) NOT NULL,
            paid_at TIMESTAMP NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS shipments (
            id INT PRIMARY KEY AUTO_INCREMENT,
            order_id INT NOT NULL,
            carrier VARCHAR(60),
            tracking_number VARCHAR(120),
            status VARCHAR(20) NOT NULL,
            shipped_at TIMESTAMP NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        """
    ))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT PRIMARY KEY AUTO_INCREMENT,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            rating INT NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """
    ))

def parse_args(argv):
    # default modest targets
    target_customers = 100
    target_orders = 1000
    for i, a in enumerate(argv):
        if a == "--customers" and i + 1 < len(argv):
            try:
                target_customers = int(argv[i + 1])
            except ValueError:
                pass
        if a == "--orders" and i + 1 < len(argv):
            try:
                target_orders = int(argv[i + 1])
            except ValueError:
                pass
    # Additional sizes
    target_categories = 50
    target_suppliers = 200
    target_products = 2000
    target_order_items = 200000
    target_payments = target_orders
    target_shipments = int(target_orders * 0.8)
    target_reviews = 100000
    target_employees = 300
    target_departments = 12

    keys = {
        "--categories": "target_categories",
        "--suppliers": "target_suppliers",
        "--products": "target_products",
        "--order-items": "target_order_items",
        "--payments": "target_payments",
        "--shipments": "target_shipments",
        "--reviews": "target_reviews",
        "--employees": "target_employees",
        "--departments": "target_departments",
    }
    for i, a in enumerate(argv):
        if a in keys and i + 1 < len(argv):
            try:
                val = int(argv[i + 1])
                locals()[keys[a]] = val  # won't persist; handled below
            except ValueError:
                pass

    # Return packed
    return {
        "customers": target_customers,
        "orders": target_orders,
        "categories": target_categories,
        "suppliers": target_suppliers,
        "products": target_products,
        "order_items": target_order_items,
        "payments": target_payments,
        "shipments": target_shipments,
        "reviews": target_reviews,
        "employees": target_employees,
        "departments": target_departments,
    }


def rand_name(i: int) -> str:
    firsts = ["Alex","Sam","Jordan","Taylor","Casey","Riley","Avery","Jamie","Morgan","Drew"]
    lasts = ["Smith","Johnson","Brown","Davis","Miller","Wilson","Moore","Taylor","Anderson","Thomas"]
    return f"{random.choice(firsts)} {random.choice(lasts)} #{i}"


def bulk_seed(engine):
    targets = parse_args(sys.argv[1:])
    target_customers = targets["customers"]
    target_orders = targets["orders"]
    print("Seeding data targets -> "
          f"customers: {target_customers}, orders: {target_orders}, "
          f"categories: {targets['categories']}, suppliers: {targets['suppliers']}, products: {targets['products']}, "
          f"order_items: {targets['order_items']}, payments: {targets['payments']}, shipments: {targets['shipments']}, reviews: {targets['reviews']}, "
          f"employees: {targets['employees']}, departments: {targets['departments']}")

    with engine.begin() as conn:
        # Ensure baseline rows exist
        count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        if count == 0:
            conn.execute(text("INSERT INTO customers (name, email) VALUES (:n,:e)"), [
                {"n": "Alice", "e": "alice@example.com"},
                {"n": "Bob", "e": "bob@example.com"},
                {"n": "Charlie", "e": "charlie@example.com"}
            ])
            count = 3

        # Top-up customers to target
        if count < target_customers:
            to_add = target_customers - count
            print(f"Adding {to_add} customers to reach {target_customers}...")
            batch = []
            for i in range(1, to_add + 1):
                name = rand_name(count + i)
                email = f"user{count + i}@example.com"
                batch.append({"n": name, "e": email})
                if len(batch) >= 1000:
                    conn.execute(text("INSERT INTO customers (name, email) VALUES (:n,:e)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO customers (name, email) VALUES (:n,:e)"), batch)

        # Departments
        dep_count = conn.execute(text("SELECT COUNT(*) FROM departments")).scalar() or 0
        if dep_count < targets["departments"]:
            to_add = targets["departments"] - dep_count
            batch = [{"n": f"Department {dep_count + i}", "b": round(random.uniform(10000, 500000), 2)} for i in range(1, to_add + 1)]
            conn.execute(text("INSERT INTO departments (name, budget) VALUES (:n,:b)"), batch)

        # Employees
        dep_total = conn.execute(text("SELECT COUNT(*) FROM departments")).scalar() or 0
        emp_count = conn.execute(text("SELECT COUNT(*) FROM employees")).scalar() or 0
        if emp_count < targets["employees"] and dep_total > 0:
            to_add = targets["employees"] - emp_count
            batch = []
            for i in range(1, to_add + 1):
                fn = random.choice(["Alex","Sam","Jordan","Taylor","Casey","Riley","Avery","Jamie","Morgan","Drew"]) 
                ln = random.choice(["Smith","Johnson","Brown","Davis","Miller","Wilson","Moore","Taylor","Anderson","Thomas"]) 
                email = f"{fn.lower()}.{ln.lower()}.{emp_count + i}@example.com"
                dept = random.randint(1, dep_total)
                salary = round(random.uniform(30000, 200000), 2)
                hired = datetime.now() - timedelta(days=random.randint(0, 3650))
                batch.append({"d": dept, "fn": fn, "ln": ln, "e": email, "s": salary, "h": hired.date()})
                if len(batch) >= 1000:
                    conn.execute(text("INSERT INTO employees (department_id, first_name, last_name, email, salary, hired_at) VALUES (:d,:fn,:ln,:e,:s,:h)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO employees (department_id, first_name, last_name, email, salary, hired_at) VALUES (:d,:fn,:ln,:e,:s,:h)"), batch)

        # Count customers for FK range
        cust_total = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar() or 0

        # Ensure baseline orders exist
        count_o = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        if count_o == 0:
            conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (:c,:a,:s)"), [
                {"c": 1, "a": 120.50, "s": "paid"},
                {"c": 1, "a": 75.00, "s": "paid"},
                {"c": 2, "a": 300.00, "s": "shipped"},
                {"c": 3, "a": 45.99, "s": "pending"}
            ])
            count_o = 4

        # Categories
        cat_count = conn.execute(text("SELECT COUNT(*) FROM categories")).scalar() or 0
        if cat_count < targets["categories"]:
            to_add = targets["categories"] - cat_count
            conn.execute(text("INSERT INTO categories (name, description) VALUES (:n,:d)"), [
                {"n": f"Category {cat_count + i}", "d": f"Description for category {cat_count + i}"} for i in range(1, to_add + 1)
            ])

        # Suppliers
        sup_count = conn.execute(text("SELECT COUNT(*) FROM suppliers")).scalar() or 0
        if sup_count < targets["suppliers"]:
            to_add = targets["suppliers"] - sup_count
            conn.execute(text("INSERT INTO suppliers (company_name, contact_email) VALUES (:n,:e)"), [
                {"n": f"Supplier {sup_count + i}", "e": f"supplier{sup_count + i}@example.com"} for i in range(1, to_add + 1)
            ])

        # Products
        cat_total = conn.execute(text("SELECT COUNT(*) FROM categories")).scalar() or 0
        sup_total = conn.execute(text("SELECT COUNT(*) FROM suppliers")).scalar() or 0
        prod_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
        if prod_count < targets["products"] and cat_total > 0 and sup_total > 0:
            to_add = targets["products"] - prod_count
            batch = []
            for i in range(1, to_add + 1):
                name = f"Product {prod_count + i}"
                sku = f"SKU{prod_count + i:08d}"
                price = round(random.uniform(1.0, 9999.0), 2)
                stock = random.randint(0, 10000)
                batch.append({
                    "cat": random.randint(1, cat_total),
                    "sup": random.randint(1, sup_total),
                    "n": name,
                    "sku": sku,
                    "p": price,
                    "st": stock,
                })
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO products (category_id, supplier_id, name, sku, price, stock) VALUES (:cat,:sup,:n,:sku,:p,:st)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO products (category_id, supplier_id, name, sku, price, stock) VALUES (:cat,:sup,:n,:sku,:p,:st)"), batch)

        # Top-up orders to target
        if count_o < target_orders and cust_total > 0:
            to_add = target_orders - count_o
            print(f"Adding {to_add} orders to reach {target_orders}...")
            statuses = ["pending","paid","processing","shipped","canceled","refunded"]
            batch = []
            start_date = datetime.now() - timedelta(days=365)
            for i in range(1, to_add + 1):
                cust_id = random.randint(1, cust_total)
                amount = round(random.uniform(5.0, 1000.0), 2)
                status = random.choice(statuses)
                # created_at random within last year
                created = start_date + timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))
                batch.append({
                    "c": cust_id,
                    "a": amount,
                    "s": status,
                })
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (:c,:a,:s)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (:c,:a,:s)"), batch)

        # Order items (requires orders & products)
        ord_total = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar() or 0
        prod_total = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
        oi_count = conn.execute(text("SELECT COUNT(*) FROM order_items")).scalar() or 0
        if oi_count < targets["order_items"] and ord_total > 0 and prod_total > 0:
            to_add = targets["order_items"] - oi_count
            print(f"Adding {to_add} order_items to reach {targets['order_items']}...")
            batch = []
            for i in range(1, to_add + 1):
                order_id = random.randint(1, ord_total)
                product_id = random.randint(1, prod_total)
                qty = random.randint(1, 10)
                price = round(random.uniform(1.0, 9999.0), 2)
                batch.append({"o": order_id, "p": product_id, "q": qty, "u": price})
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (:o,:p,:q,:u)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (:o,:p,:q,:u)"), batch)

        # Payments
        pay_count = conn.execute(text("SELECT COUNT(*) FROM payments")).scalar() or 0
        if pay_count < targets["payments"] and ord_total > 0:
            to_add = targets["payments"] - pay_count
            methods = ["card","upi","netbanking","cod"]
            statuses = ["pending","paid","failed","refunded"]
            batch = []
            for i in range(1, to_add + 1):
                order_id = random.randint(1, ord_total)
                amount = round(random.uniform(5.0, 1000.0), 2)
                method = random.choice(methods)
                status = random.choice(statuses)
                batch.append({"o": order_id, "a": amount, "m": method, "s": status})
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO payments (order_id, amount, method, status) VALUES (:o,:a,:m,:s)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO payments (order_id, amount, method, status) VALUES (:o,:a,:m,:s)"), batch)

        # Shipments
        shp_count = conn.execute(text("SELECT COUNT(*) FROM shipments")).scalar() or 0
        if shp_count < targets["shipments"] and ord_total > 0:
            to_add = targets["shipments"] - shp_count
            carriers = ["UPS","FedEx","DHL","Local"]
            statuses = ["label","in_transit","delivered","exception"]
            batch = []
            for i in range(1, to_add + 1):
                order_id = random.randint(1, ord_total)
                carrier = random.choice(carriers)
                tracking = f"TRK{random.randint(10**9, 10**10-1)}"
                status = random.choice(statuses)
                batch.append({"o": order_id, "c": carrier, "t": tracking, "s": status})
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO shipments (order_id, carrier, tracking_number, status) VALUES (:o,:c,:t,:s)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO shipments (order_id, carrier, tracking_number, status) VALUES (:o,:c,:t,:s)"), batch)

        # Reviews
        rev_count = conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar() or 0
        if rev_count < targets["reviews"] and prod_total > 0 and cust_total > 0:
            to_add = targets["reviews"] - rev_count
            batch = []
            for i in range(1, to_add + 1):
                product_id = random.randint(1, prod_total)
                customer_id = random.randint(1, cust_total)
                rating = random.randint(1, 5)
                comment = f"Review {rev_count + i} for product {product_id}"
                batch.append({"p": product_id, "c": customer_id, "r": rating, "cm": comment})
                if len(batch) >= 2000:
                    conn.execute(text("INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES (:p,:c,:r,:cm)"), batch)
                    batch.clear()
            if batch:
                conn.execute(text("INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES (:p,:c,:r,:cm)"), batch)


print("Seeding sample data (idempotent top-up)...")
bulk_seed(engine)
print("Seed completed.")

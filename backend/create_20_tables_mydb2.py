import mysql.connector
from mysql.connector import Error
import random
import string
from datetime import datetime, timedelta

PORT = 3306
DB_NAME = 'mydb2'
ROWS_PER_TABLE = 15

def create_connection(database=None):
    kwargs = dict(host='127.0.0.1', user='root', password='', port=PORT, autocommit=True)
    if database:
        kwargs['database'] = database
    return mysql.connector.connect(**kwargs)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_date():
    return (datetime.now() - timedelta(days=random.randint(0, 3650))).date()

def ensure_database(conn):
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    cur.close()

def create_tables(conn):
    cur = conn.cursor()

    # Table definitions: each table has ~15 columns to satisfy requirement
    ddl = [
        # 1 users
        ("users",
         """
        CREATE TABLE users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(60) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(60),
            last_name VARCHAR(60),
            phone VARCHAR(30),
            birth_date DATE,
            gender VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP NULL,
            profile_text TEXT,
            reputation INT DEFAULT 0
        )"""),

        # 2 roles
        ("roles",
         """
        CREATE TABLE roles (
            role_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            permissions TEXT,
            is_system BOOLEAN DEFAULT FALSE,
            priority INT DEFAULT 0,
            metadata JSON,
            reserved_by VARCHAR(100),
            color VARCHAR(20),
            icon VARCHAR(100),
            legacy_id INT,
            notes TEXT,
            deprecated BOOLEAN DEFAULT FALSE,
            sort_order INT DEFAULT 0
        )"""),

        # 3 permissions
        ("permissions",
         """
        CREATE TABLE permissions (
            permission_id INT AUTO_INCREMENT PRIMARY KEY,
            codename VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(150),
            description TEXT,
            module VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT TRUE,
            level INT DEFAULT 0,
            metadata JSON,
            notes TEXT,
            deprecated BOOLEAN DEFAULT FALSE,
            reserved_by VARCHAR(100),
            scope VARCHAR(100),
            sort_order INT DEFAULT 0
        )"""),

        # 4 user_roles (many-to-many)
        ("user_roles",
         """
        CREATE TABLE user_roles (
            user_id INT NOT NULL,
            role_id INT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_by VARCHAR(100),
            expires_at TIMESTAMP NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            note TEXT,
            INDEX (user_id),
            INDEX (role_id),
            PRIMARY KEY (user_id, role_id)
        )"""),

        # 5 posts
        ("posts",
         """
        CREATE TABLE posts (
            post_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(255),
            slug VARCHAR(255) UNIQUE,
            body TEXT,
            summary VARCHAR(500),
            status ENUM('draft','published','archived') DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            published_at TIMESTAMP NULL,
            view_count INT DEFAULT 0,
            like_count INT DEFAULT 0,
            share_count INT DEFAULT 0,
            language VARCHAR(10),
            featured BOOLEAN DEFAULT FALSE
        )"""),

        # 6 post_meta
        ("post_meta",
         """
        CREATE TABLE post_meta (
            meta_id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            meta_key VARCHAR(200),
            meta_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            namespace VARCHAR(100),
            is_private BOOLEAN DEFAULT FALSE,
            indexed_key VARCHAR(200),
            UNIQUE(post_id, meta_key)
        )"""),

        # 7 comments
        ("comments",
         """
        CREATE TABLE comments (
            comment_id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT,
            user_id INT,
            parent_id INT NULL,
            body TEXT,
            is_spam BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            upvotes INT DEFAULT 0,
            downvotes INT DEFAULT 0,
            status VARCHAR(50),
            ip_address VARCHAR(50),
            user_agent VARCHAR(255),
            sentiment_score DECIMAL(4,3)
        )"""),

        # 8 categories
        ("categories",
         """
        CREATE TABLE categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) UNIQUE NOT NULL,
            slug VARCHAR(150) UNIQUE,
            description TEXT,
            parent_id INT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            weight INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            seo_title VARCHAR(255),
            seo_description VARCHAR(500),
            image_url VARCHAR(500),
            color VARCHAR(20),
            alternate_names TEXT
        )"""),

        # 9 products
        ("products",
         """
        CREATE TABLE products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            sku VARCHAR(100) UNIQUE,
            name VARCHAR(255),
            short_description VARCHAR(500),
            description TEXT,
            category_id INT,
            price DECIMAL(12,2),
            cost DECIMAL(12,2),
            weight DECIMAL(8,2),
            length DECIMAL(8,2),
            width DECIMAL(8,2),
            height DECIMAL(8,2),
            stock_quantity INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""),

        # 10 product_details
        ("product_details",
         """
        CREATE TABLE product_details (
            detail_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            attribute_name VARCHAR(200),
            attribute_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            extra_json JSON,
            source VARCHAR(200),
            language VARCHAR(10),
            is_public BOOLEAN DEFAULT TRUE,
            UNIQUE(product_id, attribute_name)
        )"""),

        # 11 orders
        ("orders",
         """
        CREATE TABLE orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            order_number VARCHAR(100) UNIQUE,
            user_id INT,
            total_amount DECIMAL(12,2),
            tax_amount DECIMAL(12,2),
            shipping_amount DECIMAL(12,2),
            status VARCHAR(50),
            placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shipped_at TIMESTAMP NULL,
            delivered_at TIMESTAMP NULL,
            payment_method VARCHAR(100),
            currency VARCHAR(10),
            note TEXT,
            source VARCHAR(50)
        )"""),

        # 12 order_items
        ("order_items",
         """
        CREATE TABLE order_items (
            order_item_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT DEFAULT 1,
            unit_price DECIMAL(12,2),
            discount DECIMAL(12,2) DEFAULT 0,
            total_price DECIMAL(12,2),
            sku VARCHAR(100),
            product_name VARCHAR(255),
            options TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivered BOOLEAN DEFAULT FALSE,
            tracking_ref VARCHAR(200)
        )"""),

        # 13 suppliers
        ("suppliers",
         """
        CREATE TABLE suppliers (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255),
            contact_name VARCHAR(200),
            contact_email VARCHAR(200),
            phone VARCHAR(50),
            address TEXT,
            city VARCHAR(100),
            state VARCHAR(100),
            postal_code VARCHAR(50),
            country VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating DECIMAL(3,2),
            notes TEXT,
            active BOOLEAN DEFAULT TRUE
        )"""),

        # 14 shipments
        ("shipments",
         """
        CREATE TABLE shipments (
            shipment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            shipped_from VARCHAR(255),
            shipped_to VARCHAR(255),
            carrier VARCHAR(100),
            tracking_number VARCHAR(200),
            status VARCHAR(50),
            shipped_at TIMESTAMP NULL,
            delivered_at TIMESTAMP NULL,
            cost DECIMAL(10,2),
            weight DECIMAL(10,2),
            dimensions VARCHAR(100),
            notes TEXT
        )"""),

        # 15 payments
        ("payments",
         """
        CREATE TABLE payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            amount DECIMAL(12,2),
            provider VARCHAR(100),
            transaction_id VARCHAR(255) UNIQUE,
            status VARCHAR(50),
            paid_at TIMESTAMP NULL,
            refunded_at TIMESTAMP NULL,
            fee DECIMAL(10,2),
            currency VARCHAR(10),
            metadata JSON
        )"""),

        # 16 inventory
        ("inventory",
         """
        CREATE TABLE inventory (
            inventory_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            warehouse_id INT,
            lot_number VARCHAR(200),
            quantity INT DEFAULT 0,
            reserved INT DEFAULT 0,
            damaged INT DEFAULT 0,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            min_threshold INT DEFAULT 0,
            max_threshold INT DEFAULT 0,
            reorder_point INT DEFAULT 0,
            supplier_id INT,
            receipt_date DATE
        )"""),

        # 17 warehouses
        ("warehouses",
         """
        CREATE TABLE warehouses (
            warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200),
            code VARCHAR(50) UNIQUE,
            address TEXT,
            city VARCHAR(100),
            state VARCHAR(100),
            postal_code VARCHAR(50),
            country VARCHAR(100),
            capacity INT,
            manager VARCHAR(200),
            phone VARCHAR(50),
            email VARCHAR(200),
            active BOOLEAN DEFAULT TRUE
        )"""),

        # 18 tags
        ("tags",
         """
        CREATE TABLE tags (
            tag_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200) UNIQUE,
            slug VARCHAR(200) UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INT DEFAULT 0,
            metadata JSON,
            color VARCHAR(20)
        )"""),

        # 19 post_tags (many-to-many)
        ("post_tags",
         """
        CREATE TABLE post_tags (
            post_id INT NOT NULL,
            tag_id INT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (post_id, tag_id)
        )"""),

        # 20 comment_meta
        ("comment_meta",
         """
        CREATE TABLE comment_meta (
            meta_id INT AUTO_INCREMENT PRIMARY KEY,
            comment_id INT NOT NULL,
            meta_key VARCHAR(200),
            meta_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(comment_id, meta_key)
        )"""),
    ]

    for name, sql in ddl:
        cur.execute(sql)
        print(f"✅ Created table '{name}'")

    cur.close()

def seed_data(conn):
    cur = conn.cursor()

    # Insert users
    for i in range(ROWS_PER_TABLE):
        cur.execute("INSERT INTO users (username,email,password_hash,first_name,last_name,phone,birth_date,gender,profile_text,reputation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (f'user{i+1}', f'user{i+1}@example.com', 'passhash', f'First{i+1}', f'Last{i+1}', f'+91{random.randint(7000000000,7999999999)}', random_date(), random.choice(['male','female','other']), f'Profile of user {i+1}', random.randint(0,1000)))

    # Insert roles
    roles = ['admin','editor','author','subscriber','moderator']
    for r in roles:
        cur.execute("INSERT INTO roles (name,description,permissions,priority) VALUES (%s,%s,%s,%s)", (r, f'{r} role', '[]', roles.index(r)))

    # Insert permissions
    perms = ['view_post','edit_post','delete_post','create_post','manage_users']
    for p in perms:
        cur.execute("INSERT INTO permissions (codename,name,description,module) VALUES (%s,%s,%s,%s)", (p, p.replace('_',' ').title(), f'Allows {p}', 'core'))

    # Get sample users and roles
    cur.execute("SELECT user_id FROM users LIMIT 5")
    users_sample = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT role_id FROM roles")
    roles_all = [r[0] for r in cur.fetchall()]
    
    # Assign roles to users
    for u in users_sample:
        for rid in roles_all[:2]:
            cur.execute("INSERT INTO user_roles (user_id, role_id, assigned_by) VALUES (%s,%s,%s)", (u, rid, 'system'))

    # Insert posts
    for i in range(ROWS_PER_TABLE):
        cur.execute("INSERT INTO posts (user_id,title,slug,body,summary,status,language,featured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (random.choice(users_sample), f'Sample Post {i+1}', f'sample-post-{i+1}', f'Body for post {i+1}', f'Summary for post {i+1}', random.choice(['draft','published']), 'en', random.choice([0,1])))

    # Get posts
    cur.execute("SELECT post_id FROM posts LIMIT %s", (ROWS_PER_TABLE,))
    posts_sample = [r[0] for r in cur.fetchall()]

    # Insert post_meta
    for pid in posts_sample:
        cur.execute("INSERT INTO post_meta (post_id, meta_key, meta_value, namespace) VALUES (%s,%s,%s,%s)", (pid, 'views_est', str(random.randint(0,1000)), 'sys'))

    # Insert comments
    for pid in posts_sample:
        cur.execute("INSERT INTO comments (post_id,user_id,body,ip_address,user_agent,sentiment_score) VALUES (%s,%s,%s,%s,%s,%s)",
                    (pid, random.choice(users_sample), f'Comment on post {pid}', f'192.168.0.{random.randint(1,254)}', 'pytest-agent', round(random.uniform(-1,1),3)))
    
    # Get comments and insert comment_meta
    cur.execute("SELECT comment_id FROM comments LIMIT %s", (ROWS_PER_TABLE,))
    comments_sample = [r[0] for r in cur.fetchall()]
    for cid in comments_sample:
        cur.execute("INSERT INTO comment_meta (comment_id, meta_key, meta_value) VALUES (%s,%s,%s)", (cid, 'mood', random.choice(['happy','neutral','angry'])))

    # Insert categories
    for i in range(10):
        cur.execute("INSERT INTO categories (name,slug,description,weight) VALUES (%s,%s,%s,%s)", (f'Category {i+1}', f'cat-{i+1}', f'Description {i+1}', i))
    cur.execute("SELECT category_id FROM categories")
    cats = [r[0] for r in cur.fetchall()]

    # Insert products and product_details
    for i in range(ROWS_PER_TABLE):
        cur.execute("INSERT INTO products (sku,name,short_description,description,category_id,price,cost,weight,length,width,height,stock_quantity,is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (f'SKU{i+1}', f'Product {i+1}', f'Short {i+1}', f'Desc {i+1}', random.choice(cats), round(random.uniform(10,1000),2), round(random.uniform(5,500),2), round(random.uniform(0.1,10),2), round(random.uniform(1,50),2), round(random.uniform(1,50),2), round(random.uniform(1,50),2), random.randint(0,1000), 1))
    cur.execute("SELECT product_id FROM products LIMIT %s", (ROWS_PER_TABLE,))
    products_sample = [r[0] for r in cur.fetchall()]
    for pid in products_sample:
        cur.execute("INSERT INTO product_details (product_id, attribute_name, attribute_value, source) VALUES (%s,%s,%s,%s)", (pid, 'color', random.choice(['red','blue','green']), 'import'))

    # Insert suppliers
    for i in range(5):
        cur.execute("INSERT INTO suppliers (company_name,contact_name,contact_email,phone,city,country,rating) VALUES (%s,%s,%s,%s,%s,%s,%s)", (f'Supplier {i+1}', f'Contact {i+1}', f'supplier{i+1}@ex.com', f'+91{random.randint(6000000000,6999999999)}', 'City', 'Country', round(random.uniform(1,5),2)))
    cur.execute("SELECT supplier_id FROM suppliers")
    suppliers_sample = [r[0] for r in cur.fetchall()]

    # Insert warehouses
    for i in range(3):
        cur.execute("INSERT INTO warehouses (name,code,address,city,country,capacity,manager,email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (f'WH {i+1}', f'WH{i+1}', 'Addr', 'City', 'Country', 10000*(i+1), f'Mgr{i+1}', f'wh{i+1}@ex.com'))
    cur.execute("SELECT warehouse_id FROM warehouses")
    wh_sample = [r[0] for r in cur.fetchall()]

    # Insert inventory
    for pid in products_sample[:10]:
        cur.execute("INSERT INTO inventory (product_id, warehouse_id, lot_number, quantity, reserved, damaged, supplier_id, receipt_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (pid, random.choice(wh_sample), f'LOT{random.randint(1000,9999)}', random.randint(0,500), 0, 0, random.choice(suppliers_sample), random_date()))

    # Insert orders, order_items, payments, shipments
    for i in range(ROWS_PER_TABLE):
        cur.execute("INSERT INTO orders (order_number,user_id,total_amount,tax_amount,shipping_amount,status,payment_method,currency,source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (f'ORD-{1000+i}', random.choice(users_sample), round(random.uniform(50,2000),2), 0, 0, random.choice(['pending','processing','shipped']), 'card', 'USD', 'web'))
    cur.execute("SELECT order_id FROM orders LIMIT %s", (ROWS_PER_TABLE,))
    orders_sample = [r[0] for r in cur.fetchall()]
    for oid in orders_sample:
        prod = random.choice(products_sample)
        cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price, product_name) VALUES (%s,%s,%s,%s,%s,%s)", (oid, prod, 1, 99.99, 99.99, f'Product {prod}'))
        cur.execute("INSERT INTO payments (order_id, amount, provider, transaction_id, status) VALUES (%s,%s,%s,%s,%s)", (oid, 99.99, 'stripe', f'tx-{random.randint(100000,999999)}', 'completed'))
        cur.execute("INSERT INTO shipments (order_id, carrier, tracking_number, status) VALUES (%s,%s,%s,%s)", (oid, 'DHL', f'TRK{random.randint(1000,9999)}', 'shipped'))

    # Insert tags and post_tags
    for i in range(10):
        cur.execute("INSERT INTO tags (name,slug,description,color) VALUES (%s,%s,%s,%s)", (f'Tag {i+1}', f'tag-{i+1}', f'Desc {i+1}', random.choice(['red','blue','green'])))
    cur.execute("SELECT tag_id FROM tags")
    tags_sample = [r[0] for r in cur.fetchall()]
    for pid in posts_sample[:10]:
        for t in tags_sample[:3]:
            cur.execute("INSERT IGNORE INTO post_tags (post_id, tag_id) VALUES (%s,%s)", (pid, t))

    conn.commit()
    cur.close()

def verify(conn):
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [r[0] for r in cur.fetchall()]
    print('\n📋 Tables and row counts:')
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f'  {t:<20} : {cnt} rows')
    cur.close()

def main():
    print('🚀 Creating database and 20 related tables in mydb2...')
    conn = create_connection()
    try:
        ensure_database(conn)
        conn.close()
        conn = create_connection(database=DB_NAME)
        create_tables(conn)
        seed_data(conn)
        verify(conn)
        print('\n✅ Done: mydb2 populated with sample data')
    except Error as e:
        print('❌ MySQL error:', e)
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    main()

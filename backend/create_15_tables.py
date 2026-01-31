import mysql.connector
from mysql.connector import Error
import random
import string
from datetime import datetime, timedelta

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3307,
            autocommit=True
        )
        print("✅ Connected to MySQL server")
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date():
    return (datetime.now() - timedelta(days=random.randint(0, 5*365))).strftime('%Y-%m-%d')

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS ecommerce_db")
        cursor.execute("CREATE DATABASE ecommerce_db")
        cursor.execute("USE ecommerce_db")
        print("✅ Created database 'ecommerce_db'")
        cursor.close()
        return True
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables(connection):
    try:
        cursor = connection.cursor()
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            is_active BOOLEAN DEFAULT TRUE
        )""")
        print("✅ Created table 'users'")
        
        # 2. User Addresses
        cursor.execute("""
        CREATE TABLE user_addresses (
            address_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            address_type ENUM('home', 'work', 'other') NOT NULL,
            street_address1 VARCHAR(100) NOT NULL,
            street_address2 VARCHAR(100),
            city VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            postal_code VARCHAR(20) NOT NULL,
            country VARCHAR(50) NOT NULL,
            is_default BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'user_addresses'")
        
        # 3. User Payment Methods
        cursor.execute("""
        CREATE TABLE user_payment_methods (
            payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            payment_type ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer') NOT NULL,
            provider VARCHAR(50),
            account_number_masked VARCHAR(50),
            expiry_date DATE,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'user_payment_methods'")
        
        # 4. Categories
        cursor.execute("""
        CREATE TABLE categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT,
            parent_id INT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (parent_id) REFERENCES categories(category_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'categories'")
        
        # 5. Products
        cursor.execute("""
        CREATE TABLE products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            category_id INT,
            price DECIMAL(10, 2) NOT NULL,
            compare_at_price DECIMAL(10, 2),
            sku VARCHAR(50) UNIQUE,
            barcode VARCHAR(50),
            quantity INT NOT NULL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'products'")
        
        # 6. Product Variants
        cursor.execute("""
        CREATE TABLE product_variants (
            variant_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            sku VARCHAR(50) UNIQUE,
            option1_name VARCHAR(50),
            option1_value VARCHAR(50),
            option2_name VARCHAR(50),
            option2_value VARCHAR(50),
            price_adjustment DECIMAL(10, 2) DEFAULT 0.00,
            quantity INT NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_variants'")
        
        # 7. Product Attributes
        cursor.execute("""
        CREATE TABLE product_attributes (
            attribute_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_attributes'")
        
        # 8. Product Images
        cursor.execute("""
        CREATE TABLE product_images (
            image_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            image_url VARCHAR(255) NOT NULL,
            alt_text VARCHAR(100),
            is_primary BOOLEAN DEFAULT FALSE,
            sort_order INT DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_images'")
        
        # 9. Product Reviews
        cursor.execute("""
        CREATE TABLE product_reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            user_id INT NOT NULL,
            rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            title VARCHAR(100),
            comment TEXT,
            is_approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_reviews'")
        
        # 10. Orders
        cursor.execute("""
        CREATE TABLE orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            order_number VARCHAR(20) UNIQUE NOT NULL,
            user_id INT,
            status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
            subtotal DECIMAL(10, 2) NOT NULL,
            tax_amount DECIMAL(10, 2) NOT NULL,
            shipping_amount DECIMAL(10, 2) NOT NULL,
            discount_amount DECIMAL(10, 2) DEFAULT 0.00,
            total_amount DECIMAL(10, 2) NOT NULL,
            shipping_address_id INT,
            billing_address_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (shipping_address_id) REFERENCES user_addresses(address_id) ON DELETE SET NULL,
            FOREIGN KEY (billing_address_id) REFERENCES user_addresses(address_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'orders'")
        
        # 11. Order Items
        cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            product_id INT,
            variant_id INT,
            product_name VARCHAR(100) NOT NULL,
            variant_description VARCHAR(255),
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL,
            FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'order_items'")
        
        # 12. Order Status History
        cursor.execute("""
        CREATE TABLE order_status_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'order_status_history'")
        
        # 13. Payments
        cursor.execute("""
        CREATE TABLE payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            transaction_id VARCHAR(100) UNIQUE,
            status ENUM('pending', 'authorized', 'captured', 'refunded', 'failed') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'payments'")
        
        # 14. Shipments
        cursor.execute("""
        CREATE TABLE shipments (
            shipment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            tracking_number VARCHAR(100),
            carrier VARCHAR(50),
            status ENUM('pending', 'in_transit', 'delivered', 'exception') DEFAULT 'pending',
            shipped_at TIMESTAMP NULL,
            delivered_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'shipments'")
        
        # 15. Inventory
        cursor.execute("""
        CREATE TABLE inventory (
            inventory_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            variant_id INT,
            quantity INT NOT NULL DEFAULT 0,
            low_stock_threshold INT DEFAULT 10,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'inventory'")
        
        # 16. Coupons
        cursor.execute("""
        CREATE TABLE coupons (
            coupon_id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            discount_type ENUM('percentage', 'fixed_amount') NOT NULL,
            discount_value DECIMAL(10, 2) NOT NULL,
            minimum_order_amount DECIMAL(10, 2) DEFAULT 0.00,
            max_uses INT,
            used_count INT DEFAULT 0,
            start_date DATETIME,
            end_date DATETIME,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("✅ Created table 'coupons'")
        
        # 17. Wishlists
        cursor.execute("""
        CREATE TABLE wishlists (
            wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(100) DEFAULT 'My Wishlist',
            is_public BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'wishlists'")
        
        # 18. Wishlist Items
        cursor.execute("""
        CREATE TABLE wishlist_items (
            wishlist_item_id INT AUTO_INCREMENT PRIMARY KEY,
            wishlist_id INT NOT NULL,
            product_id INT NOT NULL,
            variant_id INT,
            quantity INT DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'wishlist_items'")
        
        # 19. Carts
        cursor.execute("""
        CREATE TABLE carts (
            cart_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            session_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'carts'")
        
        # 20. Cart Items
        cursor.execute("""
        CREATE TABLE cart_items (
            cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
            cart_id INT NOT NULL,
            product_id INT,
            variant_id INT,
            quantity INT NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'cart_items'")
        
        print("\n✅ All 20 tables created successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        if cursor:
            cursor.close()

def insert_sample_data(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Insert sample categories
        categories = [
            ('Electronics', 'Electronic devices and accessories', None),
            ('Clothing', 'Apparel and fashion items', None),
            ('Home & Garden', 'Home decor and garden supplies', None),
            ('Books', 'Books and publications', None),
            ('Toys & Games', 'Toys and games for all ages', None)
        ]
        
        cursor.executemany(
            "INSERT INTO categories (name, description, parent_id) VALUES (%s, %s, %s)",
            categories
        )
        
        # Insert sample users
        users = [
            ('john_doe', 'john@example.com', 'hashed_password_123', 'John', 'Doe', '+1234567890'),
            ('jane_smith', 'jane@example.com', 'hashed_password_123', 'Jane', 'Smith', '+1987654321'),
            ('admin', 'admin@example.com', 'admin_hashed_pass', 'Admin', 'User', '+1122334455')
        ]
        
        cursor.executemany(
            """
            INSERT INTO users 
            (username, email, password_hash, first_name, last_name, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            users
        )
        
        print("✅ Inserted sample data successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error inserting sample data: {e}")
        return False
    finally:
        if cursor:
            cursor.close()

def main():
    print("🚀 Starting database setup...")
    
    connection = create_connection()
    if not connection:
        return
    
    try:
        # Create database
        if not create_database(connection):
            return
            
        # Create all tables
        if not create_tables(connection):
            return
            
        # Insert sample data
        if not insert_sample_data(connection):
            return
        
        print("\n✨ Database setup completed successfully!")
        print("✅ 20+ related tables created with sample data")
        print("\nYou can now use the e-commerce database with all the required tables!")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()

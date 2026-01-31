import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3307,
            database='talkwithdata',
            autocommit=True
        )
        print("✅ Connected to MySQL server and selected 'talkwithdata' database")
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def create_tables(connection):
    try:
        cursor = connection.cursor()
        
        # 1. Categories Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("✅ Created table 'categories'")
        
        # 2. Products Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'products'")
        
        # 3. Customers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("✅ Created table 'customers'")
        
        # 4. Orders Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10, 2) NOT NULL,
            status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'orders'")
        
        # 5. Order_Items Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'order_items'")
        
        # 6. Payments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            amount DECIMAL(10, 2) NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method VARCHAR(50) NOT NULL,
            status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'payments'")
        
        # 7. Shippings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shippings (
            shipping_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            address TEXT NOT NULL,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100),
            postal_code VARCHAR(20),
            country VARCHAR(100) NOT NULL,
            status ENUM('pending', 'shipped', 'in_transit', 'delivered') DEFAULT 'pending',
            tracking_number VARCHAR(100),
            shipping_date TIMESTAMP NULL,
            delivery_date TIMESTAMP NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'shippings'")
        
        # 8. Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            customer_id INT,
            rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'reviews'")
        
        # 9. Suppliers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            contact_name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            city VARCHAR(100),
            country VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("✅ Created table 'suppliers'")
        
        # 10. Product_Suppliers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_suppliers (
            product_id INT,
            supplier_id INT,
            unit_price DECIMAL(10, 2) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (product_id, supplier_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_suppliers'")
        
        # 11. Discounts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            discount_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            discount_percent DECIMAL(5, 2) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("✅ Created table 'discounts'")
        
        # 12. Product_Discounts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_discounts (
            product_id INT,
            discount_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (product_id, discount_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (discount_id) REFERENCES discounts(discount_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'product_discounts'")
        
        # 13. Inventory_Transactions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            quantity_change INT NOT NULL,
            transaction_type ENUM('purchase', 'sale', 'return', 'adjustment') NOT NULL,
            reference_id INT,
            notes TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
        )""")
        print("✅ Created table 'inventory_transactions'")
        
        # 14. Wishlists Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            name VARCHAR(100) DEFAULT 'My Wishlist',
            is_public BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'wishlists'")
        
        # 15. Wishlist_Items Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist_items (
            wishlist_item_id INT AUTO_INCREMENT PRIMARY KEY,
            wishlist_id INT,
            product_id INT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'wishlist_items'")
        
        # 16. User_Addresses Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_addresses (
            address_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            address_type ENUM('home', 'work', 'billing', 'shipping', 'other') NOT NULL,
            address_line1 VARCHAR(255) NOT NULL,
            address_line2 VARCHAR(255),
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100),
            postal_code VARCHAR(20),
            country VARCHAR(100) NOT NULL,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )""")
        print("✅ Created table 'user_addresses'")
        
        print("\n✅ All tables created successfully in 'talkwithdata' database!")
        return True
        
    except Error as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        if cursor:
            cursor.close()

def main():
    print("🚀 Starting to add tables to 'talkwithdata' database...")
    
    connection = create_connection()
    if not connection:
        print("❌ Could not connect to the database. Please check your MySQL server and connection settings.")
        return
    
    try:
        if create_tables(connection):
            print("\n✨ Database setup completed successfully!")
            print("✅ 16+ related tables have been added to 'talkwithdata' database")
        else:
            print("\n❌ There were errors while creating the tables.")
            
    except Error as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()

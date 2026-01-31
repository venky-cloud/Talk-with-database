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
        print("✅ Connected to 'talkwithdata' database")
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def add_tables(connection):
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
        
        # 3. Order_Items Table
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
        
        # 4. Payments Table
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
        
        # 5. Shippings Table
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
        
        # 6. Reviews Table
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
        
        print("\n✅ All tables created successfully in 'talkwithdata' database!")
        return True
        
    except Error as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        if cursor:
            cursor.close()

def main():
    print("🚀 Starting to add more tables to 'talkwithdata' database...")
    
    connection = create_connection()
    if not connection:
        print("❌ Could not connect to the database. Please check your MySQL server and connection settings.")
        return
    
    try:
        if add_tables(connection):
            print("\n✨ Database update completed successfully!")
            print("✅ 6 new tables have been added to 'talkwithdata' database")
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

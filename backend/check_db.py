import mysql.connector
from mysql.connector import Error

def check_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3307
        )
        
        cursor = connection.cursor()
        
        # Check if ecommerce_db exists
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("\n📚 Available Databases:")
        for db in databases:
            print(f"- {db[0]}")
        
        # Check tables in ecommerce_db if it exists
        cursor.execute("""
        SELECT SCHEMA_NAME 
        FROM INFORMATION_SCHEMA.SCHEMATA 
        WHERE SCHEMA_NAME = 'ecommerce_db'
        """)
        
        if cursor.fetchone():
            print("\n✅ ecommerce_db exists!")
            
            # Switch to ecommerce_db
            cursor.execute("USE ecommerce_db")
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("\n📋 Tables in ecommerce_db:")
                for table in tables:
                    print(f"- {table[0]}")
            else:
                print("\n❌ No tables found in ecommerce_db")
        else:
            print("\n❌ ecommerce_db does not exist")
        
    except Error as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Connection closed")

if __name__ == "__main__":
    print("🔍 Checking database status...")
    check_database()

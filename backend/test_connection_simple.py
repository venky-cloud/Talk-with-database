import mysql.connector

def test_connection():
    try:
        # Try to connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3307
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server!")
            
            # Get server info
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL Server version: {version[0]}")
            
            # List databases
            cursor.execute("SHOW DATABASES")
            print("\n📚 Available databases:")
            for db in cursor:
                print(f"- {db[0]}")
            
            cursor.close()
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure MySQL is running in XAMPP")
        print("2. Check the port in XAMPP > MySQL > Config > my.ini")
        print("3. Try using '127.0.0.1' instead of 'localhost'")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Connection closed")

if __name__ == "__main__":
    print("🔍 Testing MySQL connection...")
    test_connection()

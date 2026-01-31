import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        # Try to connect to MySQL server
        print("🔍 Attempting to connect to MySQL server...")
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            port=3307,
            connection_timeout=5
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
            
            # Check if talkwithdata exists
            cursor.execute("SHOW DATABASES LIKE 'talkwithdata'")
            if cursor.fetchone():
                print("\n✅ Database 'talkwithdata' exists")
                cursor.execute("USE talkwithdata")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                if tables:
                    print("\n📋 Tables in 'talkwithdata':")
                    for table in tables:
                        print(f"- {table[0]}")
                else:
                    print("\nℹ️ No tables found in 'talkwithdata'")
            else:
                print("\n❌ Database 'talkwithdata' does not exist")
            
            cursor.close()
            return True
            
    except Error as e:
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
    test_connection()

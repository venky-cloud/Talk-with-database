import mysql.connector
from mysql.connector import Error

def test_connection():
    print("🔍 Testing MySQL connection...")
    
    try:
        # Try to connect to MySQL server with different configurations
        connection_params = [
            {'host': '127.0.0.1', 'port': 3306},  # Try with IP and default port
            {'host': '127.0.0.1', 'port': 3307},  # Try with IP and port 3307
            {'host': 'localhost', 'port': 3306},  # Try with localhost and default port
            {'host': 'localhost', 'port': 3307}   # Try with localhost and port 3307
        ]
        
        connection = None
        
        for params in connection_params:
            try:
                print(f"\n🔧 Trying to connect to {params['host']}:{params['port']}...")
                connection = mysql.connector.connect(
                    host=params['host'],
                    user='root',
                    password='',
                    port=params['port']
                )
                print(f"✅ Successfully connected to {params['host']}:{params['port']}")
                break
            except Error as e:
                print(f"❌ Failed to connect to {params['host']}:{params['port']} - {e.msg}")
                continue
                
        if not connection:
            print("\n❌ Could not connect to MySQL server with any configuration")
            return False
        
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
            
    except Error as e:
        print(f"\n❌ Error details:")
        print(f"Error code: {e.errno}")
        print(f"SQL State: {e.sqlstate}")
        print(f"Message: {e.msg}")
        
        if e.errno == 2003:
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure MySQL service is running in XAMPP")
            print("2. Verify the MySQL port in XAMPP (usually 3306 or 3307)")
            print("3. Check if your firewall is blocking the connection")
            print("4. Try using '127.0.0.1' instead of 'localhost'")
        
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Connection closed")

if __name__ == "__main__":
    test_connection()

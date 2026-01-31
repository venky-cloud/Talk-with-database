import mysql.connector
from mysql.connector import Error

def test_ports():
    ports_to_test = [3306, 3307, 3308, 3309, 3310]
    
    for port in ports_to_test:
        try:
            print(f"\n🔧 Trying to connect to port {port}...")
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                port=port,
                connection_timeout=2  # Shorter timeout for faster testing
            )
            
            if connection.is_connected():
                print(f"✅ Successfully connected to MySQL on port {port}")
                
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
                connection.close()
                return port
                
        except Error as e:
            print(f"❌ Failed to connect to port {port}: {e.msg}")
            continue
    
    print("\n❌ Could not connect to MySQL on any of the tested ports")
    print("\n🔧 Troubleshooting steps:")
    print("1. Open XAMPP Control Panel")
    print("2. Check if MySQL is running (should be green)")
    print("3. Click 'Config' next to MySQL and check the port in my.ini")
    print("4. Try restarting the MySQL service")
    
    return None

if __name__ == "__main__":
    print("🔍 Testing MySQL connection on different ports...")
    test_ports()

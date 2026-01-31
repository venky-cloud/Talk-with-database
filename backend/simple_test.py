import mysql.connector

print("🔍 Testing MySQL connection...")

try:
    # Try to connect with different configurations
    configs = [
        {'host': '127.0.0.1', 'port': 3306},
        {'host': '127.0.0.1', 'port': 3307},
        {'host': 'localhost', 'port': 3306},
        {'host': 'localhost', 'port': 3307},
        {'host': 'localhost', 'port': 3308},
        {'host': '127.0.0.1', 'port': 3308}
    ]
    
    connected = False
    
    for config in configs:
        try:
            print(f"\nTrying {config['host']}:{config['port']}...")
            connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user='root',
                password='',
                connection_timeout=3  # Shorter timeout for faster testing
            )
            
            if connection.is_connected():
                print(f"✅ Successfully connected to {config['host']}:{config['port']}")
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES;")
                print("\n📚 Databases:")
                for db in cursor:
                    print(f"- {db[0]}")
                cursor.close()
                connected = True
                break
                
        except Exception as e:
            print(f"❌ Failed to connect: {str(e)[:100]}")
            continue
    
    if not connected:
        print("\n❌ Could not connect to MySQL server with any configuration")
        print("\n🔧 Troubleshooting steps:")
        print("1. Open XAMPP Control Panel")
        print("2. Check if MySQL is running (should be green)")
        print("3. If not running, click 'Start' next to MySQL")
        print("4. Check the port in XAMPP > MySQL > Config > my.ini")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("\n🔌 Connection closed")

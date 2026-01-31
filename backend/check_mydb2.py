import mysql.connector
from mysql.connector import Error

def check_database():
    try:
        # Try to connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3307
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server")
            
            cursor = connection.cursor()
            
            # Check if talkwithdata exists
            cursor.execute("SHOW DATABASES LIKE 'talkwithdata'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Database 'talkwithdata' exists")
                
                # Check tables in talkwithdata
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
                print("❌ Database 'talkwithdata' does not exist")
                
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure MySQL server is running in XAMPP")
        print("2. Check if the port (3307) is correct")
        print("3. Verify your MySQL username and password")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Connection closed")

if __name__ == "__main__":
    print("🔍 Checking 'talkwithdata' database status...")
    check_database()

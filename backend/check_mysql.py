import subprocess
import os

def check_mysql_status():
    print("🔍 Checking MySQL status...")
    
    # Check if XAMPP is running
    try:
        # Try to find XAMPP control panel
        xampp_path = r"C:\xampp\xampp-control.exe"
        if os.path.exists(xampp_path):
            print(f"✅ Found XAMPP at: {xampp_path}")
            
            # Check if MySQL is running
            try:
                # This command checks if mysqld.exe is running
                output = subprocess.check_output('tasklist /FI "IMAGENAME eq mysqld.exe"', shell=True)
                if "mysqld.exe" in str(output):
                    print("✅ MySQL service is running")
                    
                    # Try to get the port from my.ini
                    my_ini_path = r"C:\xampp\mysql\bin\my.ini"
                    if os.path.exists(my_ini_path):
                        print(f"✅ Found MySQL configuration at: {my_ini_path}")
                        
                        # Read the port from my.ini
                        with open(my_ini_path, 'r') as f:
                            for line in f:
                                if 'port' in line.lower() and '=' in line:
                                    port = line.split('=')[1].strip()
                                    print(f"ℹ️ MySQL port from my.ini: {port}")
                                    return port
                    else:
                        print("❌ Could not find my.ini. Using default port 3306")
                        return "3306"
                else:
                    print("❌ MySQL service is not running")
                    print("\n🔧 Please start MySQL from XAMPP Control Panel")
                    return None
                    
            except subprocess.CalledProcessError:
                print("❌ MySQL service is not running")
                print("\n🔧 Please start MySQL from XAMPP Control Panel")
                return None
                
        else:
            print("❌ XAMPP not found at the default location")
            print("\n🔧 Please make sure XAMPP is installed at C:\\xampp")
            return None
            
    except Exception as e:
        print(f"❌ Error checking MySQL status: {e}")
        return None

def main():
    port = check_mysql_status()
    
    if port:
        print("\n🔧 Try connecting with the following details:")
        print(f"Host: localhost")
        print(f"Port: {port}")
        print(f"User: root")
        print("Password: (empty)")
        
        # Test the connection
        try:
            import mysql.connector
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                port=int(port)
            )
            print("\n✅ Successfully connected to MySQL!")
            
            # List databases
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            print("\n📚 Available databases:")
            for db in cursor:
                print(f"- {db[0]}")
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"\n❌ Failed to connect to MySQL: {e}")
            
    print("\n🔍 Troubleshooting steps:")
    print("1. Open XAMPP Control Panel")
    print("2. Make sure MySQL is running (green status)")
    print("3. Check the port in XAMPP > MySQL > Config > my.ini")
    print("4. Try restarting the MySQL service")

if __name__ == "__main__":
    main()

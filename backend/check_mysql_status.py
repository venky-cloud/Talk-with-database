"""
Quick script to check if MySQL is running and accessible
"""
import socket
import sys

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False

def main():
    print("=" * 60)
    print("MySQL Connection Status Check")
    print("=" * 60)
    
    # Check common MySQL ports
    ports_to_check = [3306, 3307]
    host = "127.0.0.1"
    
    mysql_running = False
    active_port = None
    
    for port in ports_to_check:
        print(f"\nChecking port {port}...")
        if check_port(host, port):
            print(f"  [OK] Port {port} is OPEN - MySQL might be running")
            mysql_running = True
            active_port = port
        else:
            print(f"  [FAIL] Port {port} is CLOSED - MySQL not listening")
    
    print("\n" + "=" * 60)
    
    if mysql_running:
        print(f"[SUCCESS] MySQL appears to be running on port {active_port}")
        print(f"\nYour .env file should use: mysql+pymysql://root@127.0.0.1:{active_port}/talkwithdata")
    else:
        print("[ERROR] MySQL is NOT running!")
        print("\nTo fix this:")
        print("1. Open XAMPP Control Panel")
        print("2. Click 'Start' button next to MySQL")
        print("3. Wait until MySQL shows 'Running' status")
        print("4. Run this script again to verify")
        sys.exit(1)
    
    # Try to test actual connection
    print("\n" + "=" * 60)
    print("Testing database connection...")
    try:
        from fastapi_app.core.config import settings
        from sqlalchemy import create_engine, text
        
        if not settings.DB_URI:
            print("[ERROR] DB_URI is not set in .env file")
            sys.exit(1)
        
        print(f"DB_URI: {settings.DB_URI}")
        engine = create_engine(settings.DB_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE(), VERSION()"))
            db_name, version = result.fetchone()
            print(f"[SUCCESS] Connected to database: {db_name}")
            print(f"MySQL Version: {version}")
            
            # Check if database has tables
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            if tables:
                print(f"\nFound {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n[WARNING] Database exists but has no tables")
                
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print("\nPossible issues:")
        print("1. Database 'talkwithdata' doesn't exist - create it in phpMyAdmin")
        print("2. Wrong port in .env file")
        print("3. Wrong username/password")
        sys.exit(1)

if __name__ == "__main__":
    main()

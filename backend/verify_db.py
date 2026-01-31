import mysql.connector
from mysql.connector import Error

def check_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            port=3307,
            database='talk_db'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # List all tables in the database
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("✅ Database connection successful!")
            print("\n📋 Tables in talk_db:")
            for table in tables:
                print(f"- {table['Tables_in_talk_db']}")
            
            # Show sample data from users table
            print("\n👥 Sample Users:")
            cursor.execute("SELECT user_id, username, email, role FROM users")
            users = cursor.fetchall()
            for user in users:
                print(f"ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
            
            # Show sample appointments
            print("\n📅 Sample Appointments:")
            cursor.execute("""
                SELECT a.appointment_id, u1.username as patient, u2.username as doctor, 
                       a.appointment_date, a.status
                FROM appointments a
                JOIN users u1 ON a.patient_id = u1.user_id
                JOIN users u2 ON a.doctor_id = u2.user_id
            """)
            appointments = cursor.fetchall()
            for appt in appointments:
                print(f"Appt #{appt['appointment_id']}: {appt['patient']} with Dr. {appt['doctor']} on {appt['appointment_date']} - {appt['status']}")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🔍 Verifying database setup...")
    check_database()

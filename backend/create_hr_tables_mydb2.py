import mysql.connector
from mysql.connector import Error

PORT = 3307  # XAMPP MySQL port
DB_NAME = 'talkwithdata'

DDL_STATEMENTS = [
    # departments
    '''CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        location VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    # employees
    '''CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(120) NOT NULL,
        department_id INT,
        salary DECIMAL(12,2) DEFAULT 0,
        joining_date DATE,
        email VARCHAR(150) UNIQUE,
        FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
    )''',
    # projects
    '''CREATE TABLE IF NOT EXISTS projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        employee_id INT,
        start_date DATE,
        end_date DATE NULL,
        status ENUM('planned','active','completed','on_hold') DEFAULT 'active',
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
    )'''
]

SEED_SQL = [
    ("INSERT IGNORE INTO departments (id,name,location) VALUES "+
     "(1,'Engineering','Bengaluru'),(2,'Sales','Mumbai'),(3,'HR','Chennai')", ()),
    ("INSERT IGNORE INTO employees (id,name,department_id,salary,joining_date,email) VALUES "+
     "(1,'Anita Rao',1,1200000,'2022-04-01','anita.rao@example.com'),"+
     "(2,'Vikram Singh',1,1600000,'2021-09-15','vikram.singh@example.com'),"+
     "(3,'Neha Sharma',2,900000,'2023-01-10','neha.sharma@example.com'),"+
     "(4,'Rahul Verma',3,750000,'2020-06-20','rahul.verma@example.com')", ()),
    ("INSERT IGNORE INTO projects (id,name,employee_id,start_date,end_date,status) VALUES "+
     "(1,'Website Revamp',1,'2023-07-01',NULL,'active'),"+
     "(2,'Mobile App',2,'2023-08-10',NULL,'active'),"+
     "(3,'CRM Migration',3,'2024-01-05',NULL,'active'),"+
     "(4,'Recruitment Drive',4,'2024-02-01','2024-06-30','completed'),"+
     "(5,'Data Platform',2,'2024-03-01',NULL,'active')", ())
]

def connect_server():
    return mysql.connector.connect(host='127.0.0.1', user='root', password='', port=PORT, autocommit=True)

def ensure_db():
    conn = connect_server()
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    return conn, cur

def create_tables(cur):
    for sql in DDL_STATEMENTS:
        cur.execute(sql)


def seed_data(cur):
    for sql, params in SEED_SQL:
        cur.execute(sql, params)


def verify(cur):
    cur.execute("SHOW TABLES")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)
    cur.execute("SELECT COUNT(*) FROM departments")
    print("departments:", cur.fetchone()[0])

if __name__ == '__main__':
    try:
        conn, cur = ensure_db()
        create_tables(cur)
        seed_data(cur)
        verify(cur)
        print("✅ HR tables ready in talkwithdata. Try: SELECT * FROM departments; SELECT e.name, COUNT(p.id) FROM employees e JOIN projects p ON p.employee_id=e.id WHERE p.end_date IS NULL GROUP BY e.id HAVING COUNT(p.id)>1;")
    except Error as e:
        print("❌ MySQL error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

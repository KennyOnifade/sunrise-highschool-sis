import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        dbname="highschool_sis_db",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
    )

def initialize_database():
    """Create all necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER CHECK (age >= 0),
            grade_level INTEGER CHECK (
                grade_level BETWEEN 9 AND 12),
            subject VARCHAR(100),
            letter_grade CHAR(2) CHECK (
                letter_grade IN (
                    'A+', 'A', 'A-',
                    'B+', 'B', 'B-',
                    'C+', 'C', 'C-',
                    'D+', 'D', 'D-',
                    'F'
                )
            ),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            attendance_date DATE NOT NULL,
            status VARCHAR(10) CHECK (
                status IN ('Present', 'Absent', 'Late')
            ),
            recorded_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'teacher'
        );
    """)

    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            action VARCHAR(200),
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ High School database tables created successfully!")

def log_action(username, action):
    """Record every user action for security auditing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (username, action)
        VALUES (%s, %s);
    """, (username, action))
    conn.commit()
    cursor.close()
    conn.close()

# Test the connection when this file is run directly
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Connected to highschool_sis_db successfully!")
        conn.close()
        initialize_database()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
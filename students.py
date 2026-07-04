from database import get_connection, log_action
from datetime import date

def insert_student(name, email, age, grade_level,
                  subject, letter_grade, current_user):
    """
    Insert a new student into the database.

    Args:
        name (str): Student full name.
        email (str): Student email address.
        age (int): Student age.
        grade_level (int): Grade level (9-12).
        subject (str): Subject name.
        letter_grade (str): Letter grade (A, B, C, D, F).
        current_user (dict): Logged in user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (name, email, age,
                grade_level, subject, letter_grade)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """, (name.strip().title(), email.lower(),
              age, grade_level, subject, letter_grade))
        conn.commit()
        log_action(current_user["username"],
                  f"Added student: {name}")
        print(f"✅ Student '{name}' added successfully.")
    except Exception as e:
        print(f"❌ Error inserting student: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_all_students(current_user):
    """
    Retrieve all students from the database.

    Args:
        current_user (dict): Logged in user.

    Returns:
        list: List of all student records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, email, age, grade_level,
               subject, letter_grade
        FROM students
        ORDER BY grade_level, name;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              "Viewed all student records")
    return rows

def filter_students_by_grade_level(grade_level, current_user):
    """
    Filter students by grade level.

    Args:
        grade_level (int): Grade level (9-12).
        current_user (dict): Logged in user.

    Returns:
        list: Filtered student records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, email, age, grade_level,
               subject, letter_grade
        FROM students
        WHERE grade_level = %s
        ORDER BY name;
    """, (grade_level,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              f"Filtered students by grade level {grade_level}")
    return rows

def get_grade_counts(current_user):
    """
    Count students per letter grade from real data.

    Args:
        current_user (dict): Logged in user.

    Returns:
        dict: Letter grades and their student counts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT letter_grade, COUNT(*) as count
        FROM students
        GROUP BY letter_grade
        ORDER BY letter_grade;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              "Viewed grade distribution analytics")
    return {row[0]: row[1] for row in rows}

def get_subject_counts(current_user):
    """
    Count students per subject from real data.

    Args:
        current_user (dict): Logged in user.

    Returns:
        dict: Subject names and their student counts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subject, COUNT(*) as count
        FROM students
        GROUP BY subject
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              "Viewed subject enrollment analytics")
    return {row[0]: row[1] for row in rows}

def record_attendance(student_id, status, current_user):
    """
    Record attendance for a student.

    Args:
        student_id (int): Student ID.
        status (str): Present, Absent, or Late.
        current_user (dict): Logged in user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attendance (student_id,
                attendance_date, status, recorded_by)
            VALUES (%s, %s, %s, %s);
        """, (student_id, date.today(),
              status, current_user["username"]))
        conn.commit()
        log_action(current_user["username"],
                  f"Recorded attendance for student "
                  f"ID {student_id}: {status}")
        print(f"✅ Attendance recorded: {status}")
    except Exception as e:
        print(f"❌ Error recording attendance: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_attendance_summary(current_user):
    """
    Get attendance summary for all students.

    Args:
        current_user (dict): Logged in user.

    Returns:
        list: Attendance summary records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.grade_level,
               COUNT(CASE WHEN a.status = 'Present'
                     THEN 1 END) as present,
               COUNT(CASE WHEN a.status = 'Absent'
                     THEN 1 END) as absent,
               COUNT(CASE WHEN a.status = 'Late'
                     THEN 1 END) as late
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id, s.name, s.grade_level
        ORDER BY s.grade_level, s.name;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              "Viewed attendance summary")
    return rows

def add_sample_students(current_user):
    """
    Add realistic sample high school students.

    Args:
        current_user (dict): Logged in user.
    """
    sample_students = [
        ("James Carter",    "james.carter@school.edu",
         14, 9,  "Mathematics", "A"),
        ("Maria Lopez",     "maria.lopez@school.edu",
         15, 10, "English",     "B+"),
        ("Robert Johnson",  "robert.johnson@school.edu",
         16, 11, "Science",     "A-"),
        ("Emily Davis",     "emily.davis@school.edu",
         17, 12, "Mathematics", "B"),
        ("Michael Brown",   "michael.brown@school.edu",
         14, 9,  "History",     "C+"),
        ("Sarah Wilson",    "sarah.wilson@school.edu",
         15, 10, "Science",     "A"),
        ("David Martinez",  "david.martinez@school.edu",
         16, 11, "English",     "B-"),
        ("Jennifer Taylor", "jennifer.taylor@school.edu",
         17, 12, "History",     "A-"),
        ("William Anderson","william.anderson@school.edu",
         14, 9,  "Science",     "B+"),
        ("Linda Thomas",    "linda.thomas@school.edu",
         15, 10, "Mathematics", "A"),
    ]
    print("Adding sample students...")
    for name, email, age, grade, subject, lg in sample_students:
        insert_student(name, email, age, grade,
                      subject, lg, current_user)
    print("✅ Sample students added successfully!")

# Test when run directly
if __name__ == "__main__":
    from auth import login
    user = login("principal", "Admin1234!")
    if user:
        add_sample_students(user)
        print("\nAll Students:")
        students = get_all_students(user)
        for s in students:
            print(f"  {s[0]:<25} | Grade {s[3]}"
                  f" | {s[4]:<15} | {s[5]}")
        print("\nGrade Distribution:")
        grades = get_grade_counts(user)
        for grade, count in grades.items():
            print(f"  {grade}: {count} students")
        print("\nSubject Enrollment:")
        subjects = get_subject_counts(user)
        for subject, count in subjects.items():
            print(f"  {subject}: {count} students")
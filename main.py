import matplotlib.pyplot as plt
from auth import login
from students import (get_all_students,
                      filter_students_by_grade_level,
                      get_grade_counts, get_subject_counts,
                      insert_student, record_attendance,
                      get_attendance_summary)
from database import log_action

def visualize_data(grade_counts, subject_counts, students):
    """
    Create visualizations from real database data.

    Args:
        grade_counts (dict): Real grade data from database.
        subject_counts (dict): Real subject data from database.
        students (list): List of student records.
    """
    if not grade_counts:
        print("❌ No data to visualize.")
        return

    # Bar chart — grade distribution
    plt.figure(figsize=(10, 6))
    plt.bar(grade_counts.keys(),
            grade_counts.values(),
            color="skyblue", edgecolor="black")
    plt.xlabel("Letter Grade")
    plt.ylabel("Number of Students")
    plt.title("Grade Distribution Across All Subjects")
    plt.tight_layout()
    plt.savefig("grade_distribution.png")
    plt.show()

    # Pie chart — subject enrollment
    plt.figure(figsize=(8, 6))
    plt.pie(subject_counts.values(),
            labels=subject_counts.keys(),
            autopct="%1.1f%%",
            colors=["lightblue", "lightgreen",
                   "lightcoral", "lightyellow"])
    plt.title("Student Enrollment by Subject")
    plt.tight_layout()
    plt.savefig("subject_enrollment_pie.png")
    plt.show()

    # Bar chart — students per grade level
    grade_level_counts = {}
    for s in students:
        gl = f"Grade {s[3]}"
        grade_level_counts[gl] = \
            grade_level_counts.get(gl, 0) + 1
    plt.figure(figsize=(8, 6))
    plt.bar(grade_level_counts.keys(),
            grade_level_counts.values(),
            color="lightgreen", edgecolor="black")
    plt.xlabel("Grade Level")
    plt.ylabel("Number of Students")
    plt.title("Student Count by Grade Level")
    plt.tight_layout()
    plt.savefig("students_per_grade_level.png")
    plt.show()

    print("✅ Visualizations saved and displayed!")

def add_new_student(current_user):
    """
    Prompt user to enter a new student's details.

    Args:
        current_user (dict): Logged in user.
    """
    print("\n--- Add New Student ---")
    name = input("Student full name: ")
    email = input("Student email: ")
    while True:
        try:
            age = int(input("Student age: "))
            if age < 0:
                print("❌ Age cannot be negative.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid age.")
    while True:
        try:
            grade_level = int(input("Grade level (9-12): "))
            if grade_level not in [9, 10, 11, 12]:
                print("❌ Grade level must be 9, 10, 11, or 12.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid grade level.")
    subject = input("Subject: ")
    while True:
        letter_grade = input(
            "Letter grade (A+/A/A-/B+/B/B-/"
            "C+/C/C-/D+/D/D-/F): ").strip().upper()
        valid = ["A+","A","A-","B+","B","B-",
                "C+","C","C-","D+","D","D-","F"]
        if letter_grade not in valid:
            print("❌ Invalid grade. Please try again.")
            continue
        break
    insert_student(name, email, age, grade_level,
                  subject, letter_grade, current_user)

def take_attendance(current_user):
    """
    Record attendance for students.

    Args:
        current_user (dict): Logged in user.
    """
    students = get_all_students(current_user)
    if not students:
        print("No students found.")
        return
    print("\n--- Take Attendance ---")
    print(f"{'ID':<5}{'Name':<25}{'Grade'}")
    print("-"*40)
    for i, s in enumerate(students, 1):
        print(f"{i:<5}{s[0]:<25}Grade {s[3]}")
    while True:
        try:
            student_num = int(input(
                "\nEnter student number: "))
            if student_num < 1 or \
               student_num > len(students):
                print("❌ Invalid student number.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number.")
    while True:
        status = input(
            "Status (Present/Absent/Late): ").strip().title()
        if status not in ["Present", "Absent", "Late"]:
            print("❌ Please enter Present, Absent, or Late.")
            continue
        break

    # Get student ID from database
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM students WHERE name = %s;
    """, (students[student_num - 1][0],))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        record_attendance(result[0], status, current_user)
    else:
        print("❌ Student not found.")

def generate_report(students, grade_counts,
                   subject_counts, current_user):
    """
    Save a student performance report to a text file.

    Args:
        students (list): All student records.
        grade_counts (dict): Grade distribution.
        subject_counts (dict): Subject enrollment.
        current_user (dict): Logged in user.
    """
    filename = "highschool_performance_report.txt"
    try:
        with open(filename, "w") as f:
            f.write("="*50 + "\n")
            f.write("  STUDENT PERFORMANCE REPORT\n")
            f.write("  Sunrise High School SIS\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total Students: {len(students)}\n\n")
            f.write("Grade Distribution:\n")
            for grade, count in grade_counts.items():
                f.write(f"  {grade}: {count} students\n")
            f.write("\nSubject Enrollment:\n")
            for subject, count in subject_counts.items():
                f.write(f"  {subject}: {count} students\n")
            f.write("\nFull Student List:\n")
            f.write("-"*50 + "\n")
            for s in students:
                f.write(f"  {s[0]:<25} | Grade {s[3]}"
                       f" | {s[4]:<15} | {s[5]}\n")
        log_action(current_user["username"],
                  "Generated performance report")
        print(f"✅ Report saved to '{filename}'")
    except IOError as e:
        print(f"❌ Error saving report: {e}")

def main():
    """Main High School SIS with login and full menu."""
    print("\n" + "="*50)
    print("   Welcome to Sunrise High School SIS")
    print("="*50)

    # --- LOGIN REQUIRED ---
    current_user = None
    attempts = 0
    while current_user is None:
        if attempts >= 3:
            print("❌ Too many failed attempts. Exiting.")
            return
        print("\nPlease log in to continue.")
        username = input("Username: ")
        password = input("Password: ")
        current_user = login(username, password)
        if current_user is None:
            attempts += 1
            remaining = 3 - attempts
            if remaining > 0:
                print(f"  {remaining} attempt(s) remaining.")

    # --- MAIN MENU ---
    while True:
        print("\n" + "-"*50)
        print(f"  Logged in as: {current_user['username']}"
              f" ({current_user['role']})")
        print("-"*50)
        print("1. View all students")
        print("2. Filter students by grade level")
        print("3. Add a new student")
        print("4. Take attendance")
        print("5. View attendance summary")
        print("6. View analytics and visualizations")
        print("7. Generate performance report")
        print("8. Exit")
        print("-"*50)
        choice = input("Enter your choice (1-8): ")

        if choice == "1":
            students = get_all_students(current_user)
            if students:
                print(f"\n{'Name':<25}{'Grade':<10}"
                      f"{'Subject':<20}{'Grade'}")
                print("-"*65)
                for s in students:
                    print(f"{s[0]:<25}Grade {s[3]:<4}"
                          f"{s[4]:<20}{s[5]}")
            else:
                print("No students found.")

        elif choice == "2":
            while True:
                try:
                    gl = int(input(
                        "Enter grade level (9-12): "))
                    if gl not in [9, 10, 11, 12]:
                        print("❌ Must be 9, 10, 11, or 12.")
                        continue
                    break
                except ValueError:
                    print("❌ Please enter a valid number.")
            students = filter_students_by_grade_level(
                gl, current_user)
            if students:
                print(f"\nGrade {gl} Students:")
                print(f"{'Name':<25}{'Subject':<20}"
                      f"{'Letter Grade'}")
                print("-"*55)
                for s in students:
                    print(f"{s[0]:<25}{s[4]:<20}{s[5]}")
            else:
                print(f"No students found in Grade {gl}.")

        elif choice == "3":
            add_new_student(current_user)

        elif choice == "4":
            take_attendance(current_user)

        elif choice == "5":
            summary = get_attendance_summary(current_user)
            if summary:
                print(f"\n{'Name':<25}{'Grade':<10}"
                      f"{'Present':<10}{'Absent':<10}"
                      f"{'Late'}")
                print("-"*65)
                for row in summary:
                    print(f"{row[0]:<25}Grade {row[1]:<4}"
                          f"{row[2]:<10}{row[3]:<10}{row[4]}")
            else:
                print("No attendance records found.")

        elif choice == "6":
            students = get_all_students(current_user)
            grade_counts = get_grade_counts(current_user)
            subject_counts = get_subject_counts(current_user)
            if not students:
                print("No data available to analyze.")
                continue
            print("\n--- Academic Analytics ---")
            print(f"Total Students: {len(students)}")
            print("\nGrade Distribution:")
            for grade, count in grade_counts.items():
                print(f"  {grade}: {count} students")
            print("\nSubject Enrollment:")
            for subject, count in subject_counts.items():
                print(f"  {subject}: {count} students")
            visualize_data(grade_counts,
                          subject_counts, students)
            log_action(current_user["username"],
                      "Viewed analytics and visualizations")

        elif choice == "7":
            students = get_all_students(current_user)
            grade_counts = get_grade_counts(current_user)
            subject_counts = get_subject_counts(current_user)
            if not students:
                print("No data available for report.")
                continue
            generate_report(students, grade_counts,
                          subject_counts, current_user)

        elif choice == "8":
            log_action(current_user["username"],
                      "Logged out of High School SIS")
            print("\nGoodbye! Keep inspiring students! 👋")
            break

        else:
            print("❌ Invalid choice. Please enter 1-8.")

if __name__ == "__main__":
    main()
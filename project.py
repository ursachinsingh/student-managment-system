import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# ==================================================
# DATABASE SETTINGS
# IMPORTANT: Replace YOUR_PASSWORD with your MySQL
# root password. Keep database name as student_db.
# ==================================================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sachin",
        database="student_db"
    )


# ==================================================
# DATABASE SETUP
# Creates the database/table if they do not exist.
# ==================================================

def setup_database():
    conn = None
    cursor = None
    try:
        # Connect without selecting a database first.
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sachin"
        )
        cursor = conn.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS student_db"
        )
        cursor.execute("USE student_db")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                course VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL
            )
        """)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror(
            "MySQL Connection Error",
            "MySQL database setup failed.\n\n"
            "Check that MySQL Server is running and replace "
            "YOUR_PASSWORD with your actual MySQL root password.\n\n"
            f"Details: {e}"
        )
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# HELPERS
# ==================================================

def clear_fields():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)


def get_connection_or_show_error():
    try:
        return connect_db()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None


# ==================================================
# ADD STUDENT
# ==================================================

def add_student():
    student_id = id_entry.get().strip()
    name = name_entry.get().strip()
    course = course_entry.get().strip()
    phone = phone_entry.get().strip()

    if not student_id or not name or not course or not phone:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in Student ID, Name, Course and Phone."
        )
        return

    try:
        student_id = int(student_id)
        if student_id <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid ID", "Student ID must be a positive whole number."
        )
        return

    conn = None
    cursor = None
    try:
        conn = get_connection_or_show_error()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO students (id, name, course, phone)
            VALUES (%s, %s, %s, %s)
            """,
            (student_id, name, course, phone)
        )
        conn.commit()
        messagebox.showinfo("Success", "Student added successfully!")
        clear_fields()
        view_students(show_error=True)

    except mysql.connector.IntegrityError:
        messagebox.showerror(
            "Duplicate ID",
            f"Student ID {student_id} already exists. Use another ID."
        )
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# VIEW STUDENTS
# ==================================================

def view_students(show_error=True):
    conn = None
    cursor = None
    try:
        conn = get_connection_or_show_error()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, course, phone FROM students ORDER BY id"
        )
        records = cursor.fetchall()

        for item in table.get_children():
            table.delete(item)

        for row in records:
            table.insert("", tk.END, values=row)

    except mysql.connector.Error as e:
        if show_error:
            messagebox.showerror("Database Error", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# SEARCH STUDENT
# ==================================================

def search_student():
    student_id = id_entry.get().strip()

    if not student_id:
        messagebox.showwarning(
            "Missing ID", "Enter a Student ID or select a student from the table."
        )
        return

    try:
        student_id = int(student_id)
        if student_id <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid ID", "Student ID must be a positive whole number."
        )
        return

    conn = None
    cursor = None
    try:
        conn = get_connection_or_show_error()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, course, phone FROM students WHERE id = %s",
            (student_id,)
        )
        record = cursor.fetchone()

        if record is None:
            messagebox.showwarning(
                "Not Found",
                f"Student ID {student_id} was not found in database student_db."
            )
            return

        clear_fields()
        id_entry.insert(0, str(record[0]))
        name_entry.insert(0, str(record[1]))
        course_entry.insert(0, str(record[2]))
        phone_entry.insert(0, str(record[3]))

        # Highlight matching row in the table.
        for item in table.get_children():
            values = table.item(item, "values")
            if values and str(values[0]) == str(record[0]):
                table.selection_set(item)
                table.focus(item)
                table.see(item)
                break

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# UPDATE STUDENT
# ==================================================

def update_student():
    student_id = id_entry.get().strip()
    name = name_entry.get().strip()
    course = course_entry.get().strip()
    phone = phone_entry.get().strip()

    if not student_id:
        messagebox.showwarning(
            "Missing ID", "Enter a Student ID or select a student from the table."
        )
        return

    if not name or not course or not phone:
        messagebox.showwarning(
            "Missing Information", "Fill in Name, Course and Phone before updating."
        )
        return

    try:
        student_id = int(student_id)
        if student_id <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid ID", "Student ID must be a positive whole number."
        )
        return

    conn = None
    cursor = None
    try:
        conn = get_connection_or_show_error()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE students
            SET name = %s, course = %s, phone = %s
            WHERE id = %s
            """,
            (name, course, phone, student_id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Student updated successfully!")
        else:
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            exists = cursor.fetchone()
            if exists:
                messagebox.showinfo(
                    "No Changes", "The student details are already the same."
                )
            else:
                messagebox.showwarning(
                    "Not Found", f"Student ID {student_id} was not found."
                )

        view_students(show_error=True)

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# DELETE STUDENT
# ==================================================

def delete_student():
    student_id = id_entry.get().strip()

    if not student_id:
        messagebox.showwarning(
            "Missing ID", "Enter a Student ID or select a student from the table."
        )
        return

    try:
        student_id = int(student_id)
        if student_id <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid ID", "Student ID must be a positive whole number."
        )
        return

    confirmed = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete Student ID {student_id}?"
    )
    if not confirmed:
        return

    conn = None
    cursor = None
    try:
        conn = get_connection_or_show_error()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM students WHERE id = %s",
            (student_id,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Student deleted successfully!")
            clear_fields()
            view_students(show_error=True)
        else:
            messagebox.showwarning(
                "Not Found",
                f"Student ID {student_id} was not found in database student_db."
            )

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ==================================================
# SELECT STUDENT FROM TABLE
# ==================================================

def select_student(event=None):
    selected = table.selection()
    if not selected:
        return

    values = table.item(selected[0], "values")
    if len(values) != 4:
        return

    clear_fields()
    id_entry.insert(0, str(values[0]))
    name_entry.insert(0, str(values[1]))
    course_entry.insert(0, str(values[2]))
    phone_entry.insert(0, str(values[3]))


# ==================================================
# MAIN WINDOW
# ==================================================

root = tk.Tk()
root.title("Student Management System")
root.geometry("800x620")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Student Management System",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)

input_frame = tk.Frame(root)
input_frame.pack(pady=5)

tk.Label(input_frame, text="Student ID", font=("Arial", 12)).grid(
    row=0, column=0, padx=10, pady=7, sticky="e"
)
id_entry = tk.Entry(input_frame, width=30)
id_entry.grid(row=0, column=1, padx=5, pady=7)

tk.Label(input_frame, text="Name", font=("Arial", 12)).grid(
    row=1, column=0, padx=10, pady=7, sticky="e"
)
name_entry = tk.Entry(input_frame, width=30)
name_entry.grid(row=1, column=1, padx=5, pady=7)

tk.Label(input_frame, text="Course", font=("Arial", 12)).grid(
    row=2, column=0, padx=10, pady=7, sticky="e"
)
course_entry = tk.Entry(input_frame, width=30)
course_entry.grid(row=2, column=1, padx=5, pady=7)

tk.Label(input_frame, text="Phone", font=("Arial", 12)).grid(
    row=3, column=0, padx=10, pady=7, sticky="e"
)
phone_entry = tk.Entry(input_frame, width=30)
phone_entry.grid(row=3, column=1, padx=5, pady=7)

button_frame = tk.Frame(root)
button_frame.pack(pady=12)

tk.Button(
    button_frame, text="Add Student", width=16, command=add_student
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    button_frame, text="View Students", width=16, command=view_students
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    button_frame, text="Search", width=16, command=search_student
).grid(row=0, column=2, padx=5, pady=5)

tk.Button(
    button_frame, text="Update", width=16, command=update_student
).grid(row=1, column=0, padx=5, pady=5)

tk.Button(
    button_frame, text="Delete", width=16, command=delete_student
).grid(row=1, column=1, padx=5, pady=5)

tk.Button(
    button_frame, text="Clear", width=16, command=clear_fields
).grid(row=1, column=2, padx=5, pady=5)

table_frame = tk.Frame(root)
table_frame.pack(padx=15, pady=10, fill="both", expand=True)

columns = ("ID", "Name", "Course", "Phone")
table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

for column in columns:
    table.heading(column, text=column)
    if column == "Name":
        table.column(column, width=190, anchor="center")
    elif column == "Course":
        table.column(column, width=160, anchor="center")
    else:
        table.column(column, width=120, anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame, orient="vertical", command=table.yview
)
table.configure(yscrollcommand=scrollbar.set)
table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

table.bind("<<TreeviewSelect>>", select_student)

# Set up database, then load records.
if setup_database():
    view_students(show_error=True)

root.mainloop()
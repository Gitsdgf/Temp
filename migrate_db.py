import sqlite3
import os

# Path to the database file
db_path = 'instance/employees.db'

# Check if the database file exists
if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if employee_id column exists in user table
cursor.execute("PRAGMA table_info(user)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'employee_id' not in column_names:
    print("Adding employee_id column to user table...")
    cursor.execute("ALTER TABLE user ADD COLUMN employee_id INTEGER")
    conn.commit()
    print("Column added successfully.")
else:
    print("employee_id column already exists in user table.")

# Close the connection
conn.close()
print("Database migration completed.")
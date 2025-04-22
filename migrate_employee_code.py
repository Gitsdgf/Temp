from app import app, db, User
import sqlite3

# Run this script to add the employee_code column to the User table

def add_employee_code_column():
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/employees.db')
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'employee_code' not in column_names:
            print("Adding employee_code column to User table...")
            cursor.execute("ALTER TABLE user ADD COLUMN employee_code TEXT")
            conn.commit()
            print("Column added successfully!")
        else:
            print("employee_code column already exists.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    with app.app_context():
        if add_employee_code_column():
            print("Migration completed successfully!")
        else:
            print("Migration failed!")
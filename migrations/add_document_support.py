import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create upload directories
def create_upload_directories():
    from app import app
    os.makedirs(app.config['PROFILE_PICTURES_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOCUMENTS_FOLDER'], exist_ok=True)
    print("Created upload directories")

# Add new columns to Employee table
def add_profile_picture_column():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    # Check if profile_picture column exists
    cursor.execute("PRAGMA table_info(employee)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'profile_picture' not in column_names:
        cursor.execute("ALTER TABLE employee ADD COLUMN profile_picture TEXT")
        print("Added profile_picture column to Employee table")
    else:
        print("profile_picture column already exists in Employee table")
    
    conn.commit()
    conn.close()

# Create Document table
def create_document_table():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    # Check if document table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE document (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            document_type TEXT NOT NULL,
            upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employee (id)
        )
        ''')
        print("Created Document table")
    else:
        print("Document table already exists")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Running database migration for document support...")
    create_upload_directories()
    add_profile_picture_column()
    create_document_table()
    print("Migration completed successfully!")
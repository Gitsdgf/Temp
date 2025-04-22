# Employee Management System

A Flask-based web application for managing employee information with authentication.

## Features

- Secure authentication system with login/logout functionality
- Add, edit, and delete employee records (admin only)
- View employees by department
- Search for employees by name or position
- Department-first approach on homepage
- Position suggestions system
- Calendar date picker for date selection
- Smart search functionality
- Improved UI with Bootstrap icons
- Department overview dashboard
- Fully responsive design for all devices (desktop, tablet, mobile)

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

To run the application, execute:

```bash
python app.py
```

The application will be available at http://localhost:12001

5. Login with default credentials:
   - Username: admin
   - Password: admin

## Technologies Used

- Flask: Web framework
- SQLAlchemy: ORM for database operations
- Flask-Login: User session management
- Werkzeug: Password hashing and security
- Bootstrap 5: Frontend styling and responsive design
- Bootstrap Icons: Icon library
- jQuery: JavaScript library for AJAX requests
- Flatpickr: Date picker library

## Database

The application uses SQLite as the database, which is stored in the file `employees.db`. This file will be created automatically when you first run the application.

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
  - `base.html`: Base template with common elements
  - `index.html`: Home page with department dashboard
  - `add_employee.html`: Form for adding new employees
  - `employee_details.html`: Detailed view of an employee
  - `edit_employee.html`: Form for editing employee information
  - `department_employees.html`: List of employees in a department
  - `all_employees.html`: List of all employees
  - `search_results.html`: Search results page
  - `login.html`: Authentication page
- `static/`: Static files
  - `css/`: CSS files
    - `style.css`: Custom styles
- `instance/employees.db`: SQLite database file (created automatically)

## Database Schema

The application uses SQLite with the following models:

1. Employee
   - id: Integer, primary key
   - name: String, employee's full name
   - email: String, employee's email address
   - phone: String, employee's phone number
   - department: String, employee's department
   - position: String, employee's job position
   - hire_date: Date, when the employee was hired
   - salary: Float, employee's salary
   - address: String, employee's address
   - notes: Text, additional notes about the employee

2. User
   - id: Integer, primary key
   - username: String, unique username for login
   - password_hash: String, hashed password for security

## Security Features

- Password hashing using Werkzeug's security functions
- Route protection with login_required decorator
- Session management with Flask-Login
- CSRF protection with Flask's built-in CSRF protection

## Responsive Design

The application is fully responsive and optimized for:
- Desktop computers
- Tablets (iPad, etc.)
- Mobile phones (iOS and Android)

## Default Admin Account

On first run, the application creates a default admin account:
- Username: admin
- Password: admin

It's recommended to change this password after first login for security purposes.
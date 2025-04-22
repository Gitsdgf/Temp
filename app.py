from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
import os
from markupsafe import Markup
import json
import hashlib
import uuid

app = Flask(__name__)

# Add nl2br filter
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return Markup(value.replace('\n', '<br>'))
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER_PHOTOS'] = os.path.join(app.root_path, 'static', 'uploads', 'photos')
app.config['UPLOAD_FOLDER_DOCUMENTS'] = os.path.join(app.root_path, 'static', 'uploads', 'documents')
app.config['ALLOWED_EXTENSIONS_PHOTOS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_EXTENSIONS_DOCUMENTS'] = {'pdf', 'doc', 'docx', 'txt'}

db = SQLAlchemy(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

# File upload helper functions
def allowed_file_photo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_PHOTOS']

def allowed_file_document(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_DOCUMENTS']

def save_file(file, folder):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Generate a unique filename to avoid overwriting
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(folder, unique_filename)
        file.save(file_path)
        return os.path.join('uploads', 'photos' if folder == app.config['UPLOAD_FOLDER_PHOTOS'] else 'documents', unique_filename)
    return None

# Employee model - simplified version
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    hire_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    address = db.Column(db.String(200), nullable=False)
    salary = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)  # Path to the photo file
    education_background = db.Column(db.Text, nullable=True)  # Education details
    education_document = db.Column(db.String(255), nullable=True)  # Path to education document
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

# Create database tables and default admin user
with app.app_context():
    db.create_all()
    
    # Create default admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to index
    if 'logged_in' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # Get all unique departments
    departments = db.session.query(Employee.department).distinct().all()
    departments = [dept[0] for dept in departments]
    
    # Count employees per department and total
    department_counts = {}
    total_employees = 0
    
    for dept in departments:
        count = Employee.query.filter_by(department=dept).count()
        department_counts[dept] = count
        total_employees += count
    
    return render_template('index.html', 
                          departments=departments, 
                          department_counts=department_counts,
                          total_employees=total_employees)

@app.route('/department/<department>')
@login_required
def department_employees(department):
    employees = Employee.query.filter_by(department=department).all()
    return render_template('department_employees.html', department=department, employees=employees)

@app.route('/add-department', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        
        if not department_name:
            flash('Department name cannot be empty', 'danger')
            return redirect(url_for('add_department'))
        
        # Check if department already exists
        existing_departments = db.session.query(Employee.department).distinct().all()
        existing_departments = [dept[0] for dept in existing_departments if dept[0]]
        
        if department_name in existing_departments:
            flash(f'Department "{department_name}" already exists', 'warning')
            return redirect(url_for('index'))
        
        # Create a placeholder employee to establish the department
        placeholder = Employee(
            first_name="Department",
            last_name="Placeholder",
            email=f"{department_name.lower().replace(' ', '.')}@example.com",
            phone="N/A",
            department=department_name,
            position="Department Head",
            hire_date=datetime.utcnow(),
            salary=0,
            address="N/A",
            notes="This is a placeholder record to establish the department. You can delete this record after adding real employees to this department."
        )
        
        db.session.add(placeholder)
        db.session.commit()
        
        flash(f'Department "{department_name}" has been added successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_department.html')

@app.route('/search')
@login_required
def search_employees():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))
    
    # Search by name or position
    employees = Employee.query.filter(
        db.or_(
            Employee.first_name.ilike(f'%{query}%'),
            Employee.last_name.ilike(f'%{query}%'),
            Employee.position.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('search_results.html', employees=employees, query=query)

@app.route('/positions')
@login_required
def get_positions():
    query = request.args.get('q', '')
    positions = db.session.query(Employee.position).distinct().filter(
        Employee.position.ilike(f'%{query}%')
    ).all()
    return jsonify([position[0] for position in positions])

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    # Get all unique departments for the dropdown
    departments = db.session.query(Employee.department).distinct().all()
    departments = [dept[0] for dept in departments]
    
    # Add default departments if none exist
    if not departments:
        departments = [
            "Human Resources", "Information Technology", "Finance", 
            "Marketing", "Operations", "Sales", 
            "Research & Development", "Customer Support"
        ]
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        position = request.form['position']
        hire_date_str = request.form['hire_date']
        address = request.form['address']
        salary = request.form.get('salary', 0)
        notes = request.form.get('notes', '')
        
        # Convert string date to datetime object
        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
        
        # Convert salary to float if provided
        try:
            salary = float(salary) if salary else 0
        except ValueError:
            salary = 0
        
        # Check if email already exists
        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_employee'))
        
        # Handle file uploads
        photo_path = None
        education_doc_path = None
        
        # Process photo upload
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename and allowed_file_photo(photo_file.filename):
                photo_path = save_file(photo_file, app.config['UPLOAD_FOLDER_PHOTOS'])
        
        # Process education document upload
        if 'education_document' in request.files:
            doc_file = request.files['education_document']
            if doc_file and doc_file.filename and allowed_file_document(doc_file.filename):
                education_doc_path = save_file(doc_file, app.config['UPLOAD_FOLDER_DOCUMENTS'])
        
        # Get education background
        education_background = request.form.get('education_background', '')
        
        # Create new employee
        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            position=position,
            hire_date=hire_date,
            address=address,
            salary=salary,
            notes=notes,
            photo=photo_path,
            education_background=education_background,
            education_document=education_doc_path
        )
        
        # Add to database
        db.session.add(new_employee)
        db.session.commit()
        
        flash('Employee added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_employee.html', departments=departments)

@app.route('/employee/<int:id>')
@login_required
def employee_details(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employee_details.html', employee=employee)

@app.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Get all unique departments for the dropdown
    departments = db.session.query(Employee.department).distinct().all()
    departments = [dept[0] for dept in departments]
    
    if request.method == 'POST':
        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.email = request.form['email']
        employee.phone = request.form['phone']
        employee.department = request.form['department']
        employee.position = request.form['position']
        employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
        employee.address = request.form['address']
        
        # Get salary and notes
        salary = request.form.get('salary', 0)
        employee.notes = request.form.get('notes', '')
        
        # Convert salary to float if provided
        try:
            employee.salary = float(salary) if salary else 0
        except ValueError:
            employee.salary = 0
            
        # Handle education background
        employee.education_background = request.form.get('education_background', '')
        
        # Handle photo upload or removal
        if 'remove_photo' in request.form:
            # If the employee has a photo and the remove checkbox is checked
            if employee.photo:
                # Delete the file from the filesystem
                try:
                    os.remove(os.path.join(app.root_path, 'static', employee.photo))
                except:
                    pass  # If file doesn't exist, just continue
                employee.photo = None
        elif 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename and allowed_file_photo(photo_file.filename):
                # If employee already has a photo, delete the old one
                if employee.photo:
                    try:
                        os.remove(os.path.join(app.root_path, 'static', employee.photo))
                    except:
                        pass  # If file doesn't exist, just continue
                # Save the new photo
                employee.photo = save_file(photo_file, app.config['UPLOAD_FOLDER_PHOTOS'])
        
        # Handle education document upload or removal
        if 'remove_document' in request.form:
            # If the employee has a document and the remove checkbox is checked
            if employee.education_document:
                # Delete the file from the filesystem
                try:
                    os.remove(os.path.join(app.root_path, 'static', employee.education_document))
                except:
                    pass  # If file doesn't exist, just continue
                employee.education_document = None
        elif 'education_document' in request.files:
            doc_file = request.files['education_document']
            if doc_file and doc_file.filename and allowed_file_document(doc_file.filename):
                # If employee already has a document, delete the old one
                if employee.education_document:
                    try:
                        os.remove(os.path.join(app.root_path, 'static', employee.education_document))
                    except:
                        pass  # If file doesn't exist, just continue
                # Save the new document
                employee.education_document = save_file(doc_file, app.config['UPLOAD_FOLDER_DOCUMENTS'])
        
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employee_details', id=employee.id))
    
    return render_template('edit_employee.html', employee=employee, departments=departments)

@app.route('/employee/<int:id>/delete', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/all-employees')
@login_required
def all_employees():
    employees = Employee.query.all()
    return render_template('all_employees.html', employees=employees)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
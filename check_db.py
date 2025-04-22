from app import app, db, Employee

with app.app_context():
    print('Current Employees:')
    for e in Employee.query.all():
        print(f'{e.id}: {e.first_name} {e.last_name} - {e.department} ({e.position}) - Salary: ${e.salary}')
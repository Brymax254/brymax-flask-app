from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import EmployeeForm, UploadForm  # Ensure these forms are defined
from app.models import Employee  # Assuming you have an Employee model
from app import db

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(name=form.name.data, position=form.position.data)
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('employee.list_employees'))
    return render_template('employee/add_employee.html', form=form)

@employee_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Logic for handling file upload
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('employee.list_employees'))
    return render_template('employee/upload.html', form=form)
import app.forms
print(dir(app.forms))

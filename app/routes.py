import pandas as pd
import requests
from flask import render_template, current_app, send_file, flash, redirect, session, url_for, jsonify, request, make_response, Blueprint, send_from_directory
from datetime import datetime, date
import logging
from io import StringIO, BytesIO
import plotly.express as px
from pdfkit import pdfkit
from app.models import Report, DailyReport, Update, Employee, Payroll, User, Payroll, Goal, Course, Attendance, Farmer, InputDistribution, Ploughing, Harvest, Payment, Seed, Pesticide, Manure
from app import db
from app.forms import AddEmployeeForm, ProfileForm, GoalForm, CourseForm
from flask_login import login_required, current_user, login_user, logout_user
from app.utils import generate_farmer_id, admin_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os, io
from .forms import PostUpdateForm
from config import Config
import boto3
from botocore.exceptions import ClientError
from app.models import AdminContent
from app.extensions import db
# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize blueprints
main_bp = Blueprint('main', __name__)
employee_bp = Blueprint('employee', __name__)

auth_bp = Blueprint("auth", __name__)


import logging

@main_bp.route('/')
def index():
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Redirect if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')
            next_page = request.form.get('next')  # Get the next parameter
            return redirect(next_page or url_for('main.dashboard'))  # Redirect to next page or dashboard
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html')  # Stay on login page if login fails# Core Routes

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()  # Clears session data
    return redirect(url_for("main.index"))  # Correct redirect to landing page

@main_bp.route('/api/reports', methods=['GET'])
def fetch_reports():
    reports = Report.query.all()
    report_data = [{
        'id': report.id,
        'report_date': report.report_date.strftime('%Y-%m-%d'),
        'farmers_registered': report.farmers_registered,
        'total_acres': report.total_acres,
        'staff_attendance': report.staff_attendance
    } for report in reports]
    return jsonify(report_data)


@main_bp.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    """
    Dashboard route to display farmers, dynamically retrieve uploaded documents from S3,
    allow admins to post updates directly, and show admin updates, memos, and advertisements.
    """
    # Process update submission if the request is POST
    if request.method == "POST":
        # Only allow admin users to post updates
        if not current_user.is_admin:
            flash("Admin access only.", "danger")
            return redirect(url_for('main.dashboard'))

        update_type = request.form.get("content_type")
        content = request.form.get("content")
        if not update_type or not content:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for('main.dashboard'))

        # Create a new update entry.
        # We store the type in the field 'content_type'; your model will then reflect whether
        # this is an update, memo, or advertisement.
        new_update = AdminContent(content_type=update_type, content=content, created_at=datetime.utcnow())
        db.session.add(new_update)
        try:
            db.session.commit()
            flash(f"{update_type.capitalize()} posted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error posting update: {e}", "danger")
        return redirect(url_for('main.dashboard'))

    # For GET requests, proceed to fetch and display dashboard data.
    # Fetch farmers from the database
    farmers = Farmer.query.all()
    farmer = farmers[0] if farmers else None

    # Fetch files from the S3 bucket
    try:
        response = s3.list_objects_v2(Bucket=Config.AWS_STORAGE_BUCKET_NAME)
        files = [obj['Key'] for obj in response.get('Contents', [])] if 'Contents' in response else []
        if not files:
            flash("No documents found in the cloud.", "info")
    except Exception as e:
        flash(f"Error fetching documents from S3: {str(e)}", "danger")
        files = []

    # Fetch admin updates, memos, and advertisements from the database
    latest_update = AdminContent.query.filter_by(content_type='update').order_by(AdminContent.created_at.desc()).first()
    memo = AdminContent.query.filter_by(content_type='memo').order_by(AdminContent.created_at.desc()).first()
    advertisement = AdminContent.query.filter_by(content_type='advertisement').order_by(
        AdminContent.created_at.desc()).first()

    # Render the dashboard template with all the required variables
    return render_template(
        'dashboard.html',
        active_sidebar='dashboard',
        farmers=farmers,
        farmer=farmer,
        files=files,
        latest_update=latest_update,
        memo=memo,
        advertisement=advertisement,
    )

    #Employee Management Routes
@employee_bp.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    """Add a new employee."""
    form = AddEmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(name=form.name.data, position=form.position.data)
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully', 'success')
        return redirect(url_for('employee.employee_db'))
    return render_template('add_employee.html', form=form)

@employee_bp.route('/employee_db')
def employee_db():
    """Display the employee database."""
    employees = Employee.query.all()
    return render_template('employee_db.html', employees=employees)

@main_bp.route('/visualize')
@admin_required
def visualize():
    """Render the visualization page."""
    return render_template('visualize.html')

@main_bp.route('/attendance')
def attendance():
    """Attendance tracking overview."""
    return render_template('attendance.html')

@main_bp.route('/goals')
def goals_overview():
    """Goals overview."""
    return render_template('goals.html')

# Goals & Courses Routes
@main_bp.route('/goals/<int:employee_id>', methods=['GET', 'POST'])
def employee_goals(employee_id):
    """Manage employee goals."""
    employee = Employee.query.get_or_404(employee_id)
    form = GoalForm()
    if form.validate_on_submit():
        new_goal = Goal(employee_id=employee.id, description=form.description.data, progress=0.0)
        db.session.add(new_goal)
        db.session.commit()
        flash('Goal added successfully', 'success')
        return redirect(url_for('main.employee_goals', employee_id=employee.id))
    return render_template('goals.html', form=form, employee=employee, goals=employee.goals)

@main_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    """Manage courses offered."""
    form = CourseForm()
    if form.validate_on_submit():
        new_course = Course(title=form.title.data, description=form.description.data)
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully', 'success')
        return redirect(url_for('main.courses'))
    courses = Course.query.all()
    return render_template('courses.html', form=form, courses=courses)

@main_bp.route('/daily_report', methods=['GET'])
def daily_report():
    """Render the daily report form."""
    return render_template('daily_report.html', active_sidebar ='daily_report')


@main_bp.route('/submit_daily_report', methods=['POST'])
def submit_daily_report():
    try:
        # Gather data from the form
        report_date = request.form['report_date']
        officer_name = request.form['officer_name']
        farmers_registered = int(request.form['farmers_registered'])  # Convert to int
        total_acres = float(request.form['total_acres'])  # Convert to float
        tractors_in_area = int(request.form.get('tractors_in_area', 0))  # Convert to int, default 0
        acres_ploughed = float(request.form.get('acres_ploughed', 0))  # Convert to float, default 0
        staff_attendance = request.form['staff_attendance']

        # Convert report_date from string to Python date object
        report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

        # Create a new DailyReport instance
        new_report = DailyReport(
            report_date=report_date,
            officer_name=officer_name,
            farmers_registered=farmers_registered,
            total_acres=total_acres,
            tractors_in_area=tractors_in_area,
            acres_ploughed=acres_ploughed,
            staff_attendance=staff_attendance
        )

        # Save to the database
        db.session.add(new_report)
        db.session.commit()

        flash("Daily report submitted successfully!", "success")
        return redirect(url_for('main.view_reports'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('main.daily_report'))

@main_bp.route('/enroll_course/<int:employee_id>/<int:course_id>', methods=['POST'])
def enroll_course(employee_id, course_id):
    """Enroll an employee in a course."""
    employee = Employee.query.get_or_404(employee_id)
    course = Course.query.get_or_404(course_id)
    if course not in employee.courses:
        employee.courses.append(course)
        db.session.commit()
        flash(f'Employee enrolled in {course.title} successfully', 'success')
    else:
        flash(f'Employee is already enrolled in {course.title}', 'warning')
    return redirect(url_for('main.employee_db'))

# Attendance & Payroll Routes
@main_bp.route('/clock_in/<int:employee_id>', methods=['POST'])
def clock_in(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    location = request.form.get('location')
    new_attendance = Attendance(
        employee_id=employee.id,
        check_in=datetime.utcnow(),
        location=location
    )
    db.session.add(new_attendance)
    db.session.commit()
    flash('Clocked in successfully', 'success')
    return redirect(url_for('main.employee_db'))

@main_bp.route('/clock_out/<int:attendance_id>', methods=['POST'])
def clock_out(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    if not attendance.check_out:
        attendance.check_out = datetime.utcnow()
        db.session.commit()
        flash('Clocked out successfully', 'success')
    else:
        flash('Already clocked out', 'warning')
    return redirect(url_for('main.employee_db'))

# Data Visualization Routes
@main_bp.route('/google_sheets_visualize')
@admin_required
def google_sheets_visualize():
    try:
        csv_urls = [
            "https://docs.google.com/spreadsheets/d/1D3YKZn1Ei0ikIaVGy6S8ykT0XJX-i8blXB3aNWZWoak/export?format=csv",
            "https://docs.google.com/spreadsheets/d/1ue3z_lo_BYoYrMaCLNaVIQlQfMK5x5x8E8sbvEygJUI/export?format=csv",
            "https://docs.google.com/spreadsheets/d/1YeIn3YKZ7C5aKaSoaEObcavWzcRM7Nu_xtxX_7GJHTM/export?format=csv",
            "https://docs.google.com/spreadsheets/d/1btvs1-HDJJ63aLx_8xKX_ZAa1dELNzLqR-_-9bfYGJY/export?format=csv",
            "https://docs.google.com/spreadsheets/d/1uvEheiAXJJBC0Qi4sTXzqlyn3SVazi52X2JBoAXbXTU/export?format=csv"
        ]
        all_data = []
        for url in csv_urls:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = pd.read_csv(StringIO(response.text))
                all_data.append(data)
            else:
                flash(f'Failed to load data from: {url} (Status Code: {response.status_code})', 'warning')
        if not all_data:
            flash('No data loaded from Google Sheets', 'danger')
            return redirect(url_for('main.dashboard'))
        df = pd.concat(all_data, ignore_index=True)
        expected_headers = [
            'Timestamp', 'Name', 'Phone Number', 'Constituency', 'WARD',
            'Nearest Shopping Center', 'Farm Size in ACRES', 'Your Agricultural Agent'
        ]
        missing_columns = [col for col in expected_headers if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        bar_chart_field_officer = df[' Your Agricultural Agent'].value_counts().plot(kind='bar').get_figure()
        pie_chart_field_officer = df['Your Agricultural Agent'].value_counts().plot(kind='pie').get_figure()
        bar_chart_field_officer_html = bar_chart_field_officer.to_html()
        pie_chart_field_officer_html = pie_chart_field_officer.to_html()
        field_officer_entry_count_table = df['Your Agricultural Agent'].value_counts().reset_index()
        field_officer_entry_count_table.columns = ['Agent Name', 'Entry Count']
        constituency_summary_table = df.groupby('Constituency').size().reset_index(name='Entry Count')
        return render_template(
            'google_sheets_visualize.html',
            bar_chart_field_officer=bar_chart_field_officer_html,
            pie_chart_field_officer=pie_chart_field_officer_html,
            field_officer_entry_count_table=field_officer_entry_count_table.to_html(classes='table table-striped'),
            constituency_summary_table=constituency_summary_table.to_html(classes='table table-striped')
        )
    except Exception as e:
        flash(f'Error fetching data from Google Sheets: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        # Replace the data dictionary below with the actual data you need to pass into visualize.html
        data = {
            "title": "Agricultural Report",
            # Add additional key-value pairs as required by your visualize.html template
        }

        # Render the HTML using your template and the passed-in data.
        rendered = render_template('visualize.html', **data)

        # Configure pdfkit.
        # IMPORTANT: Adjust the wkhtmltopdf path as needed.
        # For Linux/MacOS, the typical path might be '/usr/local/bin/wkhtmltopdf'.
        # For Windows, you might use something like 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'.
        wkhtmltopdf_path = '/usr/local/bin/wkhtmltopdf'  # Update this path for your environment
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # Generate PDF from the rendered HTML. The second parameter (False) means the
        # PDF will be generated as a binary stream, not saved to file.
        pdf = pdfkit.from_string(rendered, False, configuration=config)

        # Create a response with the generated PDF.
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        # 'attachment' forces download; use 'inline' if you want the PDF
        # to be displayed in the browser.
        response.headers['Content-Disposition'] = 'attachment; filename=agricultural_report.pdf'
        return response
    except Exception as e:
        flash(f'PDF generation failed: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))
@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.dashboard'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('main.dashboard'))
    allowed_extensions = {'xls', 'xlsx'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        flash('Invalid file type. Only Excel files are allowed.', 'danger')
        return redirect(url_for('main.dashboard'))
    try:
        df = pd.read_excel(file, engine='openpyxl')
        expected_headers = [
            'Company Representative', 'Company name', 'CUAA (IT)', 'Technician Ref. Company',
            'Collection Group', 'Plot', 'Surf. [ha]', 'Surf. [ac]', 'Land Use', 'Variety',
            'System duration', 'Variety Group', 'SuperPlot', 'Company Center', 'Regulation',
            'Date of harvest expected', 'Closed', 'Latitude', 'Longitude', 'Date creation',
            'Date modification', 'Officer',
        ]
        missing_columns = [col for col in expected_headers if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        df['Date creation'] = pd.to_datetime(df['Date creation'], errors='coerce')
        df.sort_values('Date creation', inplace=True)

        # Generate visualizations
        histogram_graph = px.histogram(df, x='Variety', title='Histogram of Varieties').to_html(full_html=False)
        heatmap_data = df.pivot_table(index='Variety', columns='Land Use', values='Surf. [ha]', aggfunc='sum', fill_value=0)
        heatmap_graph = px.imshow(heatmap_data, title='Surface Area Heatmap').to_html(full_html=False)
        df_interval = df.resample('10D', on='Date creation').agg({'Surf. [ha]': 'sum'}).reset_index()
        ha_bar_chart = px.bar(df_interval, x='Date creation', y='Surf. [ha]', title='10-Day Bar Graph').to_html(full_html=False)
        ha_line_chart = px.line(df_interval, x='Date creation', y='Surf. [ha]', title='10-Day Line Graph').to_html(full_html=False)

        recent_df = df[df['Date creation'] >= (df['Date creation'].max() - pd.Timedelta(days=10))]
        total_ac_over_time_graph = px.line(recent_df, x='Date creation', y='Surf. [ac]',
                                           title='Total Acres - Last 10 Days',
                                           labels={'Surf. [ac]': 'Acres', 'Date creation': 'Date'}).to_html(full_html=False)

        user_days_work_data = df.groupby('Officer')['Date creation'].nunique().reset_index().rename(columns={'Date creation': 'Work Days'})
        user_days_work_bar = px.bar(user_days_work_data, x='Officer', y='Work Days', title='User  Productivity').to_html(full_html=False)

        top_10_varieties_list = df.groupby('Variety')['Surf. [ha]'].sum().nlargest(10).to_frame().to_html(classes='table table-striped', border=0)
        best_user_creation_ha_ac_list = df.groupby('Officer')[['Surf. [ha]', 'Surf. [ac]']].sum().nlargest(100, 'Surf. [ha]').to_html(classes='table table-striped', border=0)

        officer_totals = df.groupby('Officer')['Surf. [ha]'].sum().reset_index()
        officer_totals['Surf. [ac]'] = officer_totals['Surf. [ha]'] * 2.47105
        officer_totals.rename(columns={'Surf. [ha]': 'Total (ha)', 'Surf. [ac]': 'Total (ac)'}, inplace=True)
        officer_surface_table = officer_totals.to_html(classes='table table-striped', index=False, border=0)

        best_10_user_creation_companies_list = df.groupby('Officer')['Company name'].nunique().nlargest(100).to_frame().to_html(classes='table table-striped', border=0)
        best_10_user_creation_rate_list = (df.groupby('Officer')['Surf. [ac]'].sum() / df.groupby('Officer')['Company name'].nunique()).nlargest(100).to_frame(name='Rate').to_html(classes='table table-striped', border=0)

        return render_template(
            'visualize.html',
            histogram_graph=histogram_graph,
            heatmap_graph=heatmap_graph,
            ha_bar_chart=ha_bar_chart,
            ha_line_chart=ha_line_chart,
            total_ac_over_time_graph=total_ac_over_time_graph,
            user_days_work_bar=user_days_work_bar,
            top_10_varieties_list=top_10_varieties_list,
            best_user_creation_ha_ac_list=best_user_creation_ha_ac_list,
            best_10_user_creation_companies_list=best_10_user_creation_companies_list,
            best_10_user_creation_rate_list=best_10_user_creation_rate_list,
            officer_surface_table=officer_surface_table
        )
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/employees', methods=['GET'])
def api_employees():
    """API endpoint to get employee data."""
    employees = Employee.query.all()
    data = [{'id': emp.id, 'name': emp.name, 'position': emp.position} for emp in employees]
    return jsonify(data)
@main_bp.route('/view_reports')
@login_required
def view_reports():
    try:
        # Query all DailyReport entries from the database.
        reports = DailyReport.query.order_by(DailyReport.report_date.desc()).all()

        # Convert model instances to dictionaries for easier consumption in the template.
        reports_json = [
            {
                "report_date": report.report_date.strftime("%Y-%m-%d") if report.report_date else "N/A",
                "officer_name": report.officer_name or "N/A",
                "farmers_registered": report.farmers_registered or 0,
                "total_acres": report.total_acres or 0,
                "tractors_in_area": report.tractors_in_area or 0,
                "acres_ploughed": report.acres_ploughed or 0,
                "staff_attendance": report.staff_attendance or "N/A",
            }
            for report in reports
        ]

        # Aggregate performance data per officer
        performance_data = db.session.query(
            DailyReport.officer_name,
            db.func.sum(DailyReport.farmers_registered).label("total_farmers"),
            db.func.sum(DailyReport.acres_ploughed).label("total_acres")
        ).group_by(DailyReport.officer_name).all()

        # ✅ Fixed Trend Data Query: Using `func.to_char()` instead of `strftime()`
        trends_data = db.session.query(
            DailyReport.officer_name,
            db.func.to_char(DailyReport.report_date, 'YYYY-MM').label("month"),
            db.func.sum(DailyReport.farmers_registered).label("monthly_farmers"),
            db.func.sum(DailyReport.acres_ploughed).label("monthly_acres")
        ).group_by(DailyReport.officer_name, db.func.to_char(DailyReport.report_date, 'YYYY-MM')).all()

        # Aggregate staff attendance
        staff_data = db.session.query(
            DailyReport.staff_attendance.label("staff_name"),
            db.func.count(DailyReport.staff_attendance).label("attendance_count")
        ).group_by(DailyReport.staff_attendance).all()

        # Render the view_reports.html template with the processed data.
        return render_template(
            "view_reports.html",
            active_sidebar="view_reports",
            reports=reports_json,
            performance_data=performance_data,
            trends_data=trends_data,
            staff_data=staff_data
        )
    except Exception as e:
        # ✅ Log error for debugging (optional)
        print(f"Error in view_reports(): {e}")

        # Handle exceptions gracefully and flash an error message.
        flash(f"An error occurred while fetching reports: {str(e)}", "danger")
        return redirect(url_for("main.dashboard"))

@main_bp.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    try:
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
    return redirect(url_for('main.view_reports'))

@main_bp.route('/error_404')
def error_404():
    return render_template('404.html')

@main_bp.route('/error_500')
def error_500():
    return render_template ('500.html')

@main_bp.route('/api/resources', methods=['GET'])
def api_resources():
    """API endpoint to get resources."""
    return jsonify({"message": "API resources endpoint"})

@main_bp.route('/pdfs/<path:filename>', endpoint='pdfs')
def pdfs(filename):
    """Serve PDF files from the static directory."""
    return send_from_directory('static/pdfs', filename, as_attachment=False)

# If you have another route that also uses 'pdfs', rename it:
@main_bp.route('/another_pdfs/<path:filename>', endpoint='another_pdfs')
def another_pdfs(filename):
    """Serve another type of PDF files."""
    return send_from_directory('static/another_pdfs', filename, as_attachment=False)# Main Farmer zone


@main_bp.route('/register', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        # Capture form data
        phone_number = request.form['phone_number']
        existing_farmer = Farmer.query.filter_by(phone_number=phone_number).first()
        if existing_farmer:
            msg = "Phone number already registered!"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': msg}), 400
            else:
                flash(msg, "warning")
                return redirect(url_for('main.register_farmer'))

        try:
            land_size = float(request.form['land_size'])
        except ValueError:
            msg = "Invalid land size! Please enter a valid number."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': msg}), 400
            else:
                flash(msg, "danger")
                return redirect(url_for('main.register_farmer'))

        season = request.form['season']
        year = datetime.now().year
        farmer_id, farmer_number = generate_farmer_id(season, year)

        # Capture field officer from the form
        field_officer = request.form['field_officer']

        # Create the new farmer instance
        farmer = Farmer(
            unique_number=farmer_id,
            full_name=request.form['full_name'],
            county=request.form['county'],
            subcounty=request.form['subcounty'],
            ward=request.form['ward'],
            location=request.form['location'],
            phone_number=phone_number,
            village=request.form['village'],
            land_size=land_size,
            season=season,
            year=year,
            farmer_number=farmer_number,
            field_officer=field_officer
        )
        try:
            db.session.add(farmer)
            db.session.commit()
            msg = "Farmer registered successfully 😊"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': msg})
            else:
                flash(msg, "success")
                return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))
        except Exception as e:
            db.session.rollback()
            msg = "Ops! The farmer is not registered. Try again."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': msg}), 500
            else:
                flash(msg, "danger")
                return redirect(url_for('main.register_farmer'))

    return render_template('register.html')

@main_bp.route('/fetch/<string:farmer_id>')
@login_required
def fetch_farmer(farmer_id):
    farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
    if not farmer:
        flash("Farmer not found!", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('fetch.html', farmer=farmer)

@main_bp.route('/fetch')
def fetch_farmer_default():
    # Get query parameters for Farmer ID and Phone Number
    farmer_id = request.args.get('farmer_id')
    phone_number = request.args.get('phone_number')

    if farmer_id:
        # Search by Farmer ID (unique_number)
        farmer_search = Farmer.query.filter_by(unique_number=farmer_id).first()
        return render_template('fetch.html', farmer_search=farmer_search)
    elif phone_number:
        # Search by phone number
        farmer_search = Farmer.query.filter_by(phone_number=phone_number).first()
        return render_template('fetch.html', farmer_search=farmer_search)
    else:
        # If no search parameter, display all farmers
        farmers = Farmer.query.all()
        return render_template('fetch.html', farmers=farmers)

@main_bp.route('/issue_input/<farmer_id>', methods=['POST'])
def issue_input(farmer_id):
    input_type = request.form['input_type']
    distribution = InputDistribution(farmer_id=farmer_id, input_type=input_type, date_given=datetime.utcnow())
    db.session.add(distribution)
    db.session.commit()
    flash(f"{input_type} issued successfully!", "success")
    return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))

@main_bp.route('/plough/<farmer_id>', methods=['POST'])
def plough_land(farmer_id):
    ploughing = Ploughing(farmer_id=farmer_id, date_ploughed=datetime.utcnow())
    db.session.add(ploughing)
    db.session.commit()
    flash("Land ploughed successfully!", "success")
    return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))

@main_bp.route('/plough')
@login_required
def plough_default():
    farmers = Farmer.query.all()
    return render_template('plough_default.html', farmers=farmers)


@main_bp.route('/harvest', methods=['GET', 'POST'])
def record_harvest():
    if request.method == 'POST':
        # Retrieve the primary key of the farmer from the hidden field
        farmer_id = request.form.get('farmer_id')
        if not farmer_id:
            flash("Farmer is not selected. Please search for a farmer first.", "danger")
            return redirect(url_for('main.record_harvest'))

        try:
            kgs_clean = float(request.form.get('kgs_harvested_clean'))
            kgs_husk = float(request.form.get('kgs_harvested_husk'))
        except (ValueError, TypeError):
            flash("Invalid harvest weights! Please enter valid numbers for clean and husk weights.", "danger")
            return redirect(url_for('main.record_harvest'))

        # Calculate the total payment
        total_payment = (kgs_clean * 52) + (kgs_husk * 26)

        # Save the harvest record into the database
        new_harvest = Harvest(
            farmer_id=farmer_id,  # farmer_id here is the primary key of the farmer (an integer)
            clean_kgs=kgs_clean,
            husk_kgs=kgs_husk,
            date_recorded=datetime.utcnow()
        )
        db.session.add(new_harvest)
        db.session.commit()

        flash("Harvest recorded successfully!", "success")
        # Redirect back to the dashboard instead of the payment page
        return redirect(url_for('main.dashboard'))

    # GET: render the harvest form
    return render_template('harvest.html')


# Remove duplicate definitions. Use each route only once.

# Route to fetch farmer details for non-AJAX use (renders a template)
@main_bp.route('/fetch_farmer_details', methods=['POST'])
def fetch_farmer_details():
    search_term = request.form.get('search_term')
    search_type = request.form.get('search_type')

    if search_type == "id":
        # Look up by unique_number (the display ID you use)
        farmer = Farmer.query.filter_by(unique_number=search_term).first()
    elif search_type == "phone":
        farmer = Farmer.query.filter_by(phone_number=search_term).first()
    else:
        farmer = None

    if farmer:
        # Render the harvest form with the farmer details available
        return render_template('harvest.html', farmer=farmer)
    else:
        flash("No farmer found with the provided details.", "warning")
        return redirect(url_for('main.record_harvest'))

# JSON Endpoint to fetch farmer details for AJAX use
@main_bp.route('/fetch_farmer_json', methods=['GET'])
def fetch_farmer_json():
    unique_number = request.args.get('unique_number')
    farmer = Farmer.query.filter_by(unique_number=unique_number).first()
    if farmer:
        return jsonify({
            'success': True,
            'farmer': {
                'unique_number': farmer.unique_number,
                'full_name': farmer.full_name,
                'county': farmer.county,
                'subcounty': farmer.subcounty,
                'ward': farmer.ward,
                'land_size': farmer.land_size,
                'village': farmer.village,
                'phone_number': farmer.phone_number,
                'field_officer': farmer.field_officer
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Farmer not found'}), 404

# New route to update (edit) farmer details via AJAX
@main_bp.route('/edit_farmer', methods=['POST'])
def edit_farmer():
    unique_number = request.form.get('unique_number')
    farmer = Farmer.query.filter_by(unique_number=unique_number).first()
    if not farmer:
        return jsonify({'success': False, 'error': 'Farmer not found'}), 404

    # Update farmer details from the form data
    farmer.full_name = request.form.get('full_name')
    farmer.county = request.form.get('county')
    farmer.subcounty = request.form.get('subcounty')
    farmer.ward = request.form.get('ward')
    farmer.land_size = request.form.get('land_size')
    farmer.village = request.form.get('village')
    farmer.phone_number = request.form.get('phone_number')
    farmer.field_officer = request.form.get('field_officer')
    # Add any additional fields here as needed

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Farmer details updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Update failed, please try again.'})


@main_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        farmer_id = request.form.get('farmer_id')
        payment_method = request.form.get('payment_method')

        # Ensure farmer lookup works correctly
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if not farmer:
            logging.debug(f"Farmer lookup failed for ID: {farmer_id}")
            flash("Farmer not found!", "danger")
            return redirect(url_for('main.payment'))

        # Get harvest records safely
        harvests = Harvest.query.filter_by(farmer_id=farmer.id).all()
        total_clean = sum(h.clean_kgs for h in harvests) if harvests else 0
        total_husk = sum(h.husk_kgs for h in harvests) if harvests else 0

        # Compute the total payment safely
        total_payment = (total_clean * 52) + (total_husk * 26)

        # Validate payment amount before saving
        if total_payment <= 0:
            flash("Invalid payment amount. No harvest records found!", "danger")
            return redirect(url_for('main.payment', farmer_id=farmer_id))

        # Create new payment record with proper error handling
        try:
            new_payment = Payment(
                farmer_id=farmer.id,
                amount_paid=total_payment,
                payment_method=payment_method,
                date_paid=datetime.utcnow()
            )
            db.session.add(new_payment)
            db.session.commit()
            logging.debug(f"Payment successfully saved for farmer {farmer_id}: {total_payment}")
            flash("Payment processed successfully!", "success")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving payment: {e}")
            flash("Failed to process payment! Please try again.", "danger")

        return redirect(url_for('main.dashboard'))  # Redirect to dashboard after payment

    # GET request: Retrieve Farmer Data and Payment Values
    farmer_id = request.args.get('farmer_id')
    farmer = Farmer.query.filter_by(unique_number=farmer_id).first() if farmer_id else None

    # Ensure safe handling of missing farmer records
    total_clean = sum(h.clean_kgs for h in Harvest.query.filter_by(farmer_id=farmer.id)) if farmer else 0
    total_husk = sum(h.husk_kgs for h in Harvest.query.filter_by(farmer_id=farmer.id)) if farmer else 0
    total_payment = (total_clean * 52) + (total_husk * 26) if farmer else 0

    return render_template('payment.html', farmer=farmer, total_clean=total_clean, total_husk=total_husk, total_payment=total_payment)
# Route for issuing manure
@main_bp.route('/issue_manure', methods=['GET', 'POST'])
def issue_manure():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        quantity = request.form['quantity']

        # Logic to find the farmer and issue manure
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if not farmer:
            flash("Farmer not found!", "danger")
            return redirect(url_for('main.issue_manure'))

        # Create a new Manure entry
        new_manure = Manure(farmer_id=farmer.id, quantity=quantity)
        db.session.add(new_manure)
        db.session.commit()
        flash("Manure issued successfully!", "success")
        return redirect(url_for('main.issue_manure'))

    return render_template('issue_manure.html')


@main_bp.route('/export_data', methods=['GET'])
@login_required
def export_data():
    """Render the export data page."""
    # Logic to handle data export
    return render_template('export_data.html')  # Ensure you have an export_data.html template

@main_bp.route('/farmers', methods=['GET'])
@login_required
def farmers():
    farmers_list = Farmer.query.all()
    for farmer in farmers_list:
        last_harvest = Harvest.query.filter_by(farmer_id=farmer.id).order_by(Harvest.date_recorded.desc()).first()
        last_payment = Payment.query.filter_by(farmer_id=farmer.id).order_by(Payment.date_paid.desc()).first()
        farmer.last_harvest_date = last_harvest.date_recorded if last_harvest else None
        farmer.last_payment_date = last_payment.date_paid if last_payment else None
    receipt = session.pop('receipt', None)
    return render_template('farmers.html', farmers=farmers_list, receipt=receipt)

@main_bp.route('/bulk_edit_farmers', methods=['POST'])
def bulk_edit_farmers():
    data = request.get_json()
    ids = data.get('ids')
    new_field_officer = data.get('field_officer')
    if not ids or not new_field_officer:
        return jsonify({'success': False, 'error': 'Missing data.'}), 400
    try:
        farmers = Farmer.query.filter(Farmer.unique_number.in_(ids)).all()
        if not farmers:
            return jsonify({'success': False, 'error': 'No matching farmers found.'}), 404
        for farmer in farmers:
            farmer.field_officer = new_field_officer
        db.session.commit()
        return jsonify({'success': True, 'message': 'Selected farmers updated successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Update failed: ' + str(e)}), 500

@main_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    """Admin can add a new user."""

    if current_user.role != "admin":
        flash("Access Denied: Only Admins Can Add Users", "danger")
        return redirect(url_for('main.dashboard'))  # Unauthorized users redirected

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'user')  # Default role: 'user'

        # Validate input
        if not username or not password:
            flash("Username and Password are required!", "danger")
            return redirect(url_for('main.add_user'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('main.add_user'))

        # Create and save new user
        new_user = User(username=username, role=role)
        new_user.set_password(password)  # Assuming set_password hashes passwords
        db.session.add(new_user)
        db.session.commit()

        flash("New user added successfully!", "success")
        return redirect(url_for('main.manage_users'))  # Redirect to manage users

    return render_template('add_user.html')
@main_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    """Allow only admin users to manage users."""
    if current_user.role != "admin":
        flash("Access Denied: Only Admins Can Manage Users", "danger")
        return redirect(url_for('main.dashboard'))  # Redirect unauthorized users

    try:
        if request.method == 'POST':
            # Get form data
            username = request.form.get('username')
            role = request.form.get('role', 'user')  # Default role: 'user'

            # Validate input
            if not username:
                flash("Username is required!", "danger")
                return redirect(url_for('main.manage_users'))

            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash("Username already exists!", "danger")
                return redirect(url_for('main.manage_users'))

            # Create new user
            new_user = User(username=username, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash("User added successfully!", "success")
            return redirect(url_for('main.manage_users'))  # Refresh page

        # GET: Fetch all users
        users = User.query.all()
        return render_template('manage_users.html', users=users)

    except Exception as e:
        print(f"Error managing users: {e}")
        flash("An error occurred while managing users.", "danger")
        return redirect(url_for("main.dashboard"))  # Redirect on error


@main_bp.route('/farmers_page', methods=['GET'])
def farmers_page():
    # Get the page number from query parameters; default is 1
    page = request.args.get('page', 1, type=int)
    per_page = 25  # Adjust as needed

    # Build the pagination object
    pagination = Farmer.query.order_by(Farmer.id).paginate(page=page, per_page=per_page, error_out=False)
    farmers = pagination.items

    # Note: Also pass receipt if it exists.
    receipt = ... # your receipt, if applicable

    return render_template('farmers.html', farmers=farmers, pagination=pagination, receipt=receipt)


@main_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    pass  # Implement edit functionality

@main_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    pass  # Implement delete functionality

@main_bp.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    # Your logic for adding an employee
    return render_template('add_employee.html')

@main_bp.route('/employee', methods=['GET'])
def employee():
    # Your logic for displaying employee information
    return render_template('employee.html')

@main_bp.route('/profile')
@login_required
def profile():
    # Retrieve profile or user data as needed.
    return render_template('profile.html')


@main_bp.route('/payroll')
def payroll():
    # Retrieve payroll records from the database.
    # For example, order by creation date (assuming Payroll has a date_created field)
    payroll_entries = Payroll.query.order_by(Payroll.date_created.desc()).all()

    # Optionally flash a message if no records are found
    if not payroll_entries:
        flash("No payroll records found.", "info")

    # Render the payroll template passing the records
    return render_template('payroll.html', payroll_entries=payroll_entries)
# Route to view PDF
@main_bp.route('/view_pdf')
@login_required
def view_pdf():
    return render_template('view_pdf.html')


# Route for posting updates
@main_bp.route('/post_update', methods=['GET', 'POST'])
@login_required
def post_update():
    form = PostUpdateForm()
    if form.validate_on_submit():
        new_update = Update(title=form.title.data, content=form.content.data)
        db.session.add(new_update)
        db.session.commit()
        flash("New update posted successfully!", "success")
        return redirect(url_for('main.dashboard'))
    return render_template('post_update.html', form=form)

# ALLOWED_EXTENSIONS remains the same
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpeg', 'jpg', 'xls', 'xlsx'}

# Define the allowed file check function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize the S3 client using your Cloudflare R2 configuration
s3 = boto3.client(
    "s3",
    endpoint_url=Config.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
)


def allowed_file(filename):
    """
    Check if the file extension is allowed based on configuration.
    """
    allowed_extensions = Config.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def upload_to_s3(file_path, bucket_name, s3_key):
    """
    Upload a single file to the S3 bucket.

    Args:
        file_path (str): The local path to the file being uploaded.
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key (path) under which the file will be stored in the bucket.

    Returns:
        bool: True if the upload succeeds, False otherwise.
    """
    try:
        # Upload the file to the specified S3 bucket
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Successfully uploaded '{s3_key}' to bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        # Log detailed error message
        error_message = f"Error uploading '{s3_key}' to S3: {str(e)}"
        print(error_message)
        flash(error_message, "danger")
        return False
    except FileNotFoundError:
        # Handle cases where the file does not exist
        error_message = f"File '{file_path}' not found. Please check the file path."
        print(error_message)
        flash(error_message, "danger")
        return False
    except Exception as e:
        # Catch-all for unexpected exceptions
        error_message = f"Unexpected error occurred during upload: {str(e)}"
        print(error_message)
        flash(error_message, "danger")
        return False


@main_bp.route('/downloads/<path:filename>')
@login_required
def download_file(filename):
    """
    Route to download files from S3 as attachments.
    Handles errors gracefully and redirects users if an issue occurs.
    """
    try:
        file_obj = io.BytesIO()
        s3.download_fileobj(Config.AWS_STORAGE_BUCKET_NAME, filename, file_obj)
        file_obj.seek(0)  # Reset the file pointer
        return send_file(file_obj, download_name=filename, as_attachment=True)
    except Exception as e:
        flash(f"Error retrieving file: {str(e)}", "danger")
        return redirect(url_for('main.dashboard'))


@main_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    """
    Route to display uploaded files inline (e.g., PDFs and images).
    Determines MIME type dynamically based on file extension.
    """
    try:
        file_obj = io.BytesIO()
        s3.download_fileobj(Config.AWS_STORAGE_BUCKET_NAME, filename, file_obj)
        file_obj.seek(0)

        # Determine MIME type based on file extension
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ""
        mimetypes = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }
        mimetype = mimetypes.get(ext, "application/octet-stream")

        # Serve file for inline display
        return send_file(file_obj, mimetype=mimetype, as_attachment=False)
    except Exception as e:
        flash(f"Error displaying file: {str(e)}", "danger")
        return redirect(url_for('main.dashboard'))


@main_bp.route('/documents')
@login_required
def documents():
    """
    Route to list all uploaded documents directly from S3.
    """
    try:
        # List all objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=Config.AWS_STORAGE_BUCKET_NAME)
        files = []

        # Extract the file names (keys) from the response
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]

        if not files:
            flash("No documents found in the cloud.", "info")

        return render_template("documents.html", files=files)

    except Exception as e:
        flash(f"Error retrieving files from the cloud: {str(e)}", "danger")
        return redirect(url_for('main.dashboard'))


@main_bp.route('/upload_data', methods=['POST'], endpoint='upload_data')
@login_required
def upload_data():
    """
    Handles admin file uploads and automatically uploads them to the S3 bucket.
    """
    if not current_user.is_admin:
        flash("Admin access only", "danger")
        return redirect(url_for('main.dashboard'))

    if 'files' not in request.files:
        flash("No file part in the request.", "danger")
        return redirect(url_for('main.dashboard'))

    files = request.files.getlist('files')

    for file in files:
        if file and allowed_file(file.filename):
            # Secure and save the filename
            filename = secure_filename(file.filename)
            s3_key = filename  # You can add additional folder structure logic here if needed

            try:
                # Upload file to S3
                s3.upload_fileobj(file, Config.AWS_STORAGE_BUCKET_NAME, s3_key)
                flash(f"'{filename}' uploaded successfully!", "success")
            except Exception as e:
                flash(f"Error uploading '{filename}': {str(e)}", "danger")
        else:
            flash(f"File type not allowed: {file.filename}", "danger")

    # Redirect back to the dashboard
    return redirect(url_for('main.dashboard'))

@main_bp.route('/delete_file/<path:filename>', methods=['POST'])
@login_required
def delete_file(filename):
    """
    Route to delete a specific file from the S3 bucket.
    Only accessible by admin users.
    """
    if not current_user.is_admin:
        flash("Admin access only", "danger")
        return redirect(url_for('main.dashboard'))

    try:
        # Delete the file from the S3 bucket
        s3.delete_object(Bucket=Config.AWS_STORAGE_BUCKET_NAME, Key=filename)
        flash(f"Successfully deleted '{filename}' from the cloud.", "success")
    except ClientError as e:
        flash(f"Error deleting '{filename}': {str(e)}", "danger")
    except Exception as e:
        flash(f"Unexpected error occurred: {str(e)}", "danger")

    return redirect(url_for('main.dashboard'))


@main_bp.route('/post_update', methods=['POST'], endpoint='post_update_v1')
@login_required
def post_update():
    """
    Route to save admin updates and announcements to the database.
    """
    if not current_user.is_admin:
        flash("Admin access only", "danger")
        return redirect(url_for('main.dashboard'))

    content_type = request.form.get('content_type')  # E.g., 'update', 'memo', 'advertisement'
    content = request.form.get('content')

    if content_type and content:
        new_content = AdminContent(content_type=content_type, content=content)
        db.session.add(new_content)
        db.session.commit()
        flash(f"{content_type.capitalize()} added successfully!", "success")
    else:
        flash("Failed to post update. Please provide valid content.", "danger")

    return redirect(url_for('main.dashboard'))

@main_bp.route('/delete_farmers', methods=['POST'])
def delete_farmers():
    data = request.get_json()
    farmer_ids = data.get("farmer_ids")

    if not farmer_ids:
        logging.debug("No farmer IDs provided in request.")
        return jsonify({"error": "No farmers selected"}), 400

    farmers_to_delete = Farmer.query.filter(Farmer.unique_number.in_(farmer_ids)).all()

    if not farmers_to_delete:
        logging.debug(f"No matching farmers found for IDs: {farmer_ids}")
        return jsonify({"error": "No matching farmers found"}), 404

    try:
        for farmer in farmers_to_delete:
            logging.debug(f"Deleting farmer: {farmer.unique_number}")
            db.session.delete(farmer)
        db.session.commit()
        logging.info(f"Deleted {len(farmers_to_delete)} farmers successfully.")
        return jsonify({"message": f"{len(farmers_to_delete)} farmers deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.exception("Error occurred while deleting farmers:")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route('/farmers/<season>')
def filter_farmers(season):
    valid_seasons = ["OND", "MAM"]
    if season not in valid_seasons:
        return jsonify({"error": "Invalid season filter"}), 400

    farmers = Farmer.query.filter_by(season=season).all()

    return jsonify([{
        "Farmer ID": farmer.unique_number,
        "Name": farmer.full_name,
        "Season": farmer.season
    } for farmer in farmers])

@main_bp.route('/export_quick_summary_excel')
def export_quick_summary_excel():
    # Query all farmers
    farmers = Farmer.query.all()

    # Create a list of dictionaries with only the quick summary fields.
    data = []
    for farmer in farmers:
        data.append({
            "Farmer Name": farmer.full_name,
            "County": farmer.county,
            "Subcounty": farmer.subcounty,
            "Ward": farmer.ward,
            "Acres": farmer.land_size,
            "Village": farmer.village,
            "Field Officer": farmer.field_officer,
            "Phone Number": farmer.phone_number,
        })

    # Convert the data into a pandas DataFrame.
    df = pd.DataFrame(data)

    # Write the DataFrame to an Excel file in memory.
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Quick Summary')
    output.seek(0)

    # Return the Excel file as an attachment.
    return send_file(
        output,
        as_attachment=True,
        download_name="quick_summary.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@main_bp.route('/export_farmers_excel')
def export_farmers_excel():
    # Query all farmers
    farmers = Farmer.query.all()

    # Create a list of dictionaries with detailed fields.
    data = []
    for farmer in farmers:
        data.append({
            "Farmer ID": farmer.unique_number,
            "Name": farmer.full_name,
            "County": farmer.county,
            "Subcounty": farmer.subcounty,
            "Ward": farmer.ward,
            "Location": farmer.location,
            "Phone Number": farmer.phone_number,
            "Village": farmer.village,
            "Land Size (acres)": farmer.land_size,
            "Season": farmer.season,
            "Fertilizer Type": farmer.fertilizer_type or "N/A",
            "Kgs Issued": farmer.kgs_issued or "N/A",
            "Kgs Harvested (Clean)": farmer.kgs_harvested_clean or "N/A",
            "Kgs Harvested (Husk)": farmer.kgs_harvested_husk or "N/A",
            "Total Payment": (farmer.kgs_harvested_clean or 0) * 52 + (farmer.kgs_harvested_husk or 0) * 26,
            "Amount Received": farmer.amount_received or "N/A",
            "Last Harvest Date": farmer.last_harvest_date.strftime("%Y-%m-%d") if farmer.last_harvest_date else "N/A",
            "Last Payment Date": farmer.last_payment_date.strftime("%Y-%m-%d") if farmer.last_payment_date else "N/A",
            "Field Officer": farmer.field_officer,
        })

    # Convert the data into a pandas DataFrame.
    df = pd.DataFrame(data)

    # Write the DataFrame to an Excel file in memory.
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Detailed Farmers')
    output.seek(0)

    # Return the Excel file as an attachment.
    return send_file(
        output,
        as_attachment=True,
        download_name="detailed_farmers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@main_bp.route('/data_analysis')
def data_analysis():
    farmers = Farmer.query.all()
    total_farmers = len(farmers)
    average_land_size = sum(f.land_size for f in farmers if f.land_size) / total_farmers if total_farmers else 0
    unique_field_officers = len(set(f.field_officer for f in farmers if f.field_officer))

    # Create statistics per field officer
    fe_stats = {}
    for f in farmers:
        if f.field_officer:
            if f.field_officer not in fe_stats:
                fe_stats[f.field_officer] = {'total_farmers': 0, 'total_acres': 0}
            fe_stats[f.field_officer]['total_farmers'] += 1
            fe_stats[f.field_officer]['total_acres'] += f.land_size

    field_officer_stats = [
        {'field_officer': key, 'total_farmers': value['total_farmers'], 'total_acres': value['total_acres']} for
        key, value in fe_stats.items()]

    # Prepare chart data for counties, seasons, and land sizes (existing code) ...
    counties = {}
    seasons = {"OND": 0, "MAM": 0}
    land_sizes = []
    for farmer in farmers:
        counties[farmer.county] = counties.get(farmer.county, 0) + 1
        if farmer.season in seasons:
            seasons[farmer.season] += 1
        land_sizes.append(farmer.land_size)
    counties_labels = list(counties.keys())
    counties_values = list(counties.values())
    seasons_labels = list(seasons.keys())
    seasons_values = list(seasons.values())
    land_size_labels = sorted(set(land_sizes))
    land_size_values = [land_sizes.count(size) for size in land_size_labels]

    return render_template("data_analysis.html",
                           total_farmers=total_farmers,
                           average_land_size=average_land_size,
                           unique_field_officers=unique_field_officers,
                           counties_labels=counties_labels,
                           counties_values=counties_values,
                           seasons_labels=seasons_labels,
                           seasons_values=seasons_values,
                           land_size_labels=land_size_labels,
                           land_size_values=land_size_values,
                           field_officer_stats=field_officer_stats
                           )

@main_bp.route('/payment_receipt', methods=['GET'])
def payment_receipt():
    # Retrieve the receipt as needed.
    receipt = ...  # Your logic to get the receipt.
    return render_template('payment_receipt.html', receipt=receipt)
@main_bp.route('/farmers_quick_summary', methods=['GET'])
def farmers_quick_summary():
    # Optionally use pagination if you expect many records; here we assume a quick summary only loads a subset.
    page = request.args.get('page', 1, type=int)
    per_page = 1000
    pagination = Farmer.query.order_by(Farmer.id).paginate(page=page, per_page=per_page, error_out=False)
    farmers = pagination.items
    return render_template('farmers_quick_summary.html', farmers=farmers, pagination=pagination)
@main_bp.route('/farmers_detailed', methods=['GET'])
def farmers_detailed():
    page = request.args.get('page', 1, type=int)
    per_page = 25  # Adjust per your needs.
    pagination = Farmer.query.order_by(Farmer.id).paginate(page=page, per_page=per_page, error_out=False)
    farmers_list = pagination.items
    return render_template('farmers_detailed.html', farmers=farmers_list, pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)
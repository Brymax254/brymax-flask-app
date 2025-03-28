import pandas as pd
import requests
from flask import render_template, current_app, flash, redirect, session, url_for, jsonify, request, make_response, Blueprint, send_from_directory
from datetime import datetime, date
import logging
from io import StringIO
import plotly.express as px
from pdfkit import pdfkit
from app.models import Report, DailyReport, Update, Employee, Payroll, User, Payroll, Goal, Course, Attendance, Farmer, InputDistribution, Ploughing, Harvest, Payment, Seed, Pesticide, Manure
from app import db
from app.forms import AddEmployeeForm, ProfileForm, GoalForm, CourseForm
from flask_login import login_required, current_user, login_user, logout_user
from app.utils import generate_farmer_id, admin_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from .forms import PostUpdateForm
# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize blueprints
main_bp = Blueprint('main', __name__)
employee_bp = Blueprint('employee', __name__)

auth_bp = Blueprint("auth", __name__)


import logging

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
    logout_user()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

@main_bp.route('/')
def index():
    return redirect(url_for('auth.login'))  # Redirect to login

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


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # For example, fetch all farmers from the database
    farmers = Farmer.query.all()
    farmer = farmers[0] if farmers else None

    # Get files from the UPLOAD_FOLDER
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    files = []
    if upload_folder and os.path.exists(upload_folder):
        # List all files (ignoring hidden files)
        files = [f for f in os.listdir(upload_folder) if not f.startswith('.')]
        if not files:
            flash("No documents found in the uploads folder.", "warning")
    else:
        flash("Uploads folder not found or not configured.", "danger")

    return render_template(
        'dashboard.html',
        active_sidebar='dashboard',
        farmers=farmers,
        farmer=farmer,
        files=files
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

        # Aggregate trends data (e.g., monthly or weekly)
        trends_data = db.session.query(
            DailyReport.officer_name,
            db.func.strftime('%Y-%m', DailyReport.report_date).label('month'),
            db.func.sum(DailyReport.farmers_registered).label("monthly_farmers"),
            db.func.sum(DailyReport.acres_ploughed).label("monthly_acres")
        ).group_by(DailyReport.officer_name, db.func.strftime('%Y-%m', DailyReport.report_date)).all()

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
        phone_number = request.form['phone_number']
        existing_farmer = Farmer.query.filter_by(phone_number=phone_number).first()
        if existing_farmer:
            flash("Phone number already registered!", "warning")
            return redirect(url_for('main.register_farmer'))
        try:
            land_size = float(request.form['land_size'])
        except ValueError:
            flash("Invalid land size! Please enter a valid number.", "danger")
            return redirect(url_for('main.register_farmer'))
        season = request.form['season']
        year = datetime.now().year
        farmer_id, farmer_number = generate_farmer_id(season, year)
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
            farmer_number=farmer_number
        )
        db.session.add(farmer)
        db.session.commit()
        flash("Farmer registered successfully!", "success")
        return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))
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


# Route for recording a harvest for a specific farmer
@main_bp.route('/harvest/<farmer_id>', methods=['POST'])
def record_specific_harvest(farmer_id):
    try:
        clean_kgs = float(request.form['clean_kgs'])
        husk_kgs = float(request.form['husk_kgs'])
    except ValueError:
        flash("Invalid harvest weight! Please enter valid numbers.", "danger")
        return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))

    harvest = Harvest(farmer_id=farmer_id, clean_kgs=clean_kgs, husk_kgs=husk_kgs, date_recorded=datetime.utcnow())
    db.session.add(harvest)
    db.session.commit()
    flash("Harvest recorded successfully!", "success")
    return redirect(url_for('main.fetch_farmer', farmer_id=farmer_id))


# Route for rendering the harvest form
@main_bp.route('/harvest', methods=['GET', 'POST'])
def record_harvest():
    if request.method == 'POST':
        farmer_id = request.form.get('farmer_id')
        try:
            kgs_clean = float(request.form['kgs_harvested_clean'])
            kgs_husk = float(request.form['kgs_harvested_husk'])
        except ValueError:
            flash("Invalid harvest weights! Please enter valid numbers for clean and husk weights.", "danger")
            return redirect(url_for('main.record_harvest'))

        # Calculate the total payment
        total_payment = (kgs_clean * 52) + (kgs_husk * 26)

        # Save the harvest record into the database (adjust field names if needed)
        new_harvest = Harvest(
            farmer_id=farmer_id,
            clean_kgs=kgs_clean,
            husk_kgs=kgs_husk,
            date_recorded=datetime.utcnow()
        )
        db.session.add(new_harvest)
        db.session.commit()

        flash("Harvest recorded successfully!", "success")
        # Redirect to the payment page with farmer_id and total_payment as query parameters
        return redirect(url_for('main.payment', farmer_id=farmer_id, total_payment=total_payment))

    # For GET requests, render the harvest form
    return render_template('harvest.html')


@main_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Retrieve form data
        farmer_id = request.form.get('farmer_id')
        payment_method = request.form.get('payment_method')

        # Fetch the farmer record using unique_number
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if not farmer:
            flash("Farmer not found!", "danger")
            return redirect(url_for('main.dashboard'))

        # Calculate totals from harvest records
        harvests = Harvest.query.filter_by(farmer_id=farmer_id).all()
        total_clean = sum(h.clean_kgs for h in harvests) if harvests else 0
        total_husk = sum(h.husk_kgs for h in harvests) if harvests else 0
        total_payment = (total_clean * 52) + (total_husk * 26)

        # Record the payment in the Payment table
        new_payment = Payment(
            farmer_id=farmer.id,
            amount_paid=total_payment,
            date_paid=datetime.utcnow()
        )
        db.session.add(new_payment)
        db.session.commit()

        # Optionally, update farmer's last_payment_date
        farmer.last_payment_date = new_payment.date_paid
        db.session.commit()

        # Generate a receipt dictionary with only serializable data
        receipt = {
            'receipt_number': f'R{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
            'date': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            'farmer': {
                'full_name': farmer.full_name,
                'unique_number': farmer.unique_number,
                'phone_number': farmer.phone_number
            },
            'total_clean': total_clean,
            'total_husk': total_husk,
            'total_payment': total_payment,
            'payment_method': payment_method,
        }

        flash("Payment processed successfully!", "success")
        # Redirect to the Farmers page to display updated data and receipt
        # You might choose to pass the receipt via session or query parameters.
        # For example, here we'll assume you're storing it in the session:
        session['receipt'] = receipt
        return redirect(url_for('main.farmers'))

    # GET: Render payment form if needed
    farmer_id = request.args.get('farmer_id')
    total_clean = request.args.get('total_clean', type=float)
    total_husk = request.args.get('total_husk', type=float)
    total_payment = request.args.get('total_payment', type=float)
    farmer = Farmer.query.filter_by(unique_number=farmer_id).first() if farmer_id else None
    return render_template('payment.html', farmer_id=farmer_id,
                           total_clean=total_clean,
                           total_husk=total_husk,
                           total_payment=total_payment,
                           farmer=farmer)


@main_bp.route('/issue_fertilizer', methods=['GET', 'POST'])
def issue_fertilizer():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        fertilizer_type = request.form['fertilizer_type']
        try:
            kgs_issued = float(request.form['kgs_issued'])  # Ensure this field is present
        except KeyError:
            flash("Kgs issued is required.", "danger")
            return redirect(url_for('main.issue_fertilizer'))
        except ValueError:
            flash("Invalid value for kgs issued.", "danger")
            return redirect(url_for('main.issue_fertilizer'))

        amount_received = request.form.get('amount_received', 0)  # Use get to avoid KeyError

        # Fetch the farmer from the database
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if farmer:
            farmer.fertilizer_type = fertilizer_type
            farmer.kgs_issued = kgs_issued
            farmer.amount_received = float(amount_received)
            db.session.commit()
            flash("Fertilizer issued successfully!", "success")
        else:
            flash("Farmer not found!", "danger")

        return redirect(url_for('main.farmers'))  # Redirect to the farmers page

    # If GET request, render the issue fertilizer form
    return render_template('issue_fertilizer.html')

# Route for issuing seeds
@main_bp.route('/issue_seeds', methods=['GET', 'POST'])
def issue_seeds():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        seed_type = request.form['seed_type']
        quantity = request.form['quantity']

        # Logic to find the farmer and issue seeds
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if not farmer:
            flash("Farmer not found!", "danger")
            return redirect(url_for('main.issue_seeds'))

        # Create a new Seed entry
        new_seed = Seed(farmer_id=farmer.id, seed_type=seed_type, quantity=quantity)
        db.session.add(new_seed)
        db.session.commit()
        flash("Seeds issued successfully!", "success")
        return redirect(url_for('main.issue_seeds'))

    return render_template('issue_seeds.html')

# Route for issuing pesticides
@main_bp.route('/issue_pesticides', methods=['GET', 'POST'])
def issue_pesticides():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        pesticide_type = request.form['pesticide_type']
        quantity = request.form['quantity']

        # Logic to find the farmer and issue pesticides
        farmer = Farmer.query.filter_by(unique_number=farmer_id).first()
        if not farmer:
            flash("Farmer not found!", "danger")
            return redirect(url_for('main.issue_pesticides'))

        # Create a new Pesticide entry
        new_pesticide = Pesticide(farmer_id=farmer.id, pesticide_type=pesticide_type, quantity=quantity)
        db.session.add(new_pesticide)
        db.session.commit()
        flash("Pesticides issued successfully!", "success")
        return redirect(url_for('main.issue_pesticides'))

    return render_template('issue_pesticides.html')
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

# Route to upload data (restricted to admins)
@main_bp.route('/upload_data', methods=['POST'])
@login_required
def upload_data():
    if not current_user.is_admin:
        flash("Admin access only", "danger")
        return redirect(url_for('main.dashboard'))

    if 'files' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('main.dashboard'))

    files = request.files.getlist('files')

    # Access upload folder inside the route to avoid the context error
    upload_folder = current_app.config.get('UPLOAD_FOLDER')

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
        else:
            flash(f"File type not allowed: {file.filename}", "danger")
            return redirect(url_for('main.dashboard'))

    flash("Files uploaded successfully", "success")
    return redirect(url_for('main.dashboard'))
# Route to serve uploaded files
@main_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    full_path = os.path.join(upload_folder, filename)
    if os.path.exists(full_path):
        return send_from_directory(upload_folder, filename)
    else:
        return f"File not found: {full_path}", 404


# Route to list all documents in the uploads folder
@main_bp.route('/documents')
@login_required
def documents():
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder or not os.path.exists(upload_folder):
        flash("Uploads folder not found.", "danger")
        return redirect(url_for('main.dashboard'))

    # List all files (filtering out hidden files)
    all_files = [f for f in os.listdir(upload_folder) if not f.startswith('.')]
    return render_template("documents.html", files=all_files)
if __name__ == '__main__':
    app.run(debug=True)
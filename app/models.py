from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from datetime import datetime, date
from sqlalchemy import Sequence

# ---------------------------
# User Model (Authentication)
# ---------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # Roles: 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"

    @property
    def is_admin(self):
        return self.role == "admin"  # Returns True if user role is "admin"

# ---------------------------
# Profile & Employee Models
# ---------------------------
class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    bio = db.Column(db.Text)
    # Additional Profile fields

    def __repr__(self):
        return f"<Profile {self.id}>"

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)  # Using "full_name" for clarity
    position = db.Column(db.String(100), nullable=False)
    # Relationships:
    profile = db.relationship('Profile', backref='employee', uselist=False, cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='employee', lazy=True, cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee {self.full_name}>"

# ---------------------------
# Employee Management Models
# ---------------------------
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    def __repr__(self):
        return f"<Goal {self.description[:20]}>"

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.DateTime, default=datetime.utcnow)
    check_out = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    def __repr__(self):
        return f"<Attendance {self.check_in}>"

# ---------------------------
# Agricultural Management Models
# ---------------------------
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False)
    officer_name = db.Column(db.String(100), nullable=False)
    farmers_registered = db.Column(db.Integer, nullable=False)
    total_acres = db.Column(db.Float, nullable=False)
    staff_attendance = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Report {self.id} - {self.officer_name}>"


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    unique_number = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    county = db.Column(db.String(50), nullable=False)
    subcounty = db.Column(db.String(50), nullable=False)
    ward = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    village = db.Column(db.String(50), nullable=False)
    land_size = db.Column(db.Float, nullable=False)
    season = db.Column(db.String(3), nullable=False)  # "OND" or "MAM"
    year = db.Column(db.Integer, nullable=False)
    farmer_number = db.Column(db.Integer, nullable=False)
    fertilizer_type = db.Column(db.String(100), nullable=True)
    kgs_issued = db.Column(db.Float, nullable=True)
    kgs_harvested_clean = db.Column(db.Float, nullable=True)
    kgs_harvested_husk = db.Column(db.Float, nullable=True)
    amount_received = db.Column(db.Float, nullable=True)

    # Newly added fields:
    last_harvest_date = db.Column(db.DateTime, nullable=True)
    last_payment_date = db.Column(db.DateTime, nullable=True)
    field_officer = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Farmer {self.full_name} - {self.phone_number}>"
class InputDistribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    input_type = db.Column(db.String(50), nullable=False)  # Fertilizer/Manure/Seeds/Pesticides
    date_given = db.Column(db.DateTime, default=datetime.utcnow)
    farmer = db.relationship('Farmer', backref='inputs')

    def __repr__(self):
        return f"<Input {self.input_type} - {self.date_given}>"

class Ploughing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    date_ploughed = db.Column(db.DateTime, default=datetime.utcnow)
    farmer = db.relationship('Farmer', backref='ploughing_records')

    def __repr__(self):
        return f"<Ploughing {self.date_ploughed}>"

from datetime import datetime
from app import db

class Harvest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    clean_kgs = db.Column(db.Float, nullable=False)
    husk_kgs = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    farmer = db.relationship('Farmer', backref='harvests')

    def __repr__(self):
        return f"<Harvest {self.clean_kgs} kgs>"


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Explicitly enable autoincrement
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    date_paid = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    farmer = db.relationship('Farmer', backref='payments')

    def __repr__(self):
        return f"<Payment {self.amount_paid} via {self.payment_method}>"

class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    seed_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    farmer = db.relationship('Farmer', backref='seeds')

    def __repr__(self):
        return f"<Seed {self.seed_type}>"

class Pesticide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    pesticide_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    farmer = db.relationship('Farmer', backref='pesticides')

    def __repr__(self):
        return f"<Pesticide {self.pesticide_type}>"

class Manure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    farmer = db.relationship('Farmer', backref='manure')

    def __repr__(self):
        return f"<Manure {self.quantity} kg>"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Course {self.name}>"

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payroll {self.amount}>"


class Update(db.Model):
    __tablename__ = "updates"
    id = db.Column(db.Integer, Sequence('updates_id_seq'), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Update {self.title}>"


class DailyReport(db.Model):
    __tablename__ = 'daily_reports'

    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    officer_name = db.Column(db.String(120), nullable=False)
    farmers_registered = db.Column(db.Integer, nullable=False)
    total_acres = db.Column(db.Float, nullable=False)
    tractors_in_area = db.Column(db.Integer, nullable=True)
    acres_ploughed = db.Column(db.Float, nullable=True)
    staff_attendance = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<DailyReport {self.report_date} - {self.officer_name}>"

    from app.extensions import db
class AdminContent(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     content_type = db.Column(db.String(50), nullable=False)  # 'update', 'memo', 'advertisement'
     content = db.Column(db.Text, nullable=False)
     created_at = db.Column(db.DateTime, default=db.func.now())

     def __repr__(self):
         return f"<AdminContent {self.content_type}>"




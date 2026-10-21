from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify,make_response, Response,current_app,abort,Blueprint,send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import csv
from wtforms.fields import StringField, PasswordField, SubmitField,SelectField, BooleanField,DateField,TextAreaField,FileField,DecimalField, IntegerField
import re
from wtforms.validators import DataRequired, Email, Length, ValidationError, NumberRange,UsernameAndDateForm,EqualTo
from werkzeug.routing import BaseConverter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,date, timedelta, timezone,time as dt_time
from pandas import read_frame
import cv2,os,dlib
import imutils
from imutils import face_utils
from imutils.face_utils import FaceAligner
from imutils.video import VideoStream
import face_recognition
from flask_migrate import Migrate
import time
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
import logging
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from face_recognition.face_recognition_cli import image_files_in_folder
import pickle
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import text, or_, and_, extract, func, case,desc
from sqlalchemy.exc import SQLAlchemyError
from sklearn.svm import SVC
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import seaborn as sns
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from matplotlib import rcParams
import math
from flask_mail import Mail, Message as MailMessage
from xhtml2pdf import pisa
from io import BytesIO
from geopy.distance import geodesic
from scipy.spatial import distance as dist
from skimage.feature import local_binary_pattern, hog
import calendar
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin,CORS
import json 
import threading
from threading import Thread,Lock
import click
import shutil
from pathlib import Path
from queue import Queue
from functools import lru_cache
import sqlite3
import uuid
import traceback
from sqlalchemy import and_
import psutil
from logging.handlers import RotatingFileHandler
#from flask_reuploaded import UploadSet, configure_uploads, IMAGES
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
import binascii
import random
from io import StringIO
from dateutil.relativedelta import relativedelta


mpl.use('Agg')
settings_bp = Blueprint('settings', __name__)

# Initialize global variables

class DateConverter(BaseConverter):
    """Convert URL parameter to date object"""
    def to_python(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')

# Assuming you're using SQLAlchemy for database operations

app = Flask(__name__) 
app.secret_key = '#####'
socketio = SocketIO(app)  # Initialize SocketIO
db_path = r"C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\instance\site.db"

# Construct the SQLAlchemy database URI using the absolute path
# Note the four forward slashes for an absolute path on Windows
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")
TWILIO_ACCOUNT_SID = 'AC676f2bfef4528a51f14fa316424dd1d5'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = '3e217dffe7bfb277fb03e26bee611bc8'    # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = '+251982431755'
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the workplace GPS coordinates (latitude, longitude)
WORKPLACE_COORDINATES = (9.3142, 42.1216)  # Example: Haramaya University coordinates
ALLOWED_RADIUS = 100
# Define the list of authorized IP addresses
AUTHORIZED_IPS = [
    '197.154.189.0/24',  # Haramaya University's public IP range
    '192.168.1.1',        # Example private IP (internal network)
    '127.0.0.1' ,
    '192.168.137.169'# Localhost (for testing)
]

WORKING_HOURS = (dt_time(8, 0), dt_time(17, 0))

def validate_time():
    now = datetime.now().time()
    return WORKING_HOURS[0] <= now <= WORKING_HOURS[1]
UPLOAD_FOLDER = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\recognition\static\uploeds'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['TRAINING_DATASET_PATH'] = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\face_recognition_data\training_dataset'
app.url_map.converters['date'] = DateConverter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_present_column():
    with db.engine.connect() as connection:
        connection.execute(text("ALTER TABLE present ADD COLUMN present BOOLEAN NOT NULL DEFAULT 0"))
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employees = db.relationship('User', back_populates='department')
    employees_data = db.relationship('Employee', back_populates='department')
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    employee_id = db.Column(db.String(100), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.Text, nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    employee_type = db.Column(db.String(50), nullable=False)
    date_of_joining = db.Column(db.Date, nullable=False)
    salary_structure = db.Column(db.String(100))
    salary_structure_name = db.Column(db.String(100), nullable=True)
    bank_account_details = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50))
    tax_id = db.Column(db.String(50))
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    face_encoding = db.Column(db.Text)
    photo_path = db.Column(db.String(200))
    fingerprint_data = db.Column(db.Text)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'),nullable=True)
    department = db.relationship('Department', back_populates='employees')

    employee_profile = db.relationship('Employee', back_populates='user', uselist=False)
    payroll_records = db.relationship('Payroll', back_populates='user')
    attendance_records = db.relationship('Attendance', back_populates='user')
    time_entries = db.relationship('Time', back_populates='user')
    presents = db.relationship('Present', back_populates='user')
    leave_requests = db.relationship('LeaveRequest', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user')

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    employee_type = db.Column(db.String(50), nullable=False)
    date_of_joining = db.Column(db.Date, nullable=False)
    salary_structure = db.Column(db.String(50))
    bank_account_details = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    is_registered = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('User', back_populates='employee_profile')
    department = db.relationship('Department', back_populates='employees_data')
# Other models remain unchanged but should import and use the 'users.id' FK correctly
# Example for Attendance:
class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=False, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    present = db.Column(db.Boolean, default=False)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    hours = db.Column(db.Float)
    break_hours = db.Column(db.Float)
    days_worked = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Float, default=0.0)
    absences = db.Column(db.Integer, default=0)
    month_year = db.Column(db.Date, nullable=False)
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    confidence = db.Column(db.Float)
    late_check = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='attendance_records')

    def __repr__(self):
        return f'<Attendance {self.user_id} on {self.date}>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Use Session.get()
    # Add methods for password hashing and verification
#.utcnow


def create_tables():
    db.create_all()
    
@app.cli.command('init-db')
def init_db_command():
    """Initializes the database."""
    db.create_all()
    print('Initialized the database.')
@app.before_request
def initialize():
    create_tables()
    create_admin()
@app.before_request
def create_admin():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            employee_id='ADMIN001',  # Provide a default employee ID for the admin
            email='geddikriss@gmail.com',
            dob=datetime(2000, 1, 1),  # Provide a default date of birth
            gender='Male',  
            contact_number='+251912345678',  
            address='Haramaya University',  
            department='Administration', 
            designation='Administrator',  
            employee_type='Permanent',  
            date_of_joining=datetime(2025, 1, 1), 
            salary_structure='80000', 
            bank_account_details='commercail bank of ethiopia',  
            account_number='10004328786658',
            photo_path='default.jpg',
            

            is_admin=True
        )
        admin.set_password('4567')  
        db.session.add(admin)
        db.session.commit()
        
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    generated_by = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Report {self.name}>"
    

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default='normal')

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='messages_received')

    

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
class Present(db.Model):
    __tablename__ = 'presents'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    present = db.Column(db.Boolean, nullable=False)  # Added the 'present' column
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='presents')
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    clock_in = db.Column(db.Time)  # Changed from check_in
    clock_out = db.Column(db.Time)
    
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    
class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    permission_type = db.Column(db.String(50), nullable=False)
    permission_reason = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='user_permissions')
    employee = db.relationship('Employee', backref='permissions')
class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)


class AddEmployeeForm(FlaskForm):
    username = StringField('Employee ID', validators=[DataRequired(), Length(min=2, max=80)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    # FileField for photo will be handled separately by Flask-Uploads
    submit = SubmitField('Add Employee')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # e.g., Sick Leave, Vacation
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='leave_requests')

class Payroll(db.Model):
    __tablename__ = 'payrolls'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, default=0.0)
    bonuses = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_pay = db.Column(db.Float, nullable=False)
    pay_period = db.Column(db.Date, nullable=False)
    performance_rating = db.Column(db.String(50))
    tax_amount = db.Column(db.Float, default=0.0)
    absence_penalty = db.Column(db.Float, default=0.0)
    late_penalty = db.Column(db.Float, default=0.0)
    performance_bonus = db.Column(db.Float, default=0.0)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    month = db.Column(db.Integer)  # or db.String if you prefer month names
    process_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='payroll_records')
    @property
    def finalized_net_salary(self):
        # Example calculation (customize as needed)
        base = self.basic_salary or 0
        allowances = self.allowances or 0
        bonuses = self.bonuses or 0
        deductions = self.deductions or 0
        late_penalty = self.late_penalty or 0
        absence_penalty = self.absence_penalty or 0

        # Example: subtract penalties for late days and absences
        return base + allowances + bonuses - deductions - late_penalty - absence_penalty


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='notifications')
    is_system = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=0)
    
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'geddikriss@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'G24517705'  # Replace with your email password
mail= Mail(app)
def send_email(subject, recipient, body):
    try:
        msg = MailMessage(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient],
            body=body
        )
        mail.send(msg)
        print(f"[INFO] Email sent to {recipient}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

def send_sms(to, message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        print(f"[INFO] SMS sent to {to}")
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")

def notify_attendance_alert(employee_name, alert_type):
    subject = f"Attendance Alert: {alert_type}"
    body = f"An attendance alert has been triggered for {employee_name}. Alert Type: {alert_type}."
    admin_email = "geddikriss@gmail.com"  # Replace with the admin's email
    admin_phone = "+251982431755"  # Replace with the admin's phone number

    # Send email
    send_email(subject, admin_email, body)

    # Send SMS
    send_sms(admin_phone, body)
def notify_payroll_update(employee_name, update_type):
    subject = f"Payroll Update: {update_type}"
    body = f"A payroll update has been made for {employee_name}. Update Type: {update_type}."
    admin_email = "geddikriss@gmail.com"  # Replace with the admin's email
    admin_phone = "+251982431755"  # Replace with the admin's phone number

    # Send email
    send_email(subject, admin_email, body)

    # Send SMS
    send_sms(admin_phone, body)
    
def notify_unauthorized_login(ip_address):
    subject = "Security Alert: Unauthorized Login Attempt"
    body = f"An unauthorized login attempt was detected from IP address: {ip_address}."
    admin_email = "geddikriss@gmail.com"  # Replace with the admin's email
    admin_phone = "+251982431755"  # Replace with the admin's phone number

    # Send email
    send_email(subject, admin_email, body)

    # Send SMS
    send_sms(admin_phone, body)

class DateForm_2(FlaskForm):
    date_from = DateField('Date From', format='%Y-%m-%d', validators=[DataRequired()])
    date_to = DateField('Date To', format='%Y-%m-%d', validators=[DataRequired()])

# Form Class (add to your forms.py)
class PayrollForm(FlaskForm):
    id = SelectField('Employee', validators=[DataRequired()],choices=[],render_kw={"class": "form-select select2"},coerce=int)
    month = DateField('Pay Period Month', format='%Y-%m', validators=[DataRequired()], render_kw={"class": "form-control datepicker","placeholder": "Select month","autocomplete": "off"})
    base_salary = DecimalField('Base Salary', validators=[DataRequired(), NumberRange(min=0)],render_kw={"class": "form-control","step": "0.01","min": "0"})
    allowances = DecimalField('Allowances', default=0.0, validators=[NumberRange(min=0)],render_kw={"class": "form-control","step": "0.01","min": "0"})
    bonuses = DecimalField('Bonuses', default=0.0, validators=[NumberRange(min=0, message="Bonuses cannot be negative")],render_kw={"class": "form-control","step": "0.01","min": "0"})
    deductions = DecimalField('Deductions', default=0.0, validators=[NumberRange(min=0)],render_kw={"class": "form-control","step": "0.01","min": "0"})
    absences = IntegerField('Absences', default=0, validators=[NumberRange(min=0)],render_kw={"class": "form-control","step": "0.01","min": "0","max": "31"})
    late_days = IntegerField('Late Days', default=0, validators=[NumberRange(min=0,max=31, message="Absences must be between 0-31")],render_kw={"class": "form-control","step": "0.01","min": "0"})
    performance = SelectField('Performance Rating', validators=[DataRequired()],choices=[('Outstanding', 'Outstanding (+15%)'),('Excellent', 'Excellent (+10%)'),('Good', 'Good (+5%)'),('Average', 'Average (0%)'),('Poor', 'Poor (-5%)')],default='Good',render_kw={"class": "form-select"})
    submit = SubmitField('Submit Payroll',render_kw={"class": "btn btn-primary"})


def calculate_ear(eye):
    """
    Calculate the Eye Aspect Ratio (EAR) for blink detection.
    """
    # Compute the distances between the two sets of vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Compute the distance between the horizontal eye landmarks
    C = dist.euclidean(eye[0], eye[3])

    # Compute the EAR
    ear = (A + B) / (2.0 * C)
    return ear

@app.template_filter('format_last_updated')
def format_last_updated(value, default="Never updated"):
    if not value or value == "Never":
        return default
    
    try:
        # Handle both string and datetime objects
        if isinstance(value, str):
            # Try parsing common datetime formats
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y'):
                try:
                    dt = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return value  # Return original string if no format matched
        else:
            dt = value  # Already a datetime object
        
        # Calculate time difference
        now = datetime.now()
        diff = now - dt
        
        # Return human-readable format
        if diff.days > 365:
            return f"Updated {dt.strftime('%b %Y')}"
        elif diff.days > 30:
            months = diff.days // 30
            return f"Updated {months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"Updated {diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"Updated {hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"Updated {minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Updated just now"
            
    except Exception:
        return default

# Globals (track across frames)
LIVENESS_HISTORY = []
BLINK_COUNTER = 0
TOTAL_BLINKS = 0
PREV_FACE_POSITION = None
CONSEC_FRAMES = 3  # Blink must last at least this long

def detect_liveness(face_rect, gray_frame, predictor, frame_count=0):
    global BLINK_COUNTER, TOTAL_BLINKS, PREV_FACE_POSITION, LIVENESS_HISTORY

    try:
        (x, y, w, h) = face_utils.rect_to_bb(face_rect)
        face_region = gray_frame[y:y + h, x:x + w]

        # Movement detection
        movement_detected = False
        if PREV_FACE_POSITION:
            dx = abs(x - PREV_FACE_POSITION[0])
            dy = abs(y - PREV_FACE_POSITION[1])
            if dx > 5 or dy > 5:
                movement_detected = True
        PREV_FACE_POSITION = (x, y)

        # Facial landmarks for blink detection
        shape = predictor(gray_frame, face_rect)
        shape = face_utils.shape_to_np(shape)
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        left_eye = shape[lStart:lEnd]
        right_eye = shape[rStart:rEnd]

        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # Blink logic
        BLINK_THRESHOLD = 0.2
        if ear < BLINK_THRESHOLD:
            BLINK_COUNTER += 1
        else:
            if BLINK_COUNTER >= CONSEC_FRAMES:
                TOTAL_BLINKS += 1
            BLINK_COUNTER = 0

        # Texture Analysis with LBP
        texture_score = 0
        if face_region.shape[0] >= 64 and face_region.shape[1] >= 64:
            radius = 3
            n_points = 8 * radius
            lbp = local_binary_pattern(face_region, n_points, radius, method='uniform')
            hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
            hist = hist.astype("float")
            hist /= (hist.sum() + 1e-7)
            texture_score = np.std(hist)

        # Color diversity check (optional)
        # color_diversity = np.std(frame[y:y+h, x:x+w]) if len(frame.shape) == 3 else 0

        # Scoring system
        score = 0
        if movement_detected:
            score += 0.3
        if TOTAL_BLINKS >= 1:
            score += 0.4
        if texture_score > 0.1:
            score += 0.3

        LIVENESS_HISTORY.append(score)
        if len(LIVENESS_HISTORY) > 10:
            LIVENESS_HISTORY.pop(0)

        avg_score = sum(LIVENESS_HISTORY) / len(LIVENESS_HISTORY)
        is_live = avg_score >= 0.6

        print(f"[DEBUG] EAR: {ear:.2f}, Blinks: {TOTAL_BLINKS}, Moved: {movement_detected}, Texture: {texture_score:.2f}, Liveness: {avg_score:.2f}")

        return is_live, ear, movement_detected

    except Exception as e:
        print(f"[ERROR] Liveness detection error: {e}")
        return False, 0, False
@app.route('/select_employee_for_photos')
def select_employee_for_photos():
    """Enhanced employee selection with better filtering and status indicators"""
    try:
        BASE_DIR = r"C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask"
        TRAINING_DIR = os.path.join(BASE_DIR, "face_recognition_data", "training_dataset")
        
        # Get active users with additional filters
        employees = User.query.filter(
            User.is_active == True
        ).options(
            db.joinedload(User.department)
        ).order_by(
            User.username
        ).all()
        
        employee_data = []
        for emp in employees:
            user_dir = os.path.join(TRAINING_DIR, emp.username)
            has_photos = False
            photo_samples = 0
            sample_preview = None
            registration_status = "Not Registered"
            
            if os.path.exists(user_dir):
                photo_files = [f for f in os.listdir(user_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                photo_samples = len(photo_files)
                has_photos = photo_samples > 0
                
                if has_photos:
                    first_photo = os.path.join("face_recognition_data", "training_dataset", 
                                            emp.username, photo_files[0])
                    sample_preview = url_for('static', filename=first_photo)
                    
                    # Determine registration status
                    if photo_samples >= 20:
                        registration_status = "Complete"
                    elif photo_samples >= 5:
                        registration_status = "Partial"
                    else:
                        registration_status = "Incomplete"
            
            employee_data.append({
                'id': emp.id,
                'username': emp.username,
                'full_name': emp.username,
                'department': emp.department.name if emp.department else 'No department',
                'last_updated': emp.last_updated.strftime('%Y-%m-%d %H:%M') if emp.last_updated else 'Never',
                'has_photos': has_photos,
                'photo_count': photo_samples,
                'registration_status': registration_status,
                'photo_preview': sample_preview,
                'registration_progress': min(100, (photo_samples / 20) * 100)  # For progress bar
            })
        
        return render_template('select_employee.html',
                            employees=employee_data,
                            employee_count=len(employee_data),
                            now=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    except Exception as e:
        current_app.logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
        flash('Error loading employee data. Please check server logs.', 'danger')
        return redirect(url_for('admin_dashboard'))
@app.route('/add_photos/<int:user_id>', methods=['GET', 'POST'])
def add_photos(user_id):
    """Enhanced face registration with improved frame processing and visual feedback"""
    # Constants
    MIN_SAMPLES = 20
    REQUIRED_ANGLES = ['center', 'left', 'right', 'up', 'down']
    SAMPLE_PER_ANGLE = MIN_SAMPLES // len(REQUIRED_ANGLES)

    user = User.query.get_or_404(user_id)
    processing_steps = []
    
    # Setup directories
    training_dir = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\face_recognition_data\training_dataset'
    user_dir = os.path.join(training_dir, user.username)
    os.makedirs(user_dir, exist_ok=True)
    SHAPE_PREDICTOR_PATH = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\face_recognition_data\shape_predictor_68_face_landmarks.dat'

    # Check existing samples
    existing_samples = [f for f in os.listdir(user_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    sample_num = len(existing_samples)

    if request.method == 'POST':
        try:
            # Initialize face detection components
            processing_steps.append(("1. System Initialization", "Starting"))
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
            fa = FaceAligner(predictor, desiredFaceWidth=256)
            processing_steps.append(("1. System Initialization", "Completed"))

            # Initialize camera with retries
            processing_steps.append(("4. Camera Initialization", "Starting"))
            vs = None
            try:
                vs = VideoStream(src=0, usePiCamera=False).start()
                time.sleep(2.0)
                processing_steps.append(("4. Camera Initialization", "Success"))
            except Exception as e:
                processing_steps.append(("4. Camera Initialization", f"Failed: {str(e)}"))
                flash(f'Camera initialization failed: {str(e)}', 'danger')
                return render_template('add_photos.html',user=user,min_samples=MIN_SAMPLES,current_samples=sample_num,instructions=instructions,csrf_token=generate_csrf())


            # Capture variables
            angle_counts = {angle: 0 for angle in REQUIRED_ANGLES}
            current_angle = 'center'
            last_capture_time = time.time()
            capture_cooldown = 1.5  # seconds between captures
            frame_count = 0
            consecutive_failures = 0

            while sample_num < MIN_SAMPLES:
                try:
                    frame = vs.read()
                    if frame is None:
                        consecutive_failures += 1
                        if consecutive_failures > 10:
                            raise RuntimeError("Camera stopped responding")
                        time.sleep(0.1)
                        continue
                    
                    consecutive_failures = 0  # Reset on successful frame read
                    
                    # Enhanced frame processing
                    frame = imutils.resize(frame, width=800)
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_frame = cv2.equalizeHist(gray_frame)
                    gray_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
                    
                    faces = detector(gray_frame, 0)

                    # Information display frame
                    info_frame = np.zeros((500, 800, 3), dtype="uint8")
                    cv2.rectangle(info_frame, (0, 0), (800, 500), (50, 50, 50), -1)
                    
                    # Display processing information
                    cv2.putText(info_frame, "Face Registration Progress", (20, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
                    
                    # Display last 8 processing steps
                    for i, (step, status) in enumerate(processing_steps[-8:]):
                        color = (0, 255, 0) if "Completed" in status else (255, 255, 255) if "Starting" in status else (0, 0, 255)
                        cv2.putText(info_frame, f"{step}: {status}", (20, 70 + i * 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    
                    # Current status display
                    cv2.putText(info_frame, "Registration Status:", (20, 300), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(info_frame, f"Captured: {sample_num}/{MIN_SAMPLES}", (20, 330), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_frame, f"Current Angle: {current_angle}", (20, 360), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    if len(faces) == 0:
                        status_msg = "Please position your face in the frame"
                        cv2.putText(info_frame, status_msg, (20, 390), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                    else:
                        status_msg = "Face detected - Hold position"
                        cv2.putText(info_frame, status_msg, (20, 390), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                    
                    # Display instructions
                    cv2.putText(info_frame, "Instructions:", (20, 430), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(info_frame, "1. Follow the angle instructions", (20, 460), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(info_frame, "2. Keep face centered and visible", (20, 480), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    for face in faces:
                        (x, y, w, h) = face_utils.rect_to_bb(face)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        
                        # Draw facial landmarks for better visual feedback
                        landmarks = predictor(gray_frame, face)
                        landmarks = face_utils.shape_to_np(landmarks)
                        for (lx, ly) in landmarks:
                            cv2.circle(frame, (lx, ly), 1, (0, 0, 255), -1)

                        # Check if ready for capture
                        current_time = time.time()
                        if (current_time - last_capture_time) > capture_cooldown:
                            face_aligned = fa.align(frame, gray_frame, face)
                            if face_aligned is not None:
                                # Check for duplicates
                                if check_for_duplicates(face_aligned, training_dir):
                                    cv2.putText(frame, "Duplicate detected", (x, y - 20), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    continue
                                
                                # Save the image
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"{user.username}_{current_angle}_{timestamp}.jpg"
                                cv2.imwrite(os.path.join(user_dir, filename), face_aligned)
                                
                                sample_num += 1
                                angle_counts[current_angle] += 1
                                last_capture_time = current_time
                                processing_steps.append((f"3. {current_angle.capitalize()} Capture", f"Sample {sample_num} saved"))
                                
                                # Visual feedback
                                cv2.putText(frame, "CAPTURED", (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Change angle if we have enough samples for current angle
                    if angle_counts[current_angle] >= SAMPLE_PER_ANGLE:
                        remaining_angles = [a for a in REQUIRED_ANGLES if angle_counts[a] < SAMPLE_PER_ANGLE]
                        if remaining_angles:
                            current_angle = random.choice(remaining_angles)
                            processing_steps.append(("4. Angle Change", f"Switching to {current_angle} view"))
                            # Visual cue for angle change
                            cv2.putText(frame, f"CHANGE TO: {current_angle.upper()}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            time.sleep(1)  # Brief pause for angle change

                    # Display frames
                    cv2.imshow("Face Registration", frame)
                    cv2.imshow("Registration Progress", info_frame)
                    
                    key = cv2.waitKey(50) & 0xFF
                    if key == ord("q"):
                        break

                    frame_count += 1

                except Exception as e:
                    processing_steps.append(("Error", f"Frame processing error: {str(e)}"))
                    current_app.logger.error(f"Frame processing error: {str(e)}")
                    time.sleep(0.5)
                    continue
            
            # Cleanup
            vs.stop()
            cv2.destroyAllWindows()
            
            if sample_num >= MIN_SAMPLES:
                train_result = train_face_model(training_dir, user_dir, user.id)
                if train_result.get('success'):
                    flash(f'Successfully registered {sample_num} face samples', 'success')
                    return redirect(url_for('user_profile', user_id=user.id))
                else:
                    flash('Photos saved but model training failed', 'warning')
            else:
                flash(f'Captured {sample_num} samples (minimum {MIN_SAMPLES} required)', 'warning')
            
        except Exception as e:
            flash(f'Face registration failed: {str(e)}', 'danger')
            current_app.logger.error(f"Error in add_photos: {str(e)}")
            try:
                if 'vs' in locals() and vs:
                    vs.stop()
                cv2.destroyAllWindows()
            except:
                pass
    
    # GET request - show instructions
    instructions = [
        {"icon": "fa-video", "title": "Camera Setup", 
        "desc": "Ensure your camera is properly positioned at eye level"},
        {"icon": "fa-lightbulb", "title": "Lighting", 
        "desc": "Face a light source for clear images without shadows"},
        {"icon": "fa-user", "title": "Positioning", 
        "desc": "Follow the angle instructions shown during capture"},
        {"icon": "fa-ban", "title": "No Accessories", 
        "desc": "Remove glasses, hats or other face coverings"},
        {"icon": "fa-info-circle", "title": "Process", 
        "desc": "System will guide you through multiple angles"}
    ]
    
    return render_template('add_photos.html',
        user=user,
        min_samples=MIN_SAMPLES,
        current_samples=sample_num,
        instructions=instructions,
        csrf_token=generate_csrf()
    )
def check_for_duplicates(face_aligned, user_dir, tolerance=0.5):
    """
    Check for duplicate faces in the current user's directory only.
    Returns True if a duplicate is found, False otherwise.
    """
    try:
        current_encoding_list = face_recognition.face_encodings(face_aligned)
        if not current_encoding_list:
            return False  # No face found in the aligned image
        current_encoding = current_encoding_list[0]

        # Only check images in the current user's directory
        for img_file in os.listdir(user_dir):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(user_dir, img_file)
                img = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    match = face_recognition.compare_faces([encodings[0]], current_encoding, tolerance=tolerance)
                    if match[0]:
                        return True  # Duplicate found
        return False
    except Exception as e:
        current_app.logger.error(f"Error checking for duplicates: {str(e)}")
        return False


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<int:user_id>')
def video_feed(user_id):
    """Route to stream live camera feed"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/registration_status/<int:user_id>')
def registration_status(user_id):
    user = User.query.get_or_404(user_id)
    training_dir = current_app.config['TRAINING_DATASET_PATH']
    user_dir = os.path.join(training_dir, user.username)
    
    if not os.path.exists(user_dir):
        return jsonify({
            'status': 'error',
            'message': 'Registration directory not found',
            'completed': False
        })
    
    existing_samples = [f for f in os.listdir(user_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Check if training is complete
    model_file = os.path.join(training_dir, 'trained_model.dat')
    if os.path.exists(model_file):
        return jsonify({
            'status': 'success',
            'completed': True,
            'message': 'Registration complete',
            'capture_count': len(existing_samples),
            'min_samples': MIN_SAMPLES
        })
    
    return jsonify({
        'status': 'processing',
        'completed': False,
        'capture_count': len(existing_samples),
        'min_samples': MIN_SAMPLES,
        'message': f'Captured {len(existing_samples)} of {MIN_SAMPLES} samples'
    })
@app.route('/check_registration_status/<int:user_id>')
def check_registration_status(user_id):
    user = User.query.get_or_404(user_id)
    training_dir = current_app.config['TRAINING_DATASET_PATH']
    user_dir = os.path.join(training_dir, user.username)
    
    if not os.path.exists(user_dir):
        return jsonify({
            'completed': False,
            'error': 'Registration not started'
        })
    
    # Get current capture count
    existing_samples = [f for f in os.listdir(user_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Check if training file exists (indicates completion)
    model_file = os.path.join(training_dir, 'trained_model.dat')
    if os.path.exists(model_file):
        return jsonify({
            'completed': True,
            'message': f'Successfully registered {len(existing_samples)} face samples',
            'capture_count': len(existing_samples),
            'min_samples': 20  # Your MIN_SAMPLES value
        })
    
    # Return current progress
    return jsonify({
        'completed': False,
        'capture_count': len(existing_samples),
        'min_samples': 20,  # Your MIN_SAMPLES value
        'processing_steps': []  # Placeholder for processing steps or implement the logic
    })
class FaceRegistrationProcessor:
    """Enhanced face registration processor with quality checks and guidance"""
    
    def __init__(self, user, output_dir, min_samples=20, max_samples=300, required_angles=None):
        self.user = user
        self.output_dir = output_dir
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.required_angles = required_angles or ['center']
        
        # Initialize counters and trackers
        self.capture_count = 0
        self.angle_counts = {angle: 0 for angle in self.required_angles}
        self.processing_steps = []
        self.last_face_encoding = None
        self.duplicate_threshold = 0.6
        
        # Initialize face detectors
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(current_app.config['SHAPE_PREDICTOR_PATH'])
        self.face_aligner = FaceAligner(self.predictor, desiredFaceWidth=256)
        
        # Quality thresholds
        self.min_face_size = 100  # pixels
        self.max_blur = 100  # variance threshold
    
    def process_frame(self, frame, required_angle='center'):
        """Process a video frame for face registration"""
        result = {
            'status': None,
            'message': '',
            'quality_score': 0,
            'saved_path': None
        }
        
        try:
            # Convert to RGB and resize
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = imutils.resize(rgb_frame, width=800)
            gray_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.detector(gray_frame, 1)
            
            if not faces:
                result['status'] = 'no_face'
                result['message'] = 'No face detected'
                self._add_processing_step('Detection', 'No face found')
                return result
            
            # Process first face found
            face = faces[0]
            (x, y, w, h) = face_utils.rect_to_bb(face)
            
            # Check face size
            if w < self.min_face_size or h < self.min_face_size:
                result['status'] = 'face_too_small'
                result['message'] = 'Move closer to the camera'
                self._add_processing_step('Detection', 'Face too small')
                return result
            
            # Check image blur
            blur = cv2.Laplacian(gray_frame[y:y+h, x:x+w], cv2.CV_64F).var()
            if blur < self.max_blur:
                result['status'] = 'too_blurry'
                result['message'] = 'Image is too blurry'
                self._add_processing_step('Quality', 'Image too blurry')
                return result
            
            # Align face
            face_aligned = self.face_aligner.align(rgb_frame, gray_frame, face)
            if face_aligned is None:
                result['status'] = 'alignment_failed'
                result['message'] = 'Face alignment failed'
                self._add_processing_step('Alignment', 'Failed to align face')
                return result
            
            # Check face angle
            angle_status = self._check_face_angle(face, required_angle)
            if not angle_status['valid']:
                result['status'] = 'wrong_angle'
                result['message'] = angle_status['message']
                self._add_processing_step('Pose', angle_status['message'])
                return result
            
            # Check for duplicates
            if not self._is_unique_face(face_aligned):
                result['status'] = 'duplicate'
                result['message'] = 'Similar face already captured'
                self._add_processing_step('Duplicate', 'Similar face detected')
                return result
            
            # Check liveness
            if not detect_liveness(face_aligned):
                result['status'] = 'liveness_failed'
                result['message'] = 'Liveness check failed'
                self._add_processing_step('Liveness', 'Failed liveness detection')
                return result
            
            # All checks passed - save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{self.user.username}_{required_angle}_{timestamp}.jpg"
            save_path = os.path.join(self.output_dir, filename)
            cv2.imwrite(save_path, cv2.cvtColor(face_aligned, cv2.COLOR_RGB2BGR))
            
            # Update counters
            self.capture_count += 1
            self.angle_counts[required_angle] += 1
            self.last_face_encoding = face_recognition.face_encodings(face_aligned)[0]
            
            result['status'] = 'success'
            result['message'] = f"Captured {required_angle} view"
            result['quality_score'] = self._calculate_quality_score(face_aligned)
            result['saved_path'] = save_path
            
            self._add_processing_step('Capture', f"Saved {required_angle} sample {self.angle_counts[required_angle]}")
            
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)
            self._add_processing_step('Error', str(e))
        
        return result
    
    def _check_face_angle(self, face, required_angle):
        """Check if face matches the required angle"""
        if 'gray_frame' not in locals():
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale if not already defined
        shape = self.predictor(gray_frame, face)
        shape = face_utils.shape_to_np(shape)
        
        # Calculate angles based on facial landmarks
        angle_results = {
            'center': self._is_centered(shape),
            'left': self._is_turned_left(shape),
            'right': self._is_turned_right(shape),
            'up': self._is_looking_up(shape),
            'down': self._is_looking_down(shape)
        }
        
        if not angle_results.get(required_angle, False):
            return {
                'valid': False,
                'message': f"Please turn your head {required_angle}"
            }
        
        return {'valid': True, 'message': ''}
    
    def _is_unique_face(self, face_image):
        """Check if face is significantly different from last captured face"""
        if self.last_face_encoding is None:
            return True
            
        current_encoding = face_recognition.face_encodings(face_image)
        if not current_encoding:
            return False
            
        distance = face_recognition.face_distance([self.last_face_encoding], current_encoding[0])[0]
        return distance > self.duplicate_threshold
    
    def _calculate_quality_score(self, face_image):
        """Calculate a quality score for the face image"""
        # Implement quality metrics (sharpness, contrast, etc.)
        return 85  # Placeholder
    
    def _add_processing_step(self, stage, message):
        """Add a processing step with timestamp"""
        self.processing_steps.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'stage': stage,
            'message': message
        })
    
    def add_guidance_overlay(self, frame, result):
        """Add guidance overlay to the frame"""
        # Basic frame info
        cv2.putText(frame, f"User: {self.user.username}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Captured: {self.capture_count}/{self.min_samples}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Angle progress
        angle_text = " | ".join([f"{a}: {c}" for a, c in self.angle_counts.items()])
        cv2.putText(frame, angle_text, (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        
        # Current status message
        cv2.putText(frame, result['message'], (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Face detection rectangle
        rgb_frame = frame[:, :, ::-1]
        face_locs = face_recognition.face_locations(rgb_frame)
        for (top, right, bottom, left) in face_locs:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Add angle guidance indicators
        if 'angle' in result.get('message', ''):
            self._draw_angle_guidance(frame, result['message'])
        
        return frame
    
    def _draw_angle_guidance(self, frame, message):
        """Draw visual guidance for head positioning"""
        h, w = frame.shape[:2]
        
        if 'left' in message:
            cv2.arrowedLine(frame, (w//2, h//2), (w//4, h//2), (0, 255, 255), 2)
        elif 'right' in message:
            cv2.arrowedLine(frame, (w//2, h//2), (3*w//4, h//2), (0, 255, 255), 2)
        elif 'up' in message:
            cv2.arrowedLine(frame, (w//2, h//2), (w//2, h//4), (0, 255, 255), 2)
        elif 'down' in message:
            cv2.arrowedLine(frame, (w//2, h//2), (w//2, 3*h//4), (0, 255, 255), 2)
        else:  # center
            cv2.circle(frame, (w//2, h//2), 10, (0, 255, 0), -1)
def _add_status_overlay(self, frame, processor):
    """Add real-time status overlay to the video frame"""
    # Add text overlays
    cv2.putText(frame, f"Captured: {processor.capture_count}/{MIN_SAMPLES}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Add latest processing step
    if processor.processing_steps:
        last_step = processor.processing_steps[-1]
        cv2.putText(frame, f"{last_step[0]}: {last_step[1]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Add face detection box if available
    rgb_frame = frame[:, :, ::-1]
    face_locs = face_recognition.face_locations(rgb_frame)
    for (top, right, bottom, left) in face_locs:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    
    return frame

def get_sample_images():
    """Get sample good/bad images for guidance"""
    return {
        'good': [
            {'url': url_for('static', filename='samples/good1.jpg'), 'desc': 'Well-lit, centered face'},
            {'url': url_for('static', filename='samples/good2.jpg'), 'desc': 'Neutral expression'}
        ],
        'bad': [
            {'url': url_for('static', filename='samples/bad1.jpg'), 'desc': 'Too dark'},
            {'url': url_for('static', filename='samples/bad2.jpg'), 'desc': 'Blurry image'}
        ]
    }

def log_face_registration(user_id, samples_added, total_samples):
    """
    Logs the face registration process for a user.
    Args:
        user_id (int): ID of the user.
        samples_added (int): Number of samples added during the process.
        total_samples (int): Total number of samples after the process.
    """
    logger.info(f"Face registration completed for User ID {user_id}. "
                f"Samples added: {samples_added}, Total samples: {total_samples}")


def cleanup_resources(directory_path):
    """
    Placeholder function to clean up resources.
    Args:
        directory_path (str): Path to the directory to clean up.
    """
    try:
        if os.path.exists(directory_path):
            print(f"Cleaning up resources in {directory_path}")
            # Add cleanup logic here if needed
    except Exception as e:
        print(f"Error during cleanup: {e}")


def train_face_model(training_dir, user_photos_dir, user_id):
    """
    Train the face recognition model using the provided training directory.
    Args:
        training_dir: Path to the training dataset directory.
        user_photos_dir: Path to the user's photo directory.
        user_id: ID of the user being trained.
    Returns:
        A dictionary with the training result.
    """
    try:
        # Load training data
        X = []
        y = []
        for person_name in os.listdir(training_dir):
            person_dir = os.path.join(training_dir, person_name)
            if not os.path.isdir(person_dir):
                continue
            for img_file in os.listdir(person_dir):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(person_dir, img_file)
                    img = face_recognition.load_image_file(img_path)
                    encodings = face_recognition.face_encodings(img)
                    if encodings:
                        X.append(encodings[0])
                        y.append(person_name)

        # Train the model
        if not X:
            return {'success': False, 'message': 'No training data found.'}
        X = np.array(X)
        y = np.array(y)
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y)
        svc = SVC(kernel='linear', probability=True)
        svc.fit(X, y_encoded)

        # Save the model and classes
        with open('face_recognition_data/svc.sav', 'wb') as f:
            pickle.dump(svc, f)
        np.save('face_recognition_data/classes.npy', encoder.classes_)

        return {'success': True, 'message': 'Model trained successfully.'}
    except Exception as e:
        return {'success': False, 'message': f'Error during training: {e}'}


def process_face_capture(user, user_photos_dir, existing_count, min_samples, max_samples, max_time):
    """
    Simulates the face capture process for a user.
    Args:
        user: The user object.
        user_photos_dir: Directory to save captured photos.
        existing_count: Number of existing samples.
        min_samples: Minimum samples required.
        max_samples: Maximum samples allowed.
        max_time: Maximum time allowed for capture.
    Returns:
        A dictionary with the capture result.
    """
    try:
        # Simulate capturing photos
        samples_added = max_samples - existing_count
        total_samples = existing_count + samples_added
        return {
            'success': True,
            'samples_added': samples_added,
            'total_samples': total_samples
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error during face capture: {str(e)}"
        }


def check_existing_samples(user_photos_dir, username, min_samples):
    """
    Check if the user already has enough samples in the directory.
    Args:
        user_photos_dir (str): Path to the user's photo directory.
        username (str): Username of the user.
        min_samples (int): Minimum number of samples required.
    Returns:
        list: List of existing sample files if less than min_samples, otherwise None.
    """
    if not os.path.exists(user_photos_dir):
        return []

    existing_files = [
        f for f in os.listdir(user_photos_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if len(existing_files) >= min_samples:
        return None  # User already has enough samples

    return existing_files
# Helper functions would be defined here with similar improvements





def predict(face_aligned,svc,threshold=0.7):
	face_encodings=np.zeros((1,128))
	try:
		x_face_locations=face_recognition.face_locations(face_aligned)
		faces_encodings=face_recognition.face_encodings(face_aligned,known_face_locations=x_face_locations)
		if(len(faces_encodings)==0):
			return ([-1],[0])

	except:

		return ([-1],[0])

	prob=svc.predict_proba(faces_encodings)
	result=np.where(prob[0]==np.amax(prob[0]))
	if(prob[0][result[0]]<=threshold):
		return ([-1],prob[0][result[0]])

	return (result[0],prob[0][result[0]])


	###################################################errrrrrrss###################
def update_attendance_in_db_in(present):
    today = date.today()
    time = datetime.now()
    attendance_id = None
    for person in present:
        # Fetch the user from the database
        user = User.query.filter_by(username=person).first()
        if not user:
            print(f"User with username {person} not found.")
            continue  # Skip to the next person if the user is not found

        try:
            # Check if a record already exists for the user and date
            qs = Present.query.filter_by(user_id=user.id, date=today).first()
        except Exception as e:
            print(f"Error fetching attendance record: {e}")
            qs = None

        if qs is None:
            # Create a new attendance record if none exists
            if present[person]:
                new_record = Present(user_id=user.id, date=today, present=True)
                db.session.add(new_record)
                db.session.commit()
                attendance_id = new_record.id 
            else:
                new_record = Present(user_id=user.id, date=today, present=False)
                db.session.add(new_record)
                db.session.commit()
                attendance_id = new_record.id
        else:
            # Update the existing attendance record
            if present[person]:
                qs.present = True
                db.session.commit()
                attendance_id = qs.id  # Get the ID of the existing record
            else:
                qs.present = False
                db.session.commit()
                attendance_id = qs.id
                

        if present[person]:
            # Log the time for the user
            new_time = Time(user_id=user.id, timestamp=time)
            db.session.add(new_time)

    db.session.commit()
    return attendance_id  # Return the ID of the attendance record


def update_attendance_in_db_out(present):
    today = date.today()
    current_time = datetime.now()
    for person, is_present in present.items():
        # Fetch the user from the database
        user = User.query.filter_by(username=person).first()
        if not user:
            print(f"User with username {person} not found.")
            continue  # Skip to the next person if the user is not found

        try:
            # Check if a record already exists for the user and date
            existing_record = Present.query.filter_by(user_id=user.id, date=today).first()
            if existing_record:
                # Update the existing attendance record
                if is_present:
                    existing_record.present = True
                    db.session.commit()
            else:
                # Create a new attendance record if none exists
                new_record = Present(user_id=user.id, date=today, present=is_present)
                db.session.add(new_record)
                db.session.commit()

            # Log the time-out for the user
            if is_present:
                new_time = Time(user_id=user.id, timestamp=current_time)
                db.session.add(new_time)
                db.session.commit()

        except Exception as e:
            print(f"Error updating attendance for {person}: {e}")


def check_validity_times(times_all):

	if(len(times_all)>0):
		sign=times_all.first().out
	else:
		sign=True
	times_in=times_all.filter(out=False)
	times_out=times_all.filter(out=True)
	if(len(times_in)!=len(times_out)):
		sign=True
	break_hourss=0
	if(sign==True):
			check=False
			break_hourss=0
			return (check,break_hourss)
	prev=True
	prev_time=times_all.first().time

	for obj in times_all:
		curr=obj.out
		if(curr==prev):
			check=False
			break_hourss=0
			return (check,break_hourss)
		if(curr==False):
			curr_time=obj.time
			to=curr_time
			ti=prev_time
			break_time=((to-ti).total_seconds())/3600
			break_hourss+=break_time


		else:
			prev_time=obj.time

		prev=curr

	return (True,break_hourss)
def convert_hours_to_hours_mins(hours):
	
	h=int(hours)
	hours-=h
	m=hours*60
	m=math.ceil(m)
	return str(str(h)+ " hrs " + str(m) + "  mins")

def hours_vs_date_given_employee(present_qs,time_qs,admin=True):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	qs=present_qs

	for obj in qs:
		date=obj.date
		times_in=time_qs.filter(date=date).filter(out=False).order_by('time')
		times_out=time_qs.filter(date=date).filter(out=True).order_by('time')
		times_all=time_qs.filter(date=date).order_by('time')
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.break_hours=0
		if (len(times_in)>0):			
			obj.time_in=times_in.first().time
			
		if (len(times_out)>0):
			obj.time_out=times_out.last().time

		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
		

		else:
			obj.hours=0

		(check,break_hourss)= check_validity_times(times_all)
		if check:
			obj.break_hours=break_hourss
		else:
			obj.break_hours=0
		
		df_hours.append(obj.hours)
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)
			
	df = read_frame(qs)	
	df["hours"]=df_hours
	df["break_hours"]=df_break_hours

	print(df)
	
	sns.barplot(data=df,x='date',y='hours')
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	if(admin):
		plt.savefig('./recognition/static/recognition/img/attendance_graphs/hours_vs_date/1.png')
		plt.close()
	else:
		plt.savefig('./recognition/static/recognition/img/attendance_graphs/employee_login/1.png')
		plt.close()
	return qs

#used
def hours_vs_employee_given_date(present_qs,time_qs):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	df_username=[]
	qs=present_qs

	for obj in qs:
		user=obj.user
		times_in=time_qs.filter(user=user).filter(out=False)
		times_out=time_qs.filter(user=user).filter(out=True)
		times_all=time_qs.filter(user=user)
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.hours=0
		if (len(times_in)>0):			
			obj.time_in=times_in.first().time
		if (len(times_out)>0):
			obj.time_out=times_out.last().time
		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
		else:
			obj.hours=0
		(check,break_hourss)= check_validity_times(times_all)
		if check:
			obj.break_hours=break_hourss
		else:
			obj.break_hours=0
		
		df_hours.append(obj.hours)
		df_username.append(user.username)
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)
	df = read_frame(qs)	
	df['hours']=df_hours
	df['username']=df_username
	df["break_hours"]=df_break_hours


	sns.barplot(data=df,x='username',y='hours')
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	plt.savefig('./recognition/static/recognition/img/attendance_graphs/hours_vs_employee/1.png')
	plt.close()
	return qs


def total_num_of_emp():
    qs = User.query.all()  # Corrected to use the User model
    return len(qs) - 1
# Subtract 1 to account for the admin user

def emp_present_today():
    today = date.today()
    qs = Present.query.filter_by(date=today, present=True).all()  # Corrected to fetch data from the Present model
    return len(qs)

#used	
def this_week_emp_count_vs_date():
    today = date.today()
    some_day_last_week = today - timedelta(days=7)
    monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
    monday_of_this_week = monday_of_last_week + timedelta(days=7)
    qs = Present.query.filter(Present.date >= monday_of_this_week, Present.date <= today).all()
    str_dates = []
    emp_count = []
    str_dates_all = []
    emp_cnt_all = []
    cnt = 0

    for obj in qs:
        date = obj.date
        str_dates.append(str(date))
        qs = Present.query.filter(Present.date == date, Present.present == True).all()
        emp_count.append(len(qs))

    while cnt < 5:
        date = str(monday_of_this_week + datetime.timedelta(days=cnt))
        cnt += 1
        str_dates_all.append(date)
        if str_dates.count(date) > 0:
            idx = str_dates.index(date)
            emp_cnt_all.append(emp_count[idx])
        else:
            emp_cnt_all.append(0)

    df = pd.DataFrame()
    df["date"] = str_dates_all
    df["Number of employees"] = emp_cnt_all
    sns.lineplot(data=df, x='date', y='Number of employees')

    # Ensure the directory exists before saving the file
    output_dir = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\static\images'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'this_week_1.png'))
    plt.close()
# Create your views here.
def home(request):

	return render_template(request, 'home.html')

def last_week_emp_count_vs_date():
    today = datetime.date.today()
    some_day_last_week = today - datetime.timedelta(days=7)
    monday_of_last_week = some_day_last_week - datetime.timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
    sunday_of_last_week = monday_of_last_week + datetime.timedelta(days=6)

    qs = Present.query.filter(Present.date >= monday_of_last_week, Present.date <= sunday_of_last_week).all()
    str_dates = []
    emp_count = []
    str_dates_all = []
    emp_cnt_all = []
    cnt = 0

    for obj in qs:
        date = obj.date
        str_dates.append(str(date))
        qs = Present.query.filter(Present.date == date, Present.present == True).all()
        emp_count.append(len(qs))

    while cnt < 7:  # Loop through all 7 days of the week
        date = str(monday_of_last_week + datetime.timedelta(days=cnt))
        cnt += 1
        str_dates_all.append(date)
        if str_dates.count(date) > 0:
            idx = str_dates.index(date)
            emp_cnt_all.append(emp_count[idx])
        else:
            emp_cnt_all.append(0)

    df = pd.DataFrame()
    df["date"] = str_dates_all
    df["Number of employees"] = emp_cnt_all
    sns.lineplot(data=df, x='date', y='Number of employees')

    # Ensure the directory exists before saving the file
    output_dir = r'C:\Users\HP\OneDrive\Desktop\4th Year\II semister\Flask\Flask\static\images'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'last_week_1.png'))
    plt.close()
    
@app.route('/dashboard')
def dashboard(request):
	if(request.user.username=='admin'):
		print("admin")
		return render_template(request, 'admin_dashboard.html')
	else:
		print("not admin")

		return render_template(request,'employee_dashboard.html')

class Config:
    CAMPUS_LOCATION = (9.4142, 42.0769)  # Haramaya University coordinates
    MAX_DISTANCE_METERS = 500
    WORK_START_TIME = 8, 30  # 8:30 AM
    LATE_GRACE_PERIOD_MINUTES = 10
    RECOGNITION_THRESHOLD = 0.6
    LIVENESS_THRESHOLD = 0.2
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    SYSTEM_NAME = "Smart Attendance System"
    UNIVERSITY_NAME = "Haramaya University"
    UNIVERSITY_LOGO_URL = "/static/images/haramaya_logo.png"

# Initialize database
def init_db():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                employee_name TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                is_late BOOLEAN NOT NULL,
                latitude REAL,
                longitude REAL,
                confidence REAL,
                liveness_score REAL)''')
    conn.commit()
    conn.close()

init_db()

# Camera and face recognition state
camera = None
last_frame = None
frame_lock = threading.Lock()
attendance_active = False
current_employee = None
known_face_encodings = []
known_face_names = []

# Initialize face recognition models
def load_face_models():
    global known_face_encodings, known_face_names
    try:
        if os.path.exists("face_encodings.pkl"):
            with open("face_encodings.pkl", "rb") as f:
                known_face_encodings, known_face_names = pickle.load(f)
        return True
    except Exception as e:
        print(f"Error loading face models: {e}")
        return False

# Initialize camera
def init_camera():
    global camera
    if camera and camera.isOpened():
        return True
    
    try:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        return camera.isOpened()
    except Exception as e:
        print(f"Camera init error: {e}")
        return False

# Camera frame generator
def generate_frames():
    global last_frame, frame_lock
    while True:
        with frame_lock:
            if last_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', last_frame)
            if not ret:
                continue
            frame = buffer.tobytes()
        
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

# Calculate eye aspect ratio for liveness detection
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# Process frames for face detection and liveness check
def process_frames():
    global last_frame, frame_lock, attendance_active, current_employee
    
    while True:
        if not attendance_active or not current_employee:
            time.sleep(1)
            continue
            
        if not init_camera():
            time.sleep(1)
            continue
            
        ret, frame = camera.read()
        if not ret:
            continue
            
        # Resize frame for processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # Find faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)
        
        face_data = []
        for (top, right, bottom, left), face_encoding, landmarks in zip(face_locations, face_encodings, face_landmarks_list):
            # Scale face locations back up
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Recognize face
            name = "Unknown"
            confidence = 0
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                confidence = 1 - face_distances[best_match_index]
            
            # Liveness detection
            liveness_score = 0
            if landmarks:
                left_eye = landmarks['left_eye']
                right_eye = landmarks['right_eye']
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                liveness_score = (left_ear + right_ear) / 2.0
            
            face_data.append({
                'x': left,
                'y': top,
                'width': right - left,
                'height': bottom - top,
                'name': name,
                'confidence': confidence,
                'liveness_score': liveness_score,
                'is_live': liveness_score > Config.LIVENESS_THRESHOLD
            })
        
        # Store the processed frame
        with frame_lock:
            last_frame = frame.copy()
        
        # If we found the employee with sufficient confidence and liveness, mark attendance
        for face in face_data:
            if (face['name'] == current_employee['id'] and 
                face['confidence'] >= Config.RECOGNITION_THRESHOLD and 
                face['is_live']):
                
                mark_attendance(current_employee, face['confidence'], face['liveness_score'])
                attendance_active = False
                current_employee = None
                break
            
        time.sleep(0.1)

# Mark attendance and save to database
def mark_attendance(employee, confidence, liveness_score):
    now = datetime.now()
    is_late = is_late_arrival(now)
    geolocation = get_geolocation()
    
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO attendance 
                (employee_id, employee_name, timestamp, is_late, latitude, longitude, confidence, liveness_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (employee['id'], employee['name'], now.isoformat(), is_late,
                geolocation['lat'] if geolocation else None,
                geolocation['lng'] if geolocation else None,
                confidence, liveness_score))
    conn.commit()
    conn.close()
    
    return {
        'employee_id': employee['id'],
        'employee_name': employee['name'],
        'timestamp': now.isoformat(),
        'is_late': is_late,
        'geolocation': geolocation,
        'confidence': confidence,
        'liveness_score': liveness_score,
        'status': 'late' if is_late else 'on_time'
    }

def is_late_arrival(record_time):
    work_start = datetime.combine(record_time.date(), Config.WORK_START_TIME)
    grace_end = work_start + timedelta(minutes=Config.LATE_GRACE_PERIOD_MINUTES)
    return record_time > grace_end

def get_geolocation():
    try:
        # In a real app, you would get this from the browser or device
        return {
            'lat': Config.CAMPUS_LOCATION[0] + (np.random.random() - 0.5) * 0.01,
            'lng': Config.CAMPUS_LOCATION[1] + (np.random.random() - 0.5) * 0.01
        }
    except Exception as e:
        print(f"Geolocation error: {e}")
        return None

def check_geolocation(lat, lng):
    if not lat or not lng:
        return False, None
    distance = geodesic((lat, lng), Config.CAMPUS_LOCATION).meters
    return distance <= Config.MAX_DISTANCE_METERS, distance

'''@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
'''
@app.route('/api/attendance/start', methods=['POST'])
def start_attendance():
    global attendance_active, current_employee
    
    data = request.json
    employee_id = data.get('employee_id')
    
    # In a real app, you would fetch employee details from your database
    employee = {
        'id': employee_id,
        'name': f"Employee {employee_id}"  # Replace with actual lookup
    }
    
    current_employee = employee
    attendance_active = True
    
    return jsonify({
        'status': 'success',
        'message': f"Monitoring started for {employee['name']}",
        'employee': employee
    })

@app.route('/api/attendance/stop', methods=['POST'])
def stop_attendance():
    global attendance_active, current_employee
    attendance_active = False
    current_employee = None
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/attendance/recent')
def get_recent_attendance():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''SELECT employee_id, employee_name, timestamp, is_late, 
                latitude, longitude, confidence, liveness_score 
                FROM attendance ORDER BY timestamp DESC LIMIT 10''')
    records = []
    for row in c.fetchall():
        records.append({
            'employee_id': row[0],
            'employee_name': row[1],
            'timestamp': row[2],
            'is_late': bool(row[3]),
            'geolocation': {'lat': row[4], 'lng': row[5]} if row[4] and row[5] else None,
            'confidence': row[6],
            'liveness_score': row[7],
            'status': 'late' if row[3] else 'on_time'
        })
    conn.close()
    
    # Calculate stats
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('''SELECT 
                COUNT(*) as total_present,
                SUM(CASE WHEN is_late = 0 THEN 1 ELSE 0 END) as total_on_time,
                SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) as total_late
                FROM attendance 
                WHERE date(timestamp) = date('now')''')
    stats = c.fetchone()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'records': records,
        'stats': {
            'total_present': stats[0] if stats else 0,
            'total_on_time': stats[1] if stats else 0,
            'total_late': stats[2] if stats else 0
        }
    })

# Start camera processing thread
if load_face_models():
    camera_thread = threading.Thread(target=process_frames)
    camera_thread.daemon = True
    camera_thread.start()

@app.route('/mark_attendance')
def mark_attendance():
    return render_template('mark_attendance.html', config=Config, now=datetime.now)
# System status
# SocketIO events

def get_video_stream():
    """Try different backends to initialize camera"""
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        vs = cv2.VideoCapture(0, backend)
        if vs.isOpened():
            return vs
    return None

@app.route('/mark_your_attendance_in', methods=['GET', 'POST'])
def mark_your_attendance_in():
    if request.method == 'POST':
        try:
            # Step 1: Geolocation Verification
            processing_steps = []
            status_messages = []
            
            processing_steps.append(("1. Location Verification", "Starting"))
            if not verify_haramaya_university_location():
                processing_steps.append(("1. Location Verification", "Failed - Not in campus"))
                flash('You must be within Haramaya University campus to mark attendance', 'danger')
                return render_template('mark_attendance.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)
            processing_steps.append(("1. Location Verification", "Success"))
            
            # Step 2: Security Checks
            processing_steps.append(("2. Security Checks", "Starting"))
            if not security_checks_passed():
                processing_steps.append(("2. Security Checks", "Failed"))
                return render_template('mark_attendance.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)
            processing_steps.append(("2. Security Checks", "Success"))

            # Step 3: Face Recognition Initialization
            processing_steps.append(("3. Face Recognition Init", "Starting"))
            detector, predictor, svc, encoder, fa = initialize_face_recognition()
            if None in [detector, predictor, svc, encoder, fa]:
                processing_steps.append(("3. Face Recognition Init", "Failed"))
                flash('Face recognition system initialization failed', 'danger')
                return render_template('mark_attendance.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)
            processing_steps.append(("3. Face Recognition Init", "Success"))

            # Step 4: Camera Initialization
            processing_steps.append(("4. Camera Initialization", "Starting"))
            vs = None
            try:
                vs = VideoStream(src=0, usePiCamera=False).start()
                time.sleep(2.0)
                processing_steps.append(("4. Camera Initialization", "Success"))
            except Exception as e:
                processing_steps.append(("4. Camera Initialization", f"Failed: {str(e)}"))
                flash(f'Camera initialization failed: {str(e)}', 'danger')
                return render_template('mark_attendance.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)

            # Variables for processing
            attendance_records = {}
            late_employees = []
            action_feedback = {
                'blink': {'count': 0, 'required': 2, 'last_detected': None},
                'movement': {'count': 0, 'required': 1, 'last_detected': None}
            }
            previous_face_position = None
            frame_count = 0
            face_detected_frames = 0
            last_status_update = time.time()
            recognized_employee = None
            last_recognition_time = time.time()

            try:
                while True:
                    frame = vs.read()
                    if frame is None:
                        continue

                    frame = imutils.resize(frame, width=800)
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_frame = cv2.equalizeHist(gray_frame)
                    gray_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
                    
                    faces = detector(gray_frame, 0)

                    # Information display frame
                    info_frame = np.zeros((500, 800, 3), dtype="uint8")
                    cv2.rectangle(info_frame, (0, 0), (800, 500), (50, 50, 50), -1)
                    
                    # Display processing information
                    cv2.putText(info_frame, "Check-In Processing Steps", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
                    
                    # Display last 8 processing steps
                    for i, (step, status) in enumerate(processing_steps[-8:]):
                        color = (0, 255, 0) if "Success" in status else (255, 255, 255) if "Starting" in status else (0, 0, 255)
                        cv2.putText(info_frame, f"{step}: {status}", (20, 70 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    
                    # Current status display
                    cv2.putText(info_frame, "Current Status:", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    if len(faces) == 0:
                        status_msg = "Please position your face in the frame"
                        cv2.putText(info_frame, status_msg, (20, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                    else:
                        status_msg = "Face detected - Verifying liveness"
                        cv2.putText(info_frame, status_msg, (20, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        
                        cv2.putText(info_frame, f"Blinks: {action_feedback['blink']['count']}/{action_feedback['blink']['required']}", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        cv2.putText(info_frame, f"Movements: {action_feedback['movement']['count']}/{action_feedback['movement']['required']}", (20, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Display instructions
                    cv2.putText(info_frame, "Instructions:", (20, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(info_frame, "1. Look straight at the camera", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(info_frame, "2. Blink naturally 2 times", (20, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    for face in faces:
                        face_detected_frames += 1
                        (x, y, w, h) = face_utils.rect_to_bb(face)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Liveness detection
                        is_live, ear, moved, blink_detected = simple_liveness_detection(face, gray_frame, predictor, frame_count)
                        
                        # Display EAR information
                        cv2.putText(frame, f"EAR: {ear:.2f}", (x, y - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        
                        # Blink detection handling
                        if blink_detected:
                            if action_feedback['blink']['last_detected'] is None or (time.time() - action_feedback['blink']['last_detected']) > 0.8:
                                action_feedback['blink']['count'] += 1
                                action_feedback['blink']['last_detected'] = time.time()
                                processing_steps.append(("5. Liveness Check", f"Blink {action_feedback['blink']['count']} detected"))
                                cv2.putText(frame, "BLINK DETECTED", (x, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                
                                # Visual feedback for eyes
                                landmarks = predictor(gray_frame, face)
                                landmarks = face_utils.shape_to_np(landmarks)
                                for (ex, ey) in landmarks[36:48]:
                                    cv2.circle(frame, (ex, ey), 1, (0, 0, 255), -1)

                        # Movement detection
                        if moved and previous_face_position:
                            if action_feedback['movement']['last_detected'] is None or (time.time() - action_feedback['movement']['last_detected']) > 2.0:
                                action_feedback['movement']['count'] += 1
                                action_feedback['movement']['last_detected'] = time.time()
                                processing_steps.append(("5. Liveness Check", f"Movement {action_feedback['movement']['count']} detected"))
                                cv2.putText(frame, "MOVEMENT DETECTED", (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        previous_face_position = (x, y, w, h)

                        # Check if all requirements are met
                        requirements_met = (
                            action_feedback['blink']['count'] >= action_feedback['blink']['required'] and
                            action_feedback['movement']['count'] >= action_feedback['movement']['required']
                        )

                        if requirements_met and face_detected_frames > 10:
                            try:
                                processing_steps.append(("6. Face Recognition", "Starting"))
                                face_aligned = fa.align(frame, gray_frame, face)
                                if face_aligned is None:
                                    processing_steps.append(("6. Face Recognition", "Alignment failed"))
                                    continue

                                # Face recognition
                                predictions = predict(face_aligned, svc)
                                
                                # Handle different prediction formats
                                if isinstance(predictions, tuple) and len(predictions) >= 2:
                                    pred, prob = predictions[0], predictions[1]
                                elif isinstance(predictions, (list, np.ndarray)):
                                    if len(predictions) >= 2:
                                        pred, prob = predictions[0], predictions[1]
                                    else:
                                        pred, prob = -1, 0.0
                                else:
                                    pred, prob = -1, 0.0

                                # Ensure scalar values
                                pred = pred[0] if isinstance(pred, (list, np.ndarray)) else pred
                                prob = prob[0] if isinstance(prob, (list, np.ndarray)) else prob
                                prob = float(prob) if not isinstance(prob, float) else prob

                                if pred != -1 and prob > 0.4:
                                    employee_name = encoder.inverse_transform([int(pred)])[0]
                                    processing_steps.append(("6. Face Recognition", f"Recognized: {employee_name}"))
                                    recognized_employee = employee_name
                                    last_recognition_time = time.time()
                                    
                                    employee = User.query.filter_by(username=employee_name).first()
                                    if not employee:
                                        processing_steps.append(("7. Database Update", "User not found"))
                                        continue

                                    today = datetime.now().date()
                                    now_time = datetime.now().time()
                                    current_hour = datetime.now().hour
                                    
                                    # Check for late arrival (after 8:30 AM)
                                    is_late = current_hour >= 8 and datetime.now().minute > 30
                                    if is_late:
                                        late_employees.append(employee_name)
                                        processing_steps.append(("8. Attendance Marking", "Late arrival detected"))

                                    # Check for existing attendance record
                                    attendance = Attendance.query.filter_by(
                                        user_id=employee.id, 
                                        date=today
                                    ).first()

                                    if not attendance:
                                        # Create new check-in record
                                        processing_steps.append(("8. Attendance Marking", "Creating new check-in record"))
                                        attendance = Attendance(
                                            user_id=employee.id,
                                            date=today,
                                            month_year=today.replace(day=1),
                                            timestamp=datetime.now(),
                                            time_in=now_time,
                                            time_out=None,
                                            present=True,
                                            late_check=is_late,
                                            hours=0.0
                                        )
                                        db.session.add(attendance)
                                    elif attendance.time_in is None:
                                        # Update existing record with check-in time
                                        processing_steps.append(("8. Attendance Marking", "Updating check-in time"))
                                        attendance.time_in = now_time
                                        attendance.late_check = is_late
                                        attendance.present = True
                                    
                                    db.session.commit()
                                    attendance_records[employee_name] = attendance
                                    processing_steps.append(("8. Attendance Marking", "Check-in recorded"))
                                    
                                    # Visual feedback
                                    cv2.putText(frame, "CHECK-IN RECORDED", (x, y - 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                    cv2.putText(frame, f"RECOGNIZED: {employee_name}", (x, y - 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                                    cv2.putText(frame, f"Confidence: {prob:.2f}", (x, y - 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

                                    # Reset for next verification
                                    action_feedback['blink']['count'] = 0
                                    action_feedback['movement']['count'] = 0
                                    face_detected_frames = 0

                            except Exception as e:
                                processing_steps.append(("Error", f"Recognition failed: {str(e)}"))
                                db.session.rollback()

                    # Display recognized employee if recently detected
                    if recognized_employee and (time.time() - last_recognition_time) < 5:
                        cv2.putText(info_frame, f"Recognized: {recognized_employee}", (400, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    # Display camera feeds
                    cv2.imshow("Check-In Verification", frame)
                    cv2.imshow("Processing Information", info_frame)
                    
                    key = cv2.waitKey(50) & 0xFF
                    if key == ord("q"):
                        break

                    frame_count += 1

            except Exception as e:
                processing_steps.append(("Error", f"Processing error: {str(e)}"))
                flash(f'Error processing check-in: {str(e)}', 'danger')
            finally:
                if vs:
                    vs.stop()
                cv2.destroyAllWindows()

            if attendance_records:
                report = generate_attendance_report(attendance_records, late_employees)
                flash('Check-in recorded successfully!', 'success')
                return render_template('attendance_report.html',
                                    report=report,
                                    recognized_employee=recognized_employee,
                                    processing_steps=processing_steps,
                                    check_in=True)  # Flag to indicate check-in report

            flash('No check-in records were processed', 'warning')
            return render_template('mark_attendance.html',
                                recognized_employee=recognized_employee,
                                processing_steps=processing_steps)

        except Exception as e:
            db.session.rollback()
            processing_steps.append(("System Error", f"{str(e)}"))
            flash(f'System error: {str(e)}', 'danger')
            return render_template('mark_attendance.html',
                                processing_steps=processing_steps)

    return render_template('mark_attendance.html')

@app.route('/mark_your_attendance_out', methods=['GET', 'POST'])
def mark_your_attendance_out():
    if request.method == 'POST':
        try:
            # Step 1: Geolocation Verification
            processing_steps = []
            status_messages = []
            
            processing_steps.append(("1. Location Verification", "Starting"))
            if not verify_haramaya_university_location():
                processing_steps.append(("1. Location Verification", "Failed - Not in campus"))
                flash('You must be within Haramaya University campus to mark attendance', 'danger')
                return render_template('mark_attendance_out.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)
            processing_steps.append(("1. Location Verification", "Success"))

            # Step 2: Security Checks
            processing_steps.append(("2. Security Checks", "Starting"))
            if not security_checks_passed():
                processing_steps.append(("2. Security Checks", "Failed"))
                return render_template('mark_attendance_out.html', 
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)
            processing_steps.append(("2. Security Checks", "Success"))

            # Step 3: Face Recognition Initialization
            processing_steps.append(("3. Face Recognition Init", "Starting"))
            detector, predictor, svc, encoder, fa = initialize_face_recognition()
            if None in [detector, predictor, svc, encoder, fa]:
                processing_steps.append(("3. Face Recognition Init", "Failed"))
                flash('Face recognition system initialization failed', 'danger')
                return render_template('mark_attendance_out.html', processing_steps=processing_steps,status_messages=status_messages)
            processing_steps.append(("3. Face Recognition Init", "Success"))

            # Step 4: Camera Initialization
            processing_steps.append(("4. Camera Initialization", "Starting"))
            vs = None
            try:
                vs = VideoStream(src=0, usePiCamera=False).start()
                time.sleep(2.0)
                processing_steps.append(("4. Camera Initialization", "Success"))
            except Exception as e:
                processing_steps.append(("4. Camera Initialization", f"Failed: {str(e)}"))
                flash(f'Camera initialization failed: {str(e)}', 'danger')
                return render_template('mark_attendance_out.html', processing_steps=processing_steps,status_messages=status_messages)

            # Variables for processing
            attendance_records = {}
            late_employees = []
            action_feedback = {
                'blink': {'count': 0, 'required': 2, 'last_detected': None},  # Reduced requirements
                'movement': {'count': 0, 'required': 1, 'last_detected': None}  # Reduced requirements
            }
            previous_face_position = None
            frame_count = 0
            face_detected_frames = 0
            last_status_update = time.time()
            recognized_employee = None  # To store recognized employee info
            last_recognition_time = time.time()

            try:
                while True:
                    frame = vs.read()
                    if frame is None:
                        continue

                    frame = imutils.resize(frame, width=800)
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Apply histogram equalization for low-light conditions
                    gray_frame = cv2.equalizeHist(gray_frame)
                    
                    # Apply Gaussian blur to reduce noise
                    gray_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
                    
                    faces = detector(gray_frame, 0)

                    # Create information frame
                    info_frame = np.zeros((500, 800, 3), dtype="uint8")
                    cv2.rectangle(info_frame, (0, 0), (800, 500), (50, 50, 50), -1)
                    
                    # Display title
                    cv2.putText(info_frame, "Attendance Processing Steps", (20, 30),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
                    
                    # Display processing steps (last 8 steps)
                    for i, (step, status) in enumerate(processing_steps[-8:]):
                        color = (0, 255, 0) if "Success" in status else (255, 255, 255) if "Starting" in status else (0, 0, 255)
                        cv2.putText(info_frame, f"{step}: {status}", (20, 70 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    
                    # Display current status
                    cv2.putText(info_frame, "Current Status:", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    if len(faces) == 0:
                        status_msg = "Please position your face in the frame"
                        cv2.putText(info_frame, status_msg, (20, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                    else:
                        status_msg = f"Face detected - Verifying liveness"
                        cv2.putText(info_frame, status_msg, (20, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        
                        cv2.putText(info_frame, f"Blinks: {action_feedback['blink']['count']}/{action_feedback['blink']['required']}", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        cv2.putText(info_frame, f"Movements: {action_feedback['movement']['count']}/{action_feedback['movement']['required']}", (20, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Display instructions
                    cv2.putText(info_frame, "Instructions:", (20, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(info_frame, "1. Look straight at the camera", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(info_frame, "2. Blink naturally 2 times", (20, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    for face in faces:
                        face_detected_frames += 1
                        (x, y, w, h) = face_utils.rect_to_bb(face)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        is_live, ear, moved, blink_detected = simple_liveness_detection(face, gray_frame, predictor, frame_count)
    
                        cv2.putText(frame, f"Eye Openness: {ear:.2f}", (x, y - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
                        if blink_detected:
                            cv2.putText(frame, "BLINK DETECTED", (x, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            if action_feedback['blink']['last_detected'] is None or (time.time() - action_feedback['blink']['last_detected']) > 0.8:
                                action_feedback['blink']['count'] += 1
                                action_feedback['blink']['last_detected'] = time.time()
                                processing_steps.append(("5. Liveness Check", f"Blink {action_feedback['blink']['count']} detected"))
                                cv2.putText(frame, "BLINK DETECTED", (x, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # Visual feedback - draw eyes in red when blinking
                                landmarks = predictor(gray_frame, face)
                                landmarks = face_utils.shape_to_np(landmarks)
                                for (ex, ey) in landmarks[36:48]:  # Eye landmarks
                                    cv2.circle(frame, (ex, ey), 1, (0, 0, 255), -1)

    # Track movement
                        if moved and previous_face_position:
                            if action_feedback['movement']['last_detected'] is None or (time.time() - action_feedback['movement']['last_detected']) > 2.0:
                                action_feedback['movement']['count'] += 1
                                action_feedback['movement']['last_detected'] = time.time()
                                processing_steps.append(("5. Liveness Check", f"Movement {action_feedback['movement']['count']} detected"))
                                cv2.putText(frame, "MOVEMENT DETECTED", (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        previous_face_position = (x, y, w, h)

                        # Check if all requirements are met
                        requirements_met = (
                            action_feedback['blink']['count'] >= action_feedback['blink']['required'] and
                            action_feedback['movement']['count'] >= action_feedback['movement']['required']
                        )

                        if requirements_met and face_detected_frames > 10:  # Require minimum frames
                            try:
                                
                                processing_steps.append(("6. Face Recognition", "Starting"))
                                face_aligned = fa.align(frame, gray_frame, face)
                                if face_aligned is None:
                                    processing_steps.append(("6. Face Recognition", "Alignment failed"))
                                    continue

                                pred, prob = predict(face_aligned, svc)
                                pred = pred[0] if isinstance(pred, np.ndarray) else pred
                                prob = prob[0] if isinstance(prob, np.ndarray) else prob
                                if isinstance(prob, list) or isinstance(prob, np.ndarray):
                                    prob = prob[0]
                                if pred != -1 and prob > 0.4:  # Lower confidence threshold
                                    employee_name = encoder.inverse_transform([int(pred)])[0]
                                    processing_steps.append(("6. Face Recognition", f"Recognized: {employee_name}"))
                                    recognized_employee = employee_name
                                    last_recognition_time = time.time()
                                    employee = User.query.filter_by(username=employee_name).first()
                                    if not employee:
                                        processing_steps.append(("7. Database Update", "User not found"))
                                        continue

                                    today = datetime.now().date()
                                    now_time = datetime.now().time()
                                    current_hour = datetime.now().hour
                                    
                                    
                                    is_late = current_hour >= 17
                                    if is_late:
                                        late_employees.append(employee_name)
                                        processing_steps.append(("8. Attendance Marking", "Late checkout detected"))

                                    attendance = Attendance.query.filter_by(user_id=employee.id, date=today).first()

                                    if not attendance:
                                        processing_steps.append(("8. Attendance Marking", "Creating new record"))
                                        attendance = Attendance(
                                            user_id=employee.id,
                                            date=today,month_year=today.replace(day=1),
                                            timestamp=datetime.now(),
                                            time_in=None,
                                            time_out=now_time,
                                            present=True,
                                            late_check=is_late
                                        )
                                        db.session.add(attendance)
                                    elif not attendance.time_out:
                                        processing_steps.append(("8. Attendance Marking", "Updating checkout time"))
                                        attendance.time_out = now_time
                                        attendance.late_check = is_late
                                        if attendance.time_in:
                                            time_in = datetime.combine(today, attendance.time_in)
                                            time_out = datetime.combine(today, now_time)
                                            working_hours = (time_out - time_in).total_seconds() / 3600
                                            if working_hours > 6:
                                                working_hours -= 1
                                            attendance.hours = round(working_hours, 2)
                                        else:
                                            attendance.hours = 0
                                    
                                    db.session.commit()
                                    attendance_records[employee_name] = attendance
                                    processing_steps.append(("8. Attendance Marking", "Success"))
                                    cv2.putText(frame, "ATTENDANCE RECORDED", (x, y - 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                    
                                    # Reset for next verification
                                    action_feedback['blink']['count'] = 0
                                    action_feedback['movement']['count'] = 0
                                    face_detected_frames = 0
                                    cv2.putText(frame, f"RECOGNIZED: {employee_name}", (x, y - 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                                    cv2.putText(frame, f"Confidence: {prob:.2f}", (x, y - 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)


                            except Exception as e:
                                processing_steps.append(("Error", f"Recognition failed: {str(e)}"))
                                db.session.rollback()

                    # Display camera feed and information frame
                    cv2.imshow("Attendance Verification", frame)
                    cv2.imshow("Processing Information", info_frame)
                    
                    key = cv2.waitKey(50) & 0xFF
                    if key == ord("q"):
                        break

                    frame_count += 1

            except Exception as e:
                processing_steps.append(("Error", f"Processing error: {str(e)}"))
                flash(f'Error processing attendance: {str(e)}', 'danger')
            finally:
                if vs:
                    vs.stop()
                cv2.destroyAllWindows()

            if attendance_records:
                report = generate_attendance_report(attendance_records, late_employees)
                flash('Attendance recorded successfully!', 'success')
                return render_template('attendance_report.html', 
                                    report=report,recognized_employee=recognized_employee,
                                    processing_steps=processing_steps,
                                    status_messages=status_messages[-10:])  # Show last 10 status messages

            flash('No attendance records were processed', 'warning')
            return render_template('mark_attendance_out.html',  recognized_employee=recognized_employee,
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)

        except Exception as e:
            db.session.rollback()
            processing_steps.append(("System Error", f"{str(e)}"))
            flash(f'System error: {str(e)}', 'danger')
            return render_template('mark_attendance_out.html',  recognized_employee=recognized_employee,
                                    processing_steps=processing_steps,
                                    status_messages=status_messages)

    return render_template('mark_attendance_out.html')

def simple_liveness_detection(face, gray_frame, predictor, frame_count):
    """Simplified liveness detection focusing on reliable blink detection"""
    try:
        # Initialize default values
        ear = 0.25
        blink_detected = False
        moved = False
        
        # Get facial landmarks (using only essential points)
        landmarks = predictor(gray_frame, face)
        landmarks = face_utils.shape_to_np(landmarks)
        
        # SIMPLIFIED EYE DETECTION -----------------------------------------
        # Use only 2 points per eye (top and bottom)
        left_eye_top = landmarks[37]
        left_eye_bottom = landmarks[41]
        right_eye_top = landmarks[44]
        right_eye_bottom = landmarks[46]
        
        # Calculate eye openness (vertical distance)
        left_eye_open = np.linalg.norm(left_eye_top - left_eye_bottom)
        right_eye_open = np.linalg.norm(right_eye_top - right_eye_bottom)
        
        # Normalize by face width to get consistent values
        face_width = np.linalg.norm(landmarks[0] - landmarks[16])
        if face_width > 0:
            left_ear = left_eye_open / face_width
            right_ear = right_eye_open / face_width
            ear = (left_ear + right_ear) / 2.0
        
        # FIXED THRESHOLD BLINK DETECTION ----------------------------------
        # Blink is detected when eyes are more than 30% more closed than normal
        blink_threshold = 0.15  # This works for most cases
        blink_detected = ear < blink_threshold
        
        # SIMPLE MOVEMENT DETECTION ----------------------------------------
        (x, y, w, h) = face_utils.rect_to_bb(face)
        
        if hasattr(simple_liveness_detection, 'prev_x'):
            # Check if moved more than 15% of face width
            moved = (abs(x - simple_liveness_detection.prev_x) > (w * 0.15))
        
        # Store current position for next frame
        simple_liveness_detection.prev_x = x
        simple_liveness_detection.prev_y = y
        
        # LIVENESS RESULT -------------------------------------------------
        is_live = blink_detected or moved
        
        return is_live, ear, moved, blink_detected
        
    except Exception as e:
        print(f"Liveness detection error: {str(e)}")
        return False, 0.25, False, False
def verify_haramaya_university_location():
    """Verify if the user is within Haramaya University campus"""
    try:
        # Haramaya University main campus coordinates (approximate)
        HARAMAYA_CAMPUS_CENTER = (9.3142, 42.1216)  # Latitude, Longitude
        CAMPUS_RADIUS = 9000000  # meters (adjust based on campus size)
        
        user_lat = float(request.form.get('latitude', 0))
        user_lon = float(request.form.get('longitude', 0))
        
        # Calculate distance from campus center
        distance = geodesic(HARAMAYA_CAMPUS_CENTER, (user_lat, user_lon)).meters
        
        if distance > CAMPUS_RADIUS:
            print(f"User is {distance:.2f} meters from campus center")
            return False
            
        return True
    except Exception as e:
        print(f"Location verification error: {str(e)}")
        return False


def detect_liveness(face, gray_frame, predictor, frame_count):
    """Enhanced liveness detection with eye blink and head movement"""
    landmarks = predictor(gray_frame, face)
    landmarks = face_utils.shape_to_np(landmarks)
    
    # Eye Aspect Ratio calculation
    left_eye = landmarks[42:48]
    right_eye = landmarks[36:42]
    ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
    
    # Head movement detection (simple position change between frames)
    (x, y, w, h) = face_utils.rect_to_bb(face)
    moved = False
    
    if frame_count > 0 and frame_count % 5 == 0:
        if hasattr(detect_liveness, 'prev_position'):
            prev_x, prev_y = detect_liveness.prev_position
            moved = abs(x - prev_x) > 10 or abs(y - prev_y) > 10
        detect_liveness.prev_position = (x, y)
    
    # Consider live if eyes are open or if there's movement
    is_live = ear > 0.25 or moved
    
    return is_live, ear, moved

def eye_aspect_ratio(eye):
    """Calculate eye aspect ratio for blink detection"""
    # Compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    
    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = np.linalg.norm(eye[0] - eye[3])
    
    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    
    return ear



# Helper Functions


def security_checks_passed():
    """Verify IP whitelisting and geofencing"""
    user_ip = request.remote_addr
    if user_ip not in AUTHORIZED_IPS:
        flash('Access denied: Unauthorized network.', 'danger')
        return False

    try:
        user_lat = float(request.form.get('latitude', 9.3142))
        user_lon = float(request.form.get('longitude', 42.1216))
        distance = geodesic(WORKPLACE_COORDINATES, (user_lat, user_lon)).meters
        if distance > 100:
            flash('Access denied: You are not within the allowed location.', 'danger')
            return False
    except Exception as e:
        flash(f'Error verifying location: {e}', 'danger')
        return False
    
    return True

def initialize_face_recognition():
    """Initialize all face recognition components"""
    try:
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('face_recognition_data/shape_predictor_68_face_landmarks.dat')
        
        with open("face_recognition_data/svc.sav", 'rb') as f:
            svc = pickle.load(f)
            
        encoder = LabelEncoder()
        encoder.classes_ = np.load('face_recognition_data/classes.npy')
        fa = FaceAligner(predictor, desiredFaceWidth=96)
        
        return detector, predictor, svc, encoder, fa
    except Exception as e:
        print(f"Face recognition init error: {str(e)}")
        return None, None, None, None, None

def generate_attendance_report(records, late_comers=None):
    """Generate a comprehensive attendance report."""
    if late_comers is None:
        late_comers = []

    total = len(records)
    num_late = len(late_comers)
    avg_hours = round(
        sum(r.hours if hasattr(r, 'hours') else 0 for r in records.values()) / total,
        2
    ) if total else 0

    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_employees': total,
        'on_time': total - num_late,
        'late_comers': num_late,
        'average_hours': avg_hours,
        'details': {name: {
            'time_in': rec.time_in,
            'time_out': rec.time_out,
            'hours': rec.hours
        } for name, rec in records.items()}
    }
    return report


@app.route('/attendance_success_out')
def attendance_success_out():
    return render_template('attendance_success_out.html')

training_status = {
    'is_running': False,
    'progress': 0,
    'message': 'Ready to start training',
    'total_images': 0,
    'processed_images': 0,
    'people_count': 0,
    'current_person': None
}

def visualize_data(encodings, labels):
    """Visualize face encodings using t-SNE dimensionality reduction"""
    try:
        # Reduce dimensions to 2D using t-SNE
        tsne = TSNE(n_components=2, random_state=42)
        embedded = tsne.fit_transform(encodings)
        
        # Create a new figure
        plt.figure(figsize=(12, 10))
        unique_labels = set(labels)
        
        # Plot each person's encodings with a unique color
        for label in unique_labels:
            idx = np.array(labels) == label
            plt.scatter(embedded[idx, 0], embedded[idx, 1], label=label, alpha=0.7, s=100)
        
        # Customize the plot
        plt.title("Face Encodings Visualization (t-SNE)", fontsize=16)
        plt.xlabel("t-SNE Dimension 1", fontsize=12)
        plt.ylabel("t-SNE Dimension 2", fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save the visualization
        os.makedirs('face_recognition_data/visualizations', exist_ok=True)
        viz_path = 'face_recognition_data/visualizations/training_visualization.png'
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return viz_path
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return None

def train_model():
    """Main training function that processes images and trains the model"""
    global training_status
    
    try:
        # Initialize training status
        training_dir = 'face_recognition_data/training_dataset'
        training_status.update({
            'is_running': True,
            'progress': 0,
            'message': 'Initializing training...',
            'total_images': 0,
            'processed_images': 0,
            'people_count': 0,
            'current_person': None
        })
        
        # Step 1: Count images and people
        people = []
        image_count = 0
        valid_extensions = ('.jpg', '.jpeg', '.png')
        
        for person_name in os.listdir(training_dir):
            person_dir = os.path.join(training_dir, person_name)
            if os.path.isdir(person_dir):
                # Count valid images for this person
                person_images = [f for f in os.listdir(person_dir) 
                                if f.lower().endswith(valid_extensions)]
                if len(person_images) > 0:  # Only include people with images
                    people.append(person_name)
                    image_count += len(person_images)
        
        if len(people) == 0:
            training_status.update({
                'is_running': False,
                'message': 'Error: No valid training images found'
            })
            return
        
        training_status.update({
            'total_images': image_count,
            'people_count': len(people),
            'message': f'Found {image_count} images of {len(people)} people'
        })
        
        # Step 2: Process images and extract face encodings
        X = []
        y = []
        processed = 0
        failed_images = 0
        
        for person_name in people:
            training_status['current_person'] = person_name
            person_dir = os.path.join(training_dir, person_name)
            
            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith(valid_extensions):
                    continue
                
                img_path = os.path.join(person_dir, img_file)
                try:
                    # Load and convert image
                    image = cv2.imread(img_path)
                    if image is None:
                        raise ValueError("Could not read image")
                    
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Detect face locations
                    face_locations = face_recognition.face_locations(rgb_image, model='hog')
                    if not face_locations:
                        raise ValueError("No face detected")
                    
                    # Extract face encodings
                    encodings = face_recognition.face_encodings(rgb_image, face_locations)
                    if encodings:
                        # Use the first face found
                        X.append(encodings[0])
                        y.append(person_name)
                    
                    processed += 1
                    progress = int((processed / image_count) * 100)
                    
                    # Update training status
                    training_status.update({
                        'processed_images': processed,
                        'progress': progress,
                        'message': f'Processing {person_name} ({processed}/{image_count})'
                    })
                    
                    # Small delay to allow UI updates and simulate processing
                    time.sleep(0.05)
                
                except Exception as e:
                    print(f"Error processing {img_path}: {str(e)}")
                    failed_images += 1
                    # Optionally remove problematic images
                    # os.remove(img_path)
        
        # Step 3: Train the model if we have enough data
        if len(X) < 2:
            training_status.update({
                'is_running': False,
                'message': 'Error: Need at least 2 face images to train'
            })
            return
        
        training_status['message'] = 'Training model...'
        X = np.array(X)
        y = np.array(y)
        
        # Encode labels
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y)
        
        # Train SVM classifier
        svc = SVC(kernel='linear', probability=True)
        svc.fit(X, y_encoded)
        
        # Save model and encoder
        os.makedirs('models', exist_ok=True)
        model_path = 'face_recognition_data/face_recognition_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(svc, f)
        
        encoder_path = 'face_recognition_data/classes.npy'
        np.save(encoder_path, encoder.classes_)
        
        # Generate and save visualization
        viz_path = visualize_data(X, y)
        
        # Final training status update
        training_status.update({
            'is_running': False,
            'progress': 100,
            'message': f'Training complete! Model saved with {len(encoder.classes_)} people. {failed_images} images failed.',
            'current_person': None,
            'visualization_path': viz_path
        })
    
    except Exception as e:
        training_status.update({
            'is_running': False,
            'message': f'Training failed: {str(e)}'
        })
@app.route('/train')
def train_page():
    return render_template('train.html')

@app.route('/start_training', methods=['POST'])
def start_training():
    if training_status['is_running']:
        return jsonify({'status': 'error', 'message': 'Training already in progress'})
    
    # Start training in a separate thread
    Thread(target=train_model).start()
    return jsonify({'status': 'success', 'message': 'Training started'})

@app.route('/training_status')
def get_training_status():
    return jsonify(training_status)
@app.route('/admin/messages')
def admin_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('admin_dashboard.html', messages=messages)

@app.route('/not_authorised')
def not_authorised():
	return render_template('not_authorised.html')

@app.route('/view_attendance_home', methods=['GET'])
@login_required
def view_attendance_home():
    try:
        # Current date and calculate date range for the week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_dates = [week_start + timedelta(days=i) for i in range(7)]

        # 1. Basic Employee Counts
        total_employees = User.query.filter_by(is_admin=False).count()
        present_today = Present.query.filter_by(date=today, present=True).count()
        absent_today = total_employees - present_today

        # 2. Today's Attendance Details with Department Info
        today_attendance = db.session.query(
            User.username,
            User.department,
            Present.present,
            Present.check_in,
            Present.check_out,
            func.timediff(Present.check_out, Present.check_in).label('work_duration')
        ).join(Present, User.id == Present.user_id).filter(Present.date == today).all()

        # 3. Weekly Attendance Summary
        weekly_summary = db.session.query(
            func.date(Present.date).label('day'),
            func.count(case((Present.present == True, 1))).label('present_count'),
            func.count(case((Present.present == False, 1))).label('absent_count')
        ).filter(Present.date >= week_start, Present.date <= today).group_by(func.date(Present.date)).all()

        # 4. Department-wise Breakdown
        dept_stats = db.session.query(
            User.department,
            func.count(User.id).label('total'),
            func.count(case((Present.present == True, 1))).label('present'),
            func.round(func.avg(func.timediff(Present.check_out, Present.check_in)), 2).label('avg_hours')
        ).join(Present, User.id == Present.user_id).filter(Present.date == today).group_by(User.department).all()

        # 5. Late Arrivals Today
        late_arrivals = db.session.query(
            User.username,
            Present.check_in
        ).join(Present, User.id == Present.user_id).filter(
            Present.date == today,
            Present.present == True,
            func.time(Present.check_in) > '09:30:00'
        ).order_by(Present.check_in).all()

        return render_template(
            'view_attendance_home.html',
            today=today.strftime('%A, %d %B %Y'),
            total_employees=total_employees,
            present_today=present_today,
            absent_today=absent_today,
            attendance_details=today_attendance,
            weekly_summary=weekly_summary,
            week_dates=week_dates,
            dept_stats=dept_stats,
            late_arrivals=late_arrivals,
            current_week=week_start.strftime('%d %b') + " - " + today.strftime('%d %b %Y')
        )

    except Exception as e:
        current_app.logger.error(f"Error fetching attendance data: {str(e)}")
        flash('Error loading attendance data', 'danger')
        return redirect(url_for('view_attendance_home'))

@app.route('/view_attendance_date', methods=['GET', 'POST'])
def view_attendance_date():
    if not request.user.is_authenticated or request.user.username != 'admin':
        return redirect('not-authorised')
    
    qs = None
    time_qs = None
    present_qs = None

    if request.method == 'POST':
        form = DateForm(request.form)
        if form.validate():
            date = form.date.data
            print("date:" + str(date))
            time_qs = Time.query.filter_by(date=date).all()
            present_qs = Present.query.filter_by(date=date).all()
            if time_qs or present_qs:
                qs = hours_vs_employee_given_date(present_qs, time_qs)
                return render_template('recognition/view_attendance_date.html', form=form, qs=qs)
            else:
                flash('No records for selected date.', 'warning')
                return redirect('view-attendance-date')
    else:
        form = DateForm()
    
    return render_template('recognition/view_attendance_date.html', form=form, qs=qs)

@app.route('/view_attendance_employee', methods=['GET', 'POST'])
def view_attendance_employee():
    if not request.user.is_authenticated or request.user.username != 'admin':
        return redirect('not-authorised')

    qs = None
    time_qs = None
    present_qs = None

    if request.method == 'POST':
        form = UsernameAndDateForm(request.form)
        if form.validate():
            username = form.username.data
            if username_present(username):
                u = User.query.filter_by(username=username).first()
                time_qs = Time.query.filter_by(user=u).all()
                present_qs = Present.query.filter_by(user=u).all()
                date_from = form.date_from.data
                date_to = form.date_to.data
                if date_to < date_from:
                    flash('Invalid date selection.', 'warning')
                    return redirect('view-attendance-employee')
                else:
                    time_qs = Time.query.filter(Time.date >= date_from, Time.date <= date_to).order_by(Time.date.desc()).all()
                    present_qs = Present.query.filter(Present.date >= date_from, Present.date <= date_to).order_by(Present.date.desc()).all()
                    if time_qs or present_qs:
                        qs = hours_vs_date_given_employee(present_qs, time_qs, admin=True)
                        return render_template('recognition/view_attendance_employee.html', form=form, qs=qs)
                    else:
                        flash('No records for selected duration.', 'warning')
                        return redirect('view-attendance-employee')
            else:
                flash('No such username found.', 'warning')
                return redirect('view-attendance-employee')
    else:
        form = UsernameAndDateForm()
    
    return render_template('recognition/view_attendance_employee.html', form=form, qs=qs)

class DateRangeForm(FlaskForm):
    date_from = DateField('From Date', validators=[DataRequired()])
    date_to = DateField('To Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Routes


@app.route('/employee/attendance', methods=['GET', 'POST'])
@login_required
def view_my_attendance_employee_login():
    form = DateRangeForm()
    time_qs = None
    present_qs = None
    
    if form.validate_on_submit():
        date_from = form.date_from.data
        date_to = form.date_to.data
        
        # Get attendance records for the selected date range
        time_qs = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= date_from,
            Attendance.date <= date_to
        ).order_by(Attendance.date.desc()).all()
        
        # Get present days count for visualization
        present_qs = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= date_from,
            Attendance.date <= date_to
        ).all()
        
        if not time_qs:
            flash('No attendance records found for the selected period.', 'info')
    
    # Default to current month if no date range selected
    if not time_qs and request.method == 'GET':
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
        
        time_qs = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= first_day,
            Attendance.date <= last_day
        ).order_by(Attendance.date.desc()).all()
        
        present_qs = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= first_day,
            Attendance.date <= last_day
        ).all()
    
    return render_template('view_my_attendance_employee_login.html', form=form, time_qs=time_qs, present_qs=present_qs)

@app.route('/api/attendance/stats')
@login_required
def get_attendance_stats():
    # Get stats for dashboard widgets
    today = date.today()
    month_start = today.replace(day=1)
    
    total_days = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= month_start,
        Attendance.date <= today
    ).count()
    
    present_days = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.present == True,
        Attendance.date >= month_start,
        Attendance.date <= today
    ).count()
    
    total_hours = db.session.query(db.func.sum(Attendance.hours)).filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= month_start,
        Attendance.date <= today
    ).scalar() or 0
    
    overtime_hours = db.session.query(db.func.sum(Attendance.overtime_hours)).filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= month_start,
        Attendance.date <= today
    ).scalar() or 0
    
    return jsonify({
        'total_days': total_days,
        'present_days': present_days,
        'attendance_rate': round((present_days / total_days * 100) if total_days > 0 else 0, 1),
        'total_hours': round(total_hours, 1),
        'overtime_hours': round(overtime_hours, 1)
    })
def datetimeformat(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value
##########################################################################################
@app.route('/')
def index():
    return render_template('nav.html')

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        abort(403)
    
    search_query = request.args.get('search', '') or request.form.get('search', '')

    if request.method == 'POST':
        # Handle employee selection
        if 'select_employee' in request.form:
            employee_id = request.form.get('employee_id')
            employee = Employee.query.filter_by(id=employee_id, is_registered=False).first()

            if not employee or employee.is_registered:
                flash('Employee not found or already registered', 'danger')
                return redirect(url_for('register', search=search_query))

            # Verify department exists
            department = Department.query.get(employee.department_id)
            if not department:
                flash('Invalid department assignment for the employee', 'danger')
                return redirect(url_for('register', search=search_query))

            session['registering_employee'] = {
                'id': employee.id,
                'username': employee.username,
                'email': employee.email,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'department_id': employee.department_id,
                'department_name': department.name,
                'dob': employee.dob,
                'gender': employee.gender,
                'contact_number': employee.contact_number,
                'address': employee.address,
                'designation': employee.designation,
                'employee_type': employee.employee_type,
                'date_of_joining': employee.date_of_joining,
                'salary_structure': employee.salary_structure,
                'bank_account_details': employee.bank_account_details,
                'account_number': employee.account_number
            }
            return redirect(url_for('register'))

        # Handle final registration
        elif 'complete_registration' in request.form:
            if 'registering_employee' not in session:
                flash('Registration session expired', 'danger')
                return redirect(url_for('register'))

            employee_data = session['registering_employee']
            employee = db.session.get(Employee, employee_data['id'])

            if not employee or employee.is_registered:
                flash('Invalid employee or already registered', 'danger')
                return redirect(url_for('register'))

            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html',
                                        employee=employee_data,
                                        search_query=search_query)

            # Verify department still exists
            department = db.session.get(Department, employee_data['department_id'])
            if not department:
                flash('Department no longer exists', 'danger')
                return render_template('register.html',
                                        employee=employee_data,
                                        search_query=search_query)

            try:
                # Create user account
                new_user = User(
                    username=employee.username,
                    employee_id=str(employee.id),
                    dob=employee.dob,
                    gender=employee.gender,
                    contact_number=employee.contact_number,
                    email=employee.email,
                    address=employee.address,
                    department_id=employee.department_id,
                    designation=employee.designation,
                    employee_type=employee.employee_type,
                    date_of_joining=employee.date_of_joining,
                    salary_structure=employee.salary_structure,
                    bank_account_details=employee.bank_account_details,
                    account_number=employee.account_number,
                    password_hash=generate_password_hash(password)
                )

                employee.is_registered = True

                db.session.add(new_user)
                db.session.commit()

                session.pop('registering_employee', None)
                flash('Registration successful!', 'success')
                return redirect(url_for('register'))

            except Exception as e:
                db.session.rollback()
                flash(f'Registration failed: {str(e)}', 'danger')
                return render_template('register.html',
                                        employee=employee_data,
                                        search_query=search_query)

        # Handle employee editing
        elif 'edit_employee' in request.form:
            employee_id = request.form.get('edit_employee_id')
            employee = Employee.query.get_or_404(employee_id)

            # Get new department
            new_department_id = request.form.get('department_id')
            department = Department.query.get(new_department_id)
            if not department:
                flash('Invalid department selected', 'danger')
                return redirect(url_for('register', search=search_query))

            # Update employee fields
            employee.username = request.form.get('username')
            employee.email = request.form.get('email')
            employee.department_id = new_department_id

            # Update corresponding user if registered
            if employee.is_registered:
                user = User.query.filter_by(employee_id=str(employee.id)).first()
                if user:
                    user.username = employee.username
                    user.email = employee.email
                    user.department_id = employee.department_id
                    user.department = department.name

            try:
                db.session.commit()
                flash('Employee updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating employee: {str(e)}', 'danger')

            return redirect(url_for('register', search=search_query))

    # GET request - show appropriate page
    query = Employee.query.filter_by(is_registered=False)

    if search_query:
        query = query.filter(
            (Employee.first_name.ilike(f'%{search_query}%')) |
            (Employee.last_name.ilike(f'%{search_query}%')) |
            (Employee.username.ilike(f'%{search_query}%')) |
            (Employee.email.ilike(f'%{search_query}%'))
        )

    unregistered_employees = query.all()
    departments = Department.query.order_by('name').all()

    if 'registering_employee' in session:
        return render_template('register.html',
                                employee=session['registering_employee'],
                                departments=departments,
                                search_query=search_query)
    else:
        return render_template('register.html',
                                employees=unregistered_employees,
                                departments=departments,
                                search_query=search_query)
class Time(db.Model):
    __tablename__ = 'time_entries'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='time_entries')
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Time {self.timestamp}>"
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Setting {self.name}={self.value}>'
    
@app.cli.command('seed_departments')
def seed_departments():
    departments = [
        "Recruitment and Staffing",
        "Training and Development",
        "Performance Management",
        "Compensation and Benefits",
        "Policy and Procedure Development",
        "Employee Relations and Welfare",
        "Human Resource Information Systems (HRIS)",
        "Records and Personnel Administration"
    ]
    for name in departments:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name))
    db.session.commit()
    print("Departments seeded successfully.")
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', 'No Subject')  # Default if subject not provided
        message = request.form.get('message')
        
        # Validate required fields
        if not all([name, email, message]):
            return jsonify({
                "success": False,
                "message": "Please fill in all required fields."
            }), 400

        # Save to database (if you have this setup)
        if db and ContactMessage:
            new_message = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                content=message
            )
            db.session.add(new_message)
            db.session.commit()

        # Email configuration
        admin_email = "geddikriss@gmail.com"  # Replace with actual admin email
        sender_email = "noreply@haramaya.edu.et"  # Your no-reply email
        
        # Create email message
        msg = Message(
            subject=f"New Contact Form Submission: {subject}",
            sender=sender_email,
            recipients=[admin_email],
            reply_to=email  # So admin can reply directly to the sender
        )
        
        # Email body with better formatting
        msg.body = f"""
        You have received a new message from the Haramaya University contact form:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        
        --------------------------
        This is an automated message. Please do not reply directly to this email.
        """
        
        # HTML version for email clients that support it
        msg.html = f"""
        <html>
            <body>
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <hr>
                <h3>Message:</h3>
                <p>{message.replace('\n', '<br>')}</p>
                <hr>
                <p style="color: #777; font-size: 0.9em;">
                    This is an automated message. Please do not reply directly to this email.
                </p>
            </body>
        </html>
        """
        
        # Send the email
        mail.send(msg)
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Your message has been sent successfully! We'll get back to you soon."
        })
        
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while sending your message. Please try again later."
        }), 500


@app.route('/reports')
def reports():
    # Fetch reports from the database
    reports = Report.query.order_by(Report.date.desc()).all()
    return render_template('reports.html', reports=reports)

@app.route('/success')
def success():
    return "Employee added successfully!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):  # Using check_password() method
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard' if user.is_admin else 'employee_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


NOTIFICATION_TYPES = [
    'security', 'attendance', 'payroll', 
    'permission', 'message', 'general', 'bug'
]

@app.route('/notifications-page')
def notifications_page():
    return render_template('notifications.html')

@app.route('/api/permissions/<int:permission_id>/status', methods=['PUT'])
def update_permission_status(permission_id):
    try:
        data = request.get_json()
        new_status = data['status']
        
        if new_status not in ['pending', 'accepted', 'declined']:
            return jsonify({
                'success': False,
                'error': 'Invalid status'
            }), 400
            
        permission = Permission.query.get_or_404(permission_id)
        permission.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_status': permission.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
@app.route('/api/notifications')
def get_notifications():
    """Get all notifications for the current user from database"""
    # Get user ID from session (example)
    user_id = request.args.get('user_id', 1)  # In real app, get from auth
    
    # Get notifications from database
    notifications = Notification.query.filter(
        or_(
            Notification.employee_id == user_id,
            Notification.employee_id.is_(None)  # For broadcast notifications
        )
    ).order_by(
        Notification.is_read,
        Notification.date.desc()
    ).limit(100).all()
    
    # Format for frontend
    formatted_notifications = []
    for n in notifications:
        formatted_notifications.append({
            'id': n.id,
            'type': n.type,
            'title': f"{n.type.capitalize()} Notification",
            'message': n.message,
            'timestamp': n.date.isoformat(),
            'is_read': n.is_read,
            'link': n.metadata.get('link') if n.metadata else None
        })
    
    # Get unread count
    unread_count = Notification.query.filter_by(
        employee_id=user_id,
        is_read=False
    ).count()
    
    return jsonify({
        'notifications': formatted_notifications,
        'unread_count': unread_count
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_as_read(notification_id):
    """Mark a notification as read in database"""
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    
    # Notify all clients about the change
    socketio.emit('notification_update', {
        'type': 'read',
        'notification_id': notification_id,
        'user_id': notification.employee_id
    })
    
    return jsonify({'success': True})

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification from database"""
    notification = Notification.query.get_or_404(notification_id)
    user_id = notification.employee_id
    db.session.delete(notification)
    db.session.commit()
    
    # Notify all clients about the deletion
    socketio.emit('notification_update', {
        'type': 'delete',
        'notification_id': notification_id,
        'user_id': user_id
    })
    
    return jsonify({'success': True})

# Background thread to check for real events and create notifications
def notification_monitor():
    """Monitor system for events that should trigger notifications"""
    with app.app_context():
        while True:
            try:
                # Check for attendance issues
                check_attendance_issues()
                
                # Check for upcoming holidays
                check_upcoming_holidays()
                
                # Check for pending permissions
                check_pending_permissions()
                
                # Check for unread messages
                check_unread_messages()
                
                # Check for system issues
                check_system_issues()
                
            except Exception as e:
                app.logger.error(f"Error in notification monitor: {str(e)}")
            
            time.sleep(60)  # Check every minute

def check_attendance_issues():
    """Check for attendance anomalies and create notifications"""
    # Late arrivals (after 9:30 AM)
    late_cutoff = datetime.utcnow().replace(hour=9, minute=30, second=0, microsecond=0)
    late_employees = Attendance.query.filter(
        and_(
            Attendance.date == datetime.utcnow().date(),
            Attendance.time_in > late_cutoff.time(),
            Attendance.present == True
        )
    ).all()
    
    for attendance in late_employees:
        create_notification(
            attendance.user_id,
            'attendance',
            f"Late arrival recorded at {attendance.time_in.strftime('%H:%M')}",
            f"Employee {attendance.employee.name} arrived late today."
        )

def check_upcoming_holidays():
    """Notify about upcoming holidays"""
    upcoming = Holiday.query.filter(
        Holiday.date.between(
            datetime.utcnow().date(),
            (datetime.utcnow() + timedelta(days=7)).date()
        )
    ).all()
    
    for holiday in upcoming:
        create_notification(
            None,  # For all users
            'general',
            f"Upcoming holiday: {holiday.title}",
            holiday.message
        )

def check_pending_permissions():
    """Notify about pending permission requests"""
    pending = Permission.query.filter_by(status='pending').all()
    
    for perm in pending:
        create_notification(
            perm.manager_id,
            'permission',
            f"Permission request from {perm.employee.name}",
            f"Request: {perm.reason}",
            f"/permissions/{perm.id}"
        )

@app.route('/api/permissions/<int:permission_id>', methods=['GET'])
def get_permission(permission_id):
    try:
        permission = Permission.query.get_or_404(permission_id)
        
        response = {
            'id': permission.id,
            'permission_type': permission.permission_type,
            'reason': permission.permission_reason,
            'status': permission.status,
            'submitted_at': permission.submitted_at.isoformat(),
            'file_path': permission.file_path
        }
        
        if permission.user:
            response['user'] = {
                'id': permission.user.id,
                'username': permission.user.username
            }
            
        if permission.employee:
            response['employee'] = {
                'id': permission.employee.id,
                'full_name': permission.employee.full_name
            }
            
        return jsonify({
            'success': True,
            'permission': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/api/permissions/<int:permission_id>/<action>', methods=['POST'])
def handle_permission(permission_id, action):
    if action not in ['accept', 'decline']:
        return jsonify({'error': 'Invalid action'}), 400
    
    permission = Permission.query.get_or_404(permission_id)
    permission.status = 'accepted' if action == 'accept' else 'declined'
    
    # Create notification
    notification = Notification(
        employee_id=permission.user_id,
        type='permission',
        message=f'Your {permission.permission_type} request has been {action}ed',
        metadata={
            'title': f'Permission {action}ed',
            'link': f'/permissions/{permission.id}'
        }
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True})

def check_unread_messages():
    """Notify about unread contact messages"""
    unread = ContactMessage.query.filter_by(is_read=False).all()
    
    for msg in unread:
        create_notification(
            None,  # For admins
            'message',
            f"New message from {msg.name}",
            msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
            f"/messages/{msg.id}"
        )

def check_system_issues():
    """Check for system issues (simplified example)"""
    # In a real system, this would check monitoring metrics
    if False:  # Replace with actual check
        create_notification(
            None,  # For admins
            'bug',
            "System performance degradation",
            "Server response times have increased by 30%"
        )

def create_notification(user_id, n_type, title, message, link=None):
    """Helper to create a notification and broadcast it"""
    notification = Notification(
        employee_id=user_id,
        type=n_type,
        message=message,
        date=datetime.utcnow(),
        is_read=False,
        metadata={'title': title, 'link': link} if link else {'title': title}
    )
    db.session.add(notification)
    db.session.commit()
    
    # Broadcast to relevant users
    socketio.emit('new_notification', {
        'notification': {
            'id': notification.id,
            'type': n_type,
            'title': title,
            'message': message,
            'timestamp': notification.date.isoformat(),
            'is_read': False,
            'link': link
        },
        'user_id': user_id  # None means broadcast to all
    })
@app.route('/api/permissions', methods=['POST'])
def create_permission():
    try:
        data = request.get_json()
        
        permission = Permission(
            user_id=data['user_id'],
            employee_id=data.get('employee_id'),
            permission_type=data['permission_type'],
            permission_reason=data['permission_reason'],
            file_path=data.get('file_path'),
            status='pending'
        )
        
        db.session.add(permission)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'permission_id': permission.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
# WebSocket handlers
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    # Send user ID to server when connecting
    socketio.emit('register_user', {'user_id': request.args.get('user_id')})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


@app.route('/view_messages')
def view_messages():
    """Improved view_messages endpoint with real data"""
    # Get all contact messages
    contact_messages = ContactMessage.query.order_by(
        ContactMessage.timestamp.desc()
    ).all()
    
    # Get permission requests
    permission_requests = Permission.query.order_by(
        Permission.submitted_at.desc()
    ).all()
    
    # Get employee notifications (from database)
    employee_notifications = Notification.query.filter_by(
        type='message'
    ).order_by(
        Notification.date.desc()
    ).limit(10).all()
    
    # Get system bugs/errors
    system_bugs = Notification.query.filter_by(
        type='bug'
    ).order_by(
        Notification.date.desc()
    ).limit(10).all()
    
    # Format data for template
    formatted_messages = [{
        'name': msg.name,
        'email': msg.email,
        'content': msg.content,
        'timestamp': msg.timestamp,
        'is_read': msg.is_read
    } for msg in contact_messages]
    
    formatted_permissions = [{
        'id': perm.id,
        'employee_name': perm.employee.name,
        'reason': perm.reason,
        'submitted_at': perm.submitted_at,
        'status': perm.status,
        'file_path': perm.file_path
    } for perm in permission_requests]
    
    formatted_notifications = [{
        'sender': 'System' if not n.employee_id else n.employee.name,
        'content': n.message,
        'timestamp': n.date
    } for n in employee_notifications]
    
    formatted_bugs = [{
        'title': n.metadata.get('title', 'System Issue'),
        'description': n.message,
        'timestamp': n.date
    } for n in system_bugs]
    
    return render_template(
        'view_messages.html',
        contact_messages=formatted_messages,
        employee_notifications=formatted_notifications,
        permission_requests=formatted_permissions,
        system_bugs=formatted_bugs
    )
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



# Define default working hours for late calculation (adjust as needed)
DEFAULT_CLOCK_IN_TIME = datetime.strptime('09:30:00', '%H:%M:%S').time()

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or not session.get('is_admin'):
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('login')) # Use url_for

    try:
        # --- Fetch Data for Stats Cards ---
        total_num_of_emp = User.query.filter_by(is_admin=False).count()

        today = date.today()
        # Count present employees today where attendance is recorded
        present_today = db.session.query(func.count(Present.user_id.distinct())).filter(
            Present.date == today,
            Present.present == True
        ).scalar() or 0

        # Count late arrivals today
        late_today = db.session.query(func.count(Present.user_id.distinct())).filter(
            Present.date == today,
            Present.present == True,
            # Assuming clock_in is a datetime.time or similar comparable object
            Present.clock_in > DEFAULT_CLOCK_IN_TIME
        ).scalar() or 0

        
        absent_today = total_num_of_emp - present_today

        # Count pending leave requests
        pending_leave_requests = LeaveRequest.query.filter_by(status='pending').count()
        payroll_summary = {
            "total_payroll": 0,
            "average_salary": 0,
            "total_tax": 0,
            "total_pension": 0
        }
        employees_count = User.query.filter_by(is_admin=False).count()
        if employees_count > 0:
            # Mock data for demonstration
            payroll_summary["total_payroll"] = employees_count * 15000  # Average salary
            payroll_summary["average_salary"] = 15000
            payroll_summary["total_tax"] = employees_count * 2250  # 15% of average
            payroll_summary["total_pension"] = employees_count * 1050  # 7% of average
        recent_activities_data = []
        # Add a simulated activity for new employees
        # You would query your DB for recent users added
        new_employees_month = User.query.filter(
            User.registration_date >= today.replace(day=1) # Assuming a registration_date field
        ).count()
        if new_employees_month > 0:
            recent_activities_data.append({
                'title': 'New Employees Registered',
                'description': f'{new_employees_month} new employees registered this month.',
                'time': datetime.now() - timedelta(hours=1), # Simulate time
                'type': 'primary',
                'icon': 'user-plus'
            })

        # Add simulated activity for pending leave requests
        if pending_leave_requests > 0:
            recent_activities_data.append({
                'title': 'Pending Leave Requests',
                'description': f'You have {pending_leave_requests} leave requests requiring action.',
                'time': datetime.now() - timedelta(minutes=30), # Simulate time
                'type': 'warning',
                'icon': 'calendar-alt'
            })

        # Add simulated activity for system log (e.g., last training)
        last_training_log = SystemLog.query.filter_by(action='face_training').order_by(SystemLog.timestamp.desc()).first()
        if last_training_log:
            recent_activities_data.append({
                'title': 'Face Model Trained',
                'description': f'Last training completed at {last_training_log.timestamp.strftime("%Y-%m-%d %H:%M")}.',
                'time': last_training_log.timestamp,
                'type': 'info',
                'icon': 'graduation-cap'
            })

        # Sort activities by time (most recent first)
        recent_activities_data.sort(key=lambda x: x['time'], reverse=True)

        # --- Fetch Data for Today's Attendance Table ---
        # Get the latest attendance record for each employee today
        today_attendance_logs = db.session.query(
            Present.user_id,
            User.username,
            Present.present,
            Present.clock_in,
            Present.clock_out # Include clock_out if needed
        ).join(User).filter(Present.date == today).order_by(Present.clock_in.desc()).all() # Order by clock_in descending for latest entry if multiple

        
        employee_attendance_today = {}
        for log in today_attendance_logs:
            # Only keep the latest log for each user
            if log.user_id not in employee_attendance_today or log.clock_in > employee_attendance_today[log.user_id]['timestamp']:
                status = 'Present' if log.present else 'Absent' # Adjust logic based on your Present model
                if status == 'Present' and log.clock_in > DEFAULT_CLOCK_IN_TIME:
                    status = 'Late'

                employee_attendance_today[log.user_id] = {
                    'name': log.username,
                    'status': status,
                    'timestamp': log.clock_in # Use clock_in for the time shown
                }

        # Convert dictionary to list for template
        monitoring_logs = list(employee_attendance_today.values())

        
        return render_template('admin_dashboard.html',
            total_num_of_emp=total_num_of_emp,
            new_employees_month=new_employees_month, # Pass new employees count
            present_today=present_today,
            late_today=late_today,
            absent_today=absent_today,
            pending_leave_requests=pending_leave_requests,
            recent_activities=recent_activities_data, # Pass simulated activities
            monitoring_logs=monitoring_logs, # Pass processed attendance logs
            payroll_summary=payroll_summary
        )

    except Exception as e:
        current_app.logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Error loading dashboard data', 'danger')
        # Return template with default/empty data on error
        return render_template('admin_dashboard.html',
            total_num_of_emp=0,
            new_employees_month=0,
            present_today=0,
            late_today=0,
            absent_today=0,
            pending_leave_requests=0,
            recent_activities=[],
            monitoring_logs=[],
            payroll_summary={
                "total_payroll": 0,
                "average_salary": 0,
                "total_tax": 0,
                "total_pension": 0
            }
        )
@app.route('/api/payroll')
def api_payroll():
    period = request.args.get('period')  # e.g. "2024-05"
    if not period:
        
        period = datetime.now().strftime('%Y-%m')
    year, month = map(int, period.split('-'))

    employees = User.query.filter_by(is_active=True).all()
    data = []
    for emp in employees:
        # Payroll record for this month
        payroll = Payroll.query.filter(
            Payroll.user_id == emp.id,
            extract('year', Payroll.pay_period) == year,
            extract('month', Payroll.pay_period) == month
        ).first()

        # Attendance records for this month
        attendance_records = Attendance.query.filter(
            Attendance.user_id == emp.id,
            extract('year', Attendance.date) == year,
            extract('month', Attendance.date) == month
        ).all()
        work_hours = sum(a.hours or 0 for a in attendance_records)

        # Calculate payroll (use your function)
        calculated = calculate_employee_payroll(emp, period)
        net_pay = calculated.get('net_pay', 0)
        deductions = calculated.get('deductions', 0)
        basic_salary = calculated.get('basic_salary', 0)

        data.append({
            "id": emp.id,
            "employee_id": emp.employee_id,
            "name": emp.username,
            "department": emp.department.name if emp.department else "N/A",
            "basic_salary": basic_salary,
            "work_hours": work_hours,
            "deductions": deductions,
            "net_pay": net_pay,
            "status": "Paid" if payroll and payroll.processed else "Pending"
        })
    return jsonify(data)

def calculate_payroll_summary(employee_count):
    if employee_count == 0:
        return {
            "total_payroll": 0,
            "average_salary": 0,
            "total_tax": 0,
            "total_pension": 0
        }
    
    # In a real app, these would come from actual payroll calculations
    avg_salary = 15000
    return {
        "total_payroll": employee_count * avg_salary,
        "average_salary": avg_salary,
        "total_tax": employee_count * (avg_salary * 0.15),
        "total_pension": employee_count * (avg_salary * 0.07)
    }

def get_current_payroll_period():
    today = date.today()
    return {
        "month": today.month,
        "year": today.year,
        "period": "monthly"
    }
def get_payroll_records(period):
    """Fetch payroll records for the given period"""
    # This would be replaced with actual database queries in production
    # For now, we'll return mock data
    employees = User.query.filter_by(is_admin=False).all()
    
    records = []
    for emp in employees:
        
        records.append({
            'employee_id': emp.id,
            'employee_id_number': emp.employee_id or "N/A",
            'employee_name': emp.username,
            'department': emp.department or "N/A",
            'designation': emp.designation or "N/A",
            'salary_structure': "Monthly",
            'bank_account': emp.bank_name or "N/A",
            'account_number': emp.account_number or "N/A",
            'attendance_summary': {
                'total_worked_hours': 160,  # Mock data
                'late_days': 2 if emp.id % 5 == 0 else 0  # Every 5th employee is late
            },
            'calculated_net_salary': 15000 - (15000 * 0.15) - (15000 * 0.07),
            'payroll_data': {
                'basic_salary': 15000,
                'finalized_net_salary': 15000 - (15000 * 0.15) - (15000 * 0.07),
                'processed': emp.id % 3 != 0  # Every 3rd employee is not processed
            } if emp.id % 4 != 0 else None  # Every 4th employee has no payroll data
        })
    
    return records
@app.route('/api/payroll_summary')
def get_payroll_summary():
    try:
        # In a real application, you would calculate these from your database
        employees_count = User.query.filter_by(is_admin=False).count()
        
        if employees_count == 0:
            return jsonify({
                "total_payroll": 0,
                "average_salary": 0,
                "total_tax": 0,
                "total_pension": 0
            })
        
        # Mock data for demonstration
        avg_salary = 15000
        total_payroll = employees_count * avg_salary
        total_tax = employees_count * (avg_salary * 0.15)
        total_pension = employees_count * (avg_salary * 0.07)
        
        return jsonify({
            "total_payroll": round(total_payroll, 2),
            "average_salary": round(avg_salary, 2),
            "total_tax": round(total_tax, 2),
            "total_pension": round(total_pension, 2)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/recent-activities')
def api_recent_activities():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        
        system_logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(5).all()
        activities = []
        for log in system_logs:
            activities.append({
                'title': log.action, # Use action as title
                'description': log.details or 'No details provided.', # Assuming a 'details' field
                'time': log.timestamp.isoformat(), # Format timestamp for JSON
                'type': 'info', # Assign a type based on action if needed
                'icon': 'info-circle' # Assign an icon based on action if needed
            })

        # Example: Fetch last 3 leave requests with status changes (approved/rejected)
        recent_leave_updates = LeaveRequest.query.filter(LeaveRequest.status.in_(['approved', 'rejected'])) \
                                .order_by(LeaveRequest.updated_at.desc()) \
                                .limit(3).all() # Assuming an 'updated_at' field
        for req in recent_leave_updates:
            user = User.query.get(req.user_id)
            activities.append({
                'title': f'Leave Request {req.status.capitalize()}',
                'description': f'Request for {user.username if user else "Unknown"} from {req.start_date} to {req.end_date} was {req.status}.',
                'time': req.updated_at.isoformat(),
                'type': 'success' if req.status == 'approved' else 'danger',
                'icon': 'calendar-check' if req.status == 'approved' else 'calendar-times'
            })

        # Sort combined activities by time
        activities.sort(key=lambda x: x['time'], reverse=True)


        return jsonify(activities)

    except Exception as e:
        current_app.logger.error(f"Error fetching recent activities: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent activities'}), 500


@app.route('/api/attendance/weekly')
def api_weekly_attendance():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        week_offset = int(request.args.get('week_offset', 0))
        today = date.today()

        # Calculate the start and end dates of the target week
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)

        # Fetch attendance data for the week
        weekly_attendance_data = db.session.query(
            Present.date,
            func.count(Present.user_id.distinct()).filter(Present.present == True).label('present_count'),
            func.count(Present.user_id.distinct()).filter(Present.present == False).label('absent_count'),
            # Count late arrivals for each day
            func.count(Present.user_id.distinct()).filter(Present.present == True, Present.clock_in > DEFAULT_CLOCK_IN_TIME).label('late_count')
        ).filter(
            Present.date >= start_of_week,
            Present.date <= end_of_week
        ).group_by(Present.date).all()

        # Prepare data for the chart
        days_of_week = [(start_of_week + timedelta(days=i)).strftime('%a') for i in range(7)] # Mon, Tue, etc.
        present_counts = [0] * 7
        absent_counts = [0] * 7
        late_counts = [0] * 7

        # Map fetched data to days of the week
        for entry in weekly_attendance_data:
            day_index = (entry.date - start_of_week).days
            if 0 <= day_index < 7:
                present_counts[day_index] = entry.present_count
                absent_counts[day_index] = entry.absent_count
                late_counts[day_index] = entry.late_count # Include late counts


        chart_data = {
            'days': days_of_week,
            'present': present_counts,
            'absent': absent_counts,
            'late': late_counts # Add late data
        }

        # Calculate stats for the week
        total_employees = User.query.filter_by(is_admin=False).count()
        total_present_week = sum(present_counts)
        total_absent_week = sum(absent_counts)
        total_late_week = sum(late_counts)
        total_possible_attendance = total_employees * 7 # Assuming 7 working days for simplicity

        avg_presence = (total_present_week / total_possible_attendance) * 100 if total_possible_attendance > 0 else 0

        
        prev_week_start = start_of_week - timedelta(weeks=1)
        prev_week_end = end_of_week - timedelta(weeks=1)

        prev_week_attendance_data = db.session.query(
            func.count(Present.user_id.distinct()).filter(Present.present == True).label('present_count'),
            func.count(Present.user_id.distinct()).filter(Present.present == False).label('absent_count')
        ).filter(
            Present.date >= prev_week_start,
            Present.date <= prev_week_end
        ).first()

        prev_total_present = prev_week_attendance_data.present_count if prev_week_attendance_data else 0
        prev_total_absent = prev_week_attendance_data.absent_count if prev_week_attendance_data else 0
        prev_total_possible = total_employees * 7 # Assuming same total employees

        prev_avg_presence = (prev_total_present / prev_total_possible) * 100 if prev_total_possible > 0 else 0

        attendance_change = avg_presence - prev_avg_presence
        present_change = total_present_week - prev_total_present
        absent_change = total_absent_week - prev_total_absent


        stats = {
            'avg_presence': round(avg_presence, 1),
            'total_present': total_present_week,
            'total_absent': total_absent_week,
            'total_late': total_late_week,
            'attendance_change': round(attendance_change, 1),
            'present_change': present_change,
            'absent_change': absent_change
        }

        # Calculate additional metrics (Best Day, Worst Day, Consistency)
        metrics = {}
        if len(weekly_attendance_data) > 0:
            day_percentages = []
            for i in range(7):
                day_date = start_of_week + timedelta(days=i)
                day_data = next((item for item in weekly_attendance_data if item.date == day_date), None)
                pass  # Add your logic here
                present_count = day_data.present_count if day_data else 0
                day_total_employees = total_employees # Assuming total employees is constant
                percentage = (present_count / day_total_employees) * 100 if day_total_employees > 0 else 0
                day_percentages.append({'day': days_of_week[i], 'percentage': round(percentage, 1)})

            # Find best and worst day
            best_day = max(day_percentages, key=lambda x: x['percentage']) if day_percentages else {'day': 'N/A', 'percentage': 0}
            worst_day = min(day_percentages, key=lambda x: x['percentage']) if day_percentages else {'day': 'N/A', 'percentage': 0}

            best_day['change'] = 0 # Placeholder
            worst_day['change'] = 0 # Placeholder

            metrics['best_day'] = best_day
            metrics['worst_day'] = worst_day

            if day_percentages:
                percentages_only = [d['percentage'] for d in day_percentages]
                consistency_score = max(percentages_only) - min(percentages_only)
                metrics['consistency'] = {
                    'score': f'{round(consistency_score, 1)}%',
                     'trend': 'down' if consistency_score < (prev_avg_presence * 0.1) else 'up', # Arbitrary trend logic
                    'change': 0 # Placeholder for consistency change trend
                }
            else:
                metrics['consistency'] = {'score': 'N/A', 'trend': 'neutral', 'change': 0}

        else:
            metrics = {
                'best_day': {'day': 'N/A', 'percentage': 0, 'change': 0},
                'worst_day': {'day': 'N/A', 'percentage': 0, 'change': 0},
                'consistency': {'score': 'N/A', 'trend': 'neutral', 'change': 0}
            }


        # Generate available weeks for dropdown
        available_weeks = []
        # Show current week and a few past weeks
        for i in range(-5, 1): # Show current week (0) and 5 past weeks (-1 to -5)
            week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            available_weeks.append({
                'offset': i,
                'label': f'{week_start.strftime("%b %d")} - {week_end.strftime("%b %d, %Y")}'
            })
        # Sort available weeks from oldest to newest (for dropdown order)
        available_weeks.sort(key=lambda x: x['offset'])


        week_range = {
            'start': start_of_week.strftime('%b %d, %Y'),
            'end': end_of_week.strftime('%b %d, %Y')
        }

        return jsonify({
            'chart_data': chart_data,
            'stats': stats,
            'metrics': metrics,
            'available_weeks': available_weeks,
            'week_range': week_range
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching weekly attendance data: {str(e)}")
        return jsonify({'error': 'Failed to fetch weekly attendance data'}), 500


@app.route('/api/departments/distribution')
def api_department_distribution():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        filter_status = request.args.get('filter', 'all') # 'all', 'active', 'inactive'

        query = db.session.query(
            Department.name,
            func.count(User.id).label('employee_count')
        ).join(User, Department.id == User.department_id, isouter=True) # Use left join to include departments with no employees

        if filter_status == 'active':
            query = query.filter(User.is_active == True)
        elif filter_status == 'inactive':
            query = query.filter(User.is_active == False)
        # 'all' filter doesn't add a filter on User.is_active

        
        query = query.group_by(Department.name).order_by(Department.name)

        department_data = query.all()

        # Format data for the chart
        formatted_data = [{'name': row.name or 'No Department', 'count': row.employee_count or 0} for row in department_data]

        return jsonify({'data': formatted_data})

    except Exception as e:
        current_app.logger.error(f"Error fetching department distribution: {str(e)}")
        return jsonify({'error': 'Failed to fetch department distribution'}), 500

@app.route('/api/payroll')
def api_payroll_data():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        period = request.args.get('period')
        if not period:
            # Default to current month if no period is specified
            period = date.today().strftime('%Y-%m')

        # Fetch payroll data for the specified period
        payroll_records = db.session.query(
            Payroll,
            User.username.label('employee_name')
        ).join(User).filter(Payroll.month == period).all()

        employees_data = []
        total_basic_salary = 0
        total_allowances = 0
        total_deductions = 0
        total_net_pay = 0

        for record, employee_name in payroll_records:
            # Assuming your Payroll model has fields like basic_salary, allowances, deductions, net_pay, status
            employees_data.append({
                'id': record.user_id, # Employee ID
                'name': employee_name,
                'initials': ''.join([name[0] for name in employee_name.split()]).upper() if employee_name else '?',
                'avatar_color': 'primary', # You might determine color based on department or status
                'basicSalary': record.basic_salary,
                'allowances': record.allowances, # Assuming allowances are stored directly or calculated
                'deductions': record.deductions, # Assuming deductions are stored directly or calculated
                'netPay': record.net_pay,
                'status': record.status # Assuming a status field ('pending', 'processed', 'paid', etc.)
            })
            total_basic_salary += record.basic_salary or 0
            total_allowances += record.allowances or 0
            total_deductions += record.deductions or 0
            total_net_pay += record.net_pay or 0

        # Calculate summary
        summary = {
            'totalEmployees': User.query.filter_by(is_admin=False).count(), # Total employees in the system
            'totalPayroll': total_net_pay, # Total net pay for the period
            'basicSalary': total_basic_salary,
            'allowances': total_allowances,
            'deductions': total_deductions,
            # You might add counts for different payroll statuses here
        }

        # Fetch recent payslips (e.g., last 3 processed payslips regardless of period)
        recent_payslips_records = db.session.query(
            Payroll,
            User.username.label('employee_name')
        ).join(User).filter(Payroll.processed == True).order_by(Payroll.process_date.desc()).limit(3).all() # Assuming process_date field

        recent_payslips_data = []
        for record, employee_name in recent_payslips_records:
            recent_payslips_data.append({
                'employeeName': employee_name,
                'netPay': record.net_pay,
                'period': record.month,
                'status': record.status
            })


        return jsonify({
            'employees': employees_data,
            'summary': summary,
            'recentPayslips': recent_payslips_data
            # Add pagination data if needed
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching payroll data: {str(e)}")
        return jsonify({'error': 'Failed to fetch payroll data'}), 500
@app.route('/api/payroll')
def get_payroll_data():
    try:
        # Get query parameters
        period = request.args.get('period', 'monthly')
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
        
        
        employees = User.query.filter_by(is_admin=False).all()
        
        payroll_data = []
        
        for employee in employees:
            # Generate payroll data for each employee
            basic_salary = random.randint(5000, 25000)  # Random basic salary
            overtime_hours = random.randint(0, 20)      # Random overtime hours
            overtime_rate = basic_salary / 160 * 1.5    # 1.5x hourly rate
            overtime_pay = overtime_hours * overtime_rate
            
            # Calculate deductions
            tax = basic_salary * 0.15  # 15% tax
            pension = basic_salary * 0.07  # 7% pension
            other_deductions = random.randint(0, 500)
            total_deductions = tax + pension + other_deductions
            
            # Calculate net pay
            net_pay = basic_salary + overtime_pay - total_deductions
            
            # Determine pay date (last day of month)
            if month == 12:
                last_day = 31
            else:
                last_day = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
            
            pay_date = f"{year}-{month:02d}-{last_day:02d}"
            
            payroll_data.append({
                "employee_id": employee.id,
                "name": employee.username,
                "department": "Computer Science",  # Would come from department table in real app
                "basic_salary": round(basic_salary, 2),
                "overtime": round(overtime_pay, 2),
                "allowances": round(basic_salary * 0.1, 2),  # 10% allowances
                "tax": round(tax, 2),
                "pension": round(pension, 2),
                "deductions": round(total_deductions, 2),
                "net_pay": round(net_pay, 2),
                "bank_account": f"ETB {random.randint(100000, 999999)}",  # Mock bank account
                "pay_date": pay_date
            })
        
        return jsonify(payroll_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/payroll/process', methods=['POST'])
def api_process_payroll():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    period = data.get('period')
    payment_date_str = data.get('payment_date')

    if not period or not payment_date_str:
        return jsonify({'error': 'Missing period or payment date'}), 400

    try:
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()

        employees = User.query.filter_by(is_admin=False).all()
        processed_count = 0
        total_payroll_amount = 0

        for employee in employees:
            
            basic_salary = 5000 # Example: Fetch from Employee model or a salary table
            allowances = 500 # Example: Calculate based on roles, overtime, etc.
            income_tax_rate = 0.1 # Example: Based on salary scale
            pension_deduction = basic_salary * 0.07 # Example: 7% employee contribution
            other_deductions = 100 # Example: Union fees, loan repayments, etc.

            taxable_income = basic_salary + allowances - pension_deduction - other_deductions # Simplified taxable income

            # Calculate income tax based on taxable income bands (Ethiopian tax system)
            # This is a highly simplified example - you need the actual tax brackets
            income_tax = max(0, (taxable_income * income_tax_rate) - 50) # Example: 10% tax with 50 ETB deduction

            total_deductions = pension_deduction + income_tax + other_deductions
            net_pay = basic_salary + allowances - total_deductions

            # Check if a payroll record already exists for this employee and period
            existing_payroll = Payroll.query.filter_by(user_id=employee.id, month=period).first()

            if existing_payroll:
                # Update existing record
                existing_payroll.basic_salary = basic_salary
                existing_payroll.allowances = allowances
                existing_payroll.deductions = total_deductions
                existing_payroll.net_pay = net_pay
                existing_payroll.processed = True # Mark as processed
                existing_payroll.process_date = datetime.now()
                existing_payroll.payment_date = payment_date
                existing_payroll.status = 'processed' # Or 'pending_payment'
            else:
                # Create new record
                new_payroll = Payroll(
                    user_id=employee.id,
                    month=period,
                    basic_salary=basic_salary,
                    allowances=allowances,
                    deductions=total_deductions,
                    net_pay=net_pay,
                    processed=True, # Mark as processed
                    process_date=datetime.now(),
                    payment_date=payment_date,
                    status='processed' # Or 'pending_payment'
                )
                db.session.add(new_payroll)

            processed_count += 1
            total_payroll_amount += net_pay

        db.session.commit()

        # Log the payroll processing action
        new_log = SystemLog(
            action='payroll_processed',
            details=f'Payroll for period {period} processed for {processed_count} employees. Total Net Pay: ETB {total_payroll_amount:,.2f}',
            timestamp=datetime.now()
        )
        db.session.add(new_log)
        db.session.commit()


        return jsonify({'success': True, 'message': 'Payroll processed successfully', 'processed_count': processed_count})

    except Exception as e:
        db.session.rollback() # Rollback changes if any error occurs
        current_app.logger.error(f"Error processing payroll for period {period}: {str(e)}")
        # Log the error
        error_log = SystemLog(
            action='payroll_processing_error',
            details=f'Error processing payroll for period {period}: {str(e)}',
            timestamp=datetime.now()
        )
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'success': False, 'message': f'An error occurred during payroll processing: {str(e)}'}), 500


@app.route('/api/payroll/payslip/<int:employee_id>')
def api_get_payslip(employee_id):
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    period = request.args.get('period')
    if not period:
        # Default to current month if no period specified
        period = date.today().strftime('%Y-%m')

    try:
        payslip_record = Payroll.query.filter_by(user_id=employee_id, month=period).first()
        employee = User.query.get(employee_id)

        if not payslip_record or not employee:
            return jsonify({'error': 'Payslip or Employee not found for this period'}), 404

        # --- Format Payslip Data ---
        # This structure should match what your frontend expects for the modal
        payslip_data = {
            'companyName': 'Haramaya University', # Static or fetched from config
            'companyAddress': 'P.O. Box 138, Dire Dawa, Ethiopia', # Static or fetched
            'period': payslip_record.month,
            'paymentDate': payslip_record.payment_date.strftime('%Y-%m-%d') if payslip_record.payment_date else 'N/A',
            'payslipNumber': f'PS-{payslip_record.id}-{payslip_record.month.replace("-","")}', # Example number
            'employee': {
                'id': employee.id,
                'name': employee.username,
                'department': employee.department.name if employee.department else 'N/A', # Assuming User has department_id relationship
                'position': 'N/A', # Assuming position is on User or another table
                'bank': 'N/A', # Assuming bank details are elsewhere
                'account': 'N/A' # Assuming bank details are elsewhere
            },
            'earnings': {
                'basic': payslip_record.basic_salary,
                'details': { # Break down allowances if possible, otherwise just use 'Allowances'
                    'Basic Salary': payslip_record.basic_salary,
                    'Allowances': payslip_record.allowances # Assuming allowances are a single sum
                    # Add other specific allowances if you have them
                },
                'gross': (payslip_record.basic_salary or 0) + (payslip_record.allowances or 0) # Calculate gross
            },
            'deductions': {
                'total': payslip_record.deductions,
                'details': { # Break down deductions if possible, otherwise just use 'Deductions'
                    'Total Deductions': payslip_record.deductions # Assuming deductions are a single sum
                    # You would break this down into Income Tax, Pension, Loans, etc.
                    # Example: 'Income Tax': payslip_record.income_tax, 'Pension': payslip_record.pension_deduction
                }
            },
            'taxableIncome': (payslip_record.basic_salary or 0) + (payslip_record.allowances or 0) - (payslip_record.deductions or 0), # Simplified taxable income calculation
            'netPay': payslip_record.net_pay,
            'paymentMethod': 'Bank Transfer', # Static or fetched
            'status': payslip_record.status,
            'notes': 'This is an automatically generated payslip.' # Static or fetched
        }

        return jsonify(payslip_data)

    except Exception as e:
        current_app.logger.error(f"Error fetching payslip for employee {employee_id} period {period}: {str(e)}")
        return jsonify({'error': 'Failed to fetch payslip data'}), 500

@app.route('/api/payroll/email-payslip', methods=['POST'])
def api_email_payslip():
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    employee_id = data.get('employee_id')
    period = data.get('period')

    if not employee_id or not period:
        return jsonify({'error': 'Missing employee ID or period'}), 400

    try:
        # Fetch payslip data (can reuse the logic from api_get_payslip)
        payslip_response = api_get_payslip(employee_id)
        if payslip_response.status_code != 200:
            return payslip_response # Return error from get_payslip

        payslip_data = payslip_response.get_json()
        employee = User.query.get(employee_id)

        if not employee or not employee.email: # Assuming User model has an 'email' field
            return jsonify({'success': False, 'message': 'Employee or Employee Email not found'}), 404

        
        print(f"Simulating email sent to {employee.email} for payslip period {period}") # Log for demonstration

        # Log the email action
        new_log = SystemLog(
            action='payslip_emailed',
            details=f'Payslip for employee {employee.username} ({employee.id}) for period {period} emailed.',
            timestamp=datetime.now()
        )
        db.session.add(new_log)
        db.session.commit()


        return jsonify({'success': True, 'message': 'Payslip emailed successfully!'})

    except Exception as e:
        current_app.logger.error(f"Error emailing payslip for employee {employee_id} period {period}: {str(e)}")
        # Log the error
        error_log = SystemLog(
            action='payslip_email_error',
            details=f'Error emailing payslip for employee {employee_id} period {period}: {str(e)}',
            timestamp=datetime.now()
        )
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'success': False, 'message': f'Failed to email payslip: {str(e)}'}), 500

@app.route('/get_today_employees')
def get_today_employees():
    today = date.today()
    employees = Present.query.filter_by(date=today, present=True).join(Employee).all()
    
    return jsonify([{
        'id': emp.employee.id,
        'name': f"{emp.employee.first_name} {emp.employee.last_name}",
        'department': emp.employee.department.name if emp.employee.department else 'N/A'
    } for emp in employees])

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for employee dashboard with multi-language support
@app.route('/employee_dashboard')
@login_required
def employee_dashboard():
    if 'username' not in session or session.get('is_admin'):
        flash('You are not authorized to access this page', 'danger')
        return redirect('/login')
    
    # Get language preference (default to English)
    language = request.args.get('lang', session.get('language', 'en'))
    session['language'] = language
    
    # Fetch all necessary data efficiently
    user_data = db.session.get(User, current_user.id)
    
    # Get leave requests with optimized query
    leave_requests = db.session.query(LeaveRequest)\
        .filter_by(user_id=current_user.id)\
        .order_by(LeaveRequest.submitted_at.desc())\
        .limit(5).all()
    
    # Get permission requests
    permission_requests = db.session.query(Permission)\
        .filter_by(user_id=current_user.id)\
        .order_by(Permission.submitted_at.desc())\
        .limit(5).all()
    
    # Get attendance records for the current month
    today = date.today()
    first_day = date(today.year, today.month, 1)
    attendance_records = db.session.query(Attendance)\
        .filter_by(user_id=current_user.id)\
        .filter(Attendance.date >= first_day)\
        .order_by(Attendance.date.desc()).all()
    
    # Get latest payroll data
    payroll_data = db.session.query(Payroll)\
        .filter_by(user_id=current_user.id)\
        .order_by(Payroll.pay_period.desc())\
        .first()
    
    # Get unread notifications
    notifications = db.session.query(Notification)\
        .filter_by(user_id=current_user.id, is_read=False)\
        .order_by(Notification.created_at.desc())\
        .limit(5).all()
    
    # Scrape university news from the website
    try:
        news_response = requests.get('https://www.haramaya.edu.et/news/', timeout=5)
        university_news = []
        if news_response.status_code == 200:
            soup = BeautifulSoup(news_response.text, 'html.parser')
            news_items = soup.select('.news-item')[:5]  # Get latest 5 news items
            for item in news_items:
                title = item.select_one('.news-title').text.strip()
                date_str = item.select_one('.news-date').text.strip()
                summary = item.select_one('.news-excerpt').text.strip()
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = f"https://www.haramaya.edu.et{link}"
                university_news.append({
                    "title": title,
                    "date": date_str,
                    "summary": summary,
                    "link": link
                })
    except Exception as e:
        app.logger.error(f"Error fetching university news: {str(e)}")
        university_news = [{
            "title": "News unavailable",
            "date": "",
            "summary": "Could not fetch latest news from university website",
            "link": "https://www.haramaya.edu.et/news/"
        }]
    
    # Translation dictionary for multi-language support
    translations = {
        "en": {
            "welcome": "Welcome",
            "attendance": "Attendance",
            "payroll": "Payroll",
            "notifications": "Notifications",
            "leave_balance": "Leave Balance",
            # Add more translations as needed
        },
        "am": {
            "welcome": "እንኳን ደህና መጡ",
            "attendance": "ተገኝነት",
            "payroll": "ደመወዝ",
            "notifications": "ማስታወቂያዎች",
            "leave_balance": "የፈቃድ ቀሪ ቀን",
            # Add more translations as needed
        },
        "om": {
            "welcome": "Baga nagaan dhuftan",
            "attendance": "Argama",
            "payroll": "Hojii",
            "notifications": "Beeksisaa",
            "leave_balance": "Dhiifama dhiifama",
            # Add more translations as needed
        }
    }
    
    return render_template('employee_dashboard.html', 
                        user=user_data,
                        permissions=permission_requests,
                        leave_requests=leave_requests,
                        attendance_records=attendance_records,
                        payroll_data=payroll_data,
                        notifications=notifications,
                        university_news=university_news,
                        today=today,
                        language=language,
                        translations=translations.get(language, translations['en']))

# Route to handle leave request submission
@app.route('/submit_leave_request', methods=['POST'])
@login_required
def submit_leave_request():
    if request.method == 'POST':
        try:
            leave_type = request.form['leave_type']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            reason = request.form['reason']
            
            # Validate dates
            if start_date > end_date:
                flash('End date must be after start date', 'danger')
                return redirect(url_for('employee_dashboard'))
            
            if start_date < date.today():
                flash('Start date cannot be in the past', 'danger')
                return redirect(url_for('employee_dashboard'))
            
            # Check leave balance
            user = db.session.get(User, current_user.id)
            required_days = (end_date - start_date).days + 1
            if leave_type == 'Annual Leave' and user.salary_structure < required_days:
                flash(f'Not enough leave balance. You have {user.salary_structure} days remaining but requested {required_days} days.', 'danger')
                return redirect(url_for('employee_dashboard'))
            
            # Handle file upload if present
            file_path = None
            if 'supporting_docs' in request.files:
                file = request.files['supporting_docs']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'leave'), exist_ok=True)
                    file_path = os.path.join('uploads/leave', filename)
                    file.save(os.path.join('static', file_path))
            
            new_leave = LeaveRequest(
                user_id=current_user.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                supporting_docs=file_path,
                status='Pending',
                submitted_at=datetime.now()
            )
            
            db.session.add(new_leave)
            db.session.commit()
            
            flash('Leave request submitted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error submitting leave request: {str(e)}")
            flash('Error submitting leave request', 'danger')
        
        return redirect(url_for('employee_dashboard'))

# Route to handle permission request submission
@app.route('/submit_permission', methods=['POST'])
@login_required
def submit_permission():
    if request.method == 'POST':
        try:
            permission_type = request.form['permission_type']
            permission_date = datetime.strptime(request.form['permission_date'], '%Y-%m-%d').date()
            permission_time = request.form.get('permission_time')
            permission_reason = request.form['permission_reason']
            
            # Validate date
            if permission_date < date.today():
                flash('Permission date cannot be in the past', 'danger')
                return redirect(url_for('employee_dashboard'))
            
            # Handle file upload
            file_path = None
            if 'permission_file' in request.files:
                file = request.files['permission_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'permissions'), exist_ok=True)
                    file_path = os.path.join('uploads/permissions', filename)
                    file.save(os.path.join('static', file_path))
            
            new_permission = Permission(
                user_id=current_user.id,
                permission_type=permission_type,
                permission_date=permission_date,
                permission_time=permission_time,
                permission_reason=permission_reason,
                file_path=file_path,
                status='Pending',
                submitted_at=datetime.now()
            )
            
            db.session.add(new_permission)
            db.session.commit()
            
            flash('Permission request submitted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error submitting permission request: {str(e)}")
            flash('Error submitting permission request', 'danger')
        
        return redirect(url_for('employee_dashboard'))

# API endpoint to fetch university news
@app.route('/api/university_news')
def get_university_news():
    try:
        news_response = requests.get('https://www.haramaya.edu.et/news/', timeout=5)
        if news_response.status_code == 200:
            soup = BeautifulSoup(news_response.text, 'html.parser')
            news_items = soup.select('.news-item')[:5]
            news_list = []
            for item in news_items:
                title = item.select_one('.news-title').text.strip()
                date_str = item.select_one('.news-date').text.strip()
                summary = item.select_one('.news-excerpt').text.strip()
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = f"https://www.haramaya.edu.et{link}"
                
                # Try to get image if available
                image = item.select_one('img')
                image_url = image['src'] if image else url_for('static', filename='images/news_placeholder.jpg')
                
                news_list.append({
                    "title": title,
                    "date": date_str,
                    "summary": summary,
                    "link": link,
                    "image": image_url
                })
            return jsonify(news_list)
    except Exception as e:
        app.logger.error(f"Error fetching university news: {str(e)}")
    
    return jsonify({"error": "Could not fetch university news"}), 500

# Route to change language preference
@app.route('/set_language/<lang>')
@login_required
def set_language(lang):
    if lang in ['en', 'am', 'om']:
        session['language'] = lang
    return redirect(request.referrer or url_for('employee_dashboard'))
@app.route('/')
def home():
    return render_template('nav.html')
@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/help')
def help():
    return render_template('help.html')
@app.route('/payroll_employee')
@login_required
def payroll_employee():
    if 'username' not in session or session.get('is_admin'):
        flash('You are not authorized to access this page', 'danger')
        return redirect('/login')
    
    # Fetch employee details
    employee = User.query.get(current_user.id)
    
    # Fetch payroll records for the logged-in employee
    payrolls = Payroll.query.filter_by(user_id=current_user.id)\
                            .order_by(Payroll.pay_period.desc())\
                            .all()

    # Calculate detailed payroll information
    detailed_payrolls = []
    for payroll in payrolls:
        # Get attendance data for the pay period
        start_date = payroll.pay_period.replace(day=1)
        end_date = payroll.pay_period
        
        attendance_records = Attendance.query.filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()

        # Calculate attendance metrics
        present_days = sum(1 for record in attendance_records if record.present)
        absent_days = sum(1 for record in attendance_records if not record.present)
        late_days = sum(1 for record in attendance_records if record.late_check)
        
        # Calculate components from payroll model
        gross_pay = payroll.basic_salary + payroll.allowances + payroll.bonuses
        total_deductions = payroll.deductions + payroll.tax_amount + payroll.absence_penalty + payroll.late_penalty
        
        detailed_payrolls.append({
            'pay_period': payroll.pay_period.strftime('%B %Y'),
            'period_date': payroll.pay_period,
            'basic_salary': payroll.basic_salary,
            'allowances': payroll.allowances,
            'bonuses': payroll.bonuses,
            'performance_bonus': payroll.performance_bonus,
            'absence_penalty': payroll.absence_penalty,
            'late_penalty': payroll.late_penalty,
            'tax_amount': payroll.tax_amount,
            'other_deductions': payroll.deductions,
            'total_deductions': total_deductions,
            'net_pay': payroll.net_pay,
            'gross_pay': gross_pay,
            'attendance': {
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'total_days': (end_date - start_date).days + 1  # Total days in month
            },
            'performance_rating': payroll.performance_rating,
            'status': 'Processed' if payroll.processed else 'Pending',
            'process_date': payroll.process_date.strftime('%d/%m/%Y') if payroll.process_date else 'N/A',
            'id': payroll.id
        })

    return render_template('payroll_employee.html', 
                        payrolls=detailed_payrolls,
                        employee=employee)

def calculate_tax(income):
    """Calculate tax based on progressive tax brackets"""
    if income <= 15000:
        return 0
    elif income <= 30000:
        return (income - 15000) * 0.1
    elif income <= 60000:
        return 1500 + (income - 30000) * 0.15
    else:
        return 6000 + (income - 60000) * 0.2

def calculate_performance_bonus(basic_salary, performance_rating):
    """Calculate performance bonus based on rating"""
    performance_bonus_rates = {
        'Outstanding': 0.15,
        'Excellent': 0.10,
        'Good': 0.05,
        'Average': 0.0,
        'Poor': -0.05
    }
    bonus_rate = performance_bonus_rates.get(performance_rating, 0.0)
    return basic_salary * bonus_rate

@app.template_filter('get_month_display')
def get_month_display(month_options, current_month):
    if not month_options:
        return current_month
    month = next((m for m in month_options if m['value'] == current_month), None)
    return month['display'] if month else current_month
def calculate_payroll_components(employee, base_salary, attendance_stats, leave_days, month_year):
    """
    Calculate payroll components for an employee.
    """
    # Example calculation logic
    daily_salary = base_salary / attendance_stats['total_days']
    absence_penalty = attendance_stats['absent_days'] * daily_salary
    late_penalty = attendance_stats['late_days'] * (daily_salary * 0.1)
    overtime_bonus = attendance_stats['overtime_hours'] * (daily_salary / 8 * 1.5)
    performance_bonus = calculate_performance_bonus(base_salary, employee.performance_rating or 'Good')
    taxable_income = base_salary + overtime_bonus + performance_bonus
    tax_amount = calculate_tax(taxable_income)
    net_pay = base_salary + overtime_bonus + performance_bonus - absence_penalty - late_penalty - tax_amount

    return {
        'basic_salary': base_salary,
        'allowances': 0,  # Placeholder for allowances
        'bonuses': overtime_bonus,
        'deductions': absence_penalty + late_penalty + tax_amount,
        'tax_amount': tax_amount,
        'absence_penalty': absence_penalty,
        'late_penalty': late_penalty,
        'performance_bonus': performance_bonus,
        'net_pay': net_pay
    }
def process_payroll(month_year):
    """
    Process payroll for a specific month-year period
    Returns: Tuple (success: bool, message: str)
    """
    try:
        # Validate month_year format (YYYY-MM)
        processing_date = datetime.strptime(month_year, '%Y-%m')
        
        # Check if payroll already processed for this period
        existing = Payroll.query.filter(
            extract('month', Payroll.pay_period) == processing_date.month,
            extract('year', Payroll.pay_period) == processing_date.year,
            Payroll.processed == True
        ).first()
        
        if existing:
            return False, f"Payroll already processed for {month_year}"

        payroll_data = calculate_payroll_components(
                employee, 
                base_salary,
                attendance_stats,
                leave_days,
                month_year
            )
        employees = User.query.filter_by(is_active=True, is_admin=False).all()
        
        if not employees:
            return False, "No active employees found"

        processed_count = 0
        
        for employee in employees:
            # Skip if employee has no salary structure
            if not employee.salary_structure:
                continue

            # Calculate attendance metrics
            attendance_stats = calculate_attendance_stats(employee.id, month_year)
            
            # Calculate leave days
            leave_days = calculate_approved_leave_days(employee.id, month_year)
            
            # Get base salary from employee record
            try:
                base_salary = float(employee.salary_structure)
            except (ValueError, TypeError):
                base_salary = 0.0

            # Calculate payroll components
            payroll_data = calculate_payroll_components(
                employee, 
                base_salary,
                attendance_stats,
                leave_days,
                month_year
            )

            # Create payroll record
            payroll = Payroll(
                user_id=employee.id,
                basic_salary=payroll_data['basic_salary'],
                allowances=payroll_data['allowances'],
                bonuses=payroll_data['bonuses'],
                deductions=payroll_data['deductions'],
                net_pay=payroll_data['net_pay'],
                pay_period=processing_date,
                tax_amount=payroll_data['tax_amount'],
                absence_penalty=payroll_data['absence_penalty'],
                late_penalty=payroll_data['late_penalty'],
                performance_bonus=payroll_data['performance_bonus'],
                processed=True,
                month=processing_date.month,
                process_date=datetime.utcnow()
            )
            
            db.session.add(payroll)
            processed_count += 1

        db.session.commit()
        return True, f"Successfully processed payroll for {processed_count} employees"

    except Exception as e:
        db.session.rollback()
        return False, f"Payroll processing failed: {str(e)}"

def calculate_attendance_stats(user_id, month_year):
    """
    Calculate attendance metrics for payroll
    Returns: dict with attendance statistics
    """
    try:
        processing_date = datetime.strptime(month_year, '%Y-%m')
        start_date = processing_date.replace(day=1)
        end_date = (processing_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        # Get all attendance records for the period
        attendance_records = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()

        total_days = (end_date - start_date).days + 1
        present_days = sum(1 for record in attendance_records if record.present)
        absent_days = total_days - present_days
        late_days = sum(1 for record in attendance_records if record.late_check)
        overtime_hours = sum(record.overtime_hours or 0 for record in attendance_records)
        total_worked_hours = sum(record.hours or 0 for record in attendance_records)

        return {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'overtime_hours': overtime_hours,
            'total_worked_hours': total_worked_hours
        }

    except Exception as e:
        return {
            'total_days': 0,
            'present_days': 0,
            'absent_days': 0,
            'late_days': 0,
            'overtime_hours': 0,
            'total_worked_hours': 0
        }

def calculate_approved_leave_days(user_id, month_year):
    """
    Calculate approved leave days for payroll calculations
    """
    try:
        processing_date = datetime.strptime(month_year, '%Y-%m')
        start_date = processing_date.replace(day=1)
        end_date = (processing_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        # Get approved leave requests that overlap with the payroll period
        leaves = LeaveRequest.query.filter(
            LeaveRequest.user_id == user_id,
            LeaveRequest.status == 'Approved',
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        ).all()

        total_leave_days = 0
        
        for leave in leaves:
            # Calculate actual leave days within the payroll period
            effective_start = max(leave.start_date, start_date)
            effective_end = min(leave.end_date, end_date)
            total_leave_days += (effective_end - effective_start).days + 1
            
        return total_leave_days

    except Exception as e:
        return 0
logger = logging.getLogger(__name__)

@app.route('/payroll_dashboard', methods=['GET', 'POST'])
@login_required
def payroll_dashboard():
    """
    Enhanced Payroll Dashboard View:
    - Includes employee details, salary structure, bank info
    - Shows attendance data (time worked, check-in/out, lateness)
    - Handles month selection and validation
    """
    try:
        # 1. Get selected month from request (default to current month)
        selected_month = validate_month_input(request)
        processing_date = datetime.strptime(selected_month, '%Y-%m')

        # 2. Handle payroll processing POST requests
        if request.method == 'POST':
            return handle_payroll_post_requests(processing_date, selected_month)

        # 3. Fetch enhanced payroll data including employee details
        payroll_data = fetch_enhanced_payroll_data(processing_date)

        # 4. Get available reporting periods for dropdown
        month_options = get_available_reporting_periods()

        # 5. If no data for current month, redirect to most recent available period
        if not payroll_data['records'] and month_options:
            return redirect_to_most_recent(month_options)

        # 6. Prepare enhanced data for template rendering
        template_data = prepare_enhanced_template_data(
            payroll_data,
            selected_month,
            month_options,
            processing_date
        )

        # 7. Render the dashboard
        return render_template('payroll_dashboard.html', **template_data)

    except Exception as e:
        logger.error(f"Payroll dashboard error: {str(e)}", exc_info=True)
        flash('Error loading payroll dashboard', 'danger')
        return redirect(url_for('payroll_dashboard', month=datetime.now().strftime('%Y-%m')))

def fetch_enhanced_payroll_data(processing_date):
    """Fetch payroll data with employee details and attendance records"""
    # Get all active employees
    employees = User.query.filter_by(is_active=True).all()
    
    records = []
    for employee in employees:
        # Get payroll records for the selected month
        payroll_record = Payroll.query.filter(
            Payroll.user_id == employee.id,
            func.strftime('%Y-%m', Payroll.pay_period) == processing_date.strftime('%Y-%m')
        ).first()
        
        # Get attendance records for the selected month
        attendance_records = Attendance.query.filter(
            Attendance.user_id == employee.id,
            func.strftime('%Y-%m', Attendance.date) == processing_date.strftime('%Y-%m')
        ).all()
        
        # Calculate attendance summary
        total_worked_hours = sum(rec.hours or 0 for rec in attendance_records)
        total_overtime = sum(rec.overtime_hours or 0 for rec in attendance_records)
        late_days = sum(1 for rec in attendance_records if rec.late_check)
        absences = sum(rec.absences or 0 for rec in attendance_records)
        
        records.append({
            'employee_id': employee.id,
            'employee_name': employee.username,
            'employee_id_number': employee.employee_id,
            'designation': employee.designation,
            'department': employee.department.name if employee.department else 'N/A',
            'salary_structure': employee.salary_structure,
            'salary_structure_name': employee.salary_structure_name,
            'bank_account': employee.bank_account_details,
            'account_number': employee.account_number,
            'tax_id': employee.tax_id,
            'payroll_data': payroll_record,
            'attendance_summary': {
                'total_worked_hours': total_worked_hours,
                'total_overtime': total_overtime,
                'late_days': late_days,
                'absences': absences,
                'days_present': len([r for r in attendance_records if r.present])
            },
            'attendance_details': [{
                'date': rec.date.strftime('%Y-%m-%d'),
                'present': rec.present,
                'time_in': rec.time_in.strftime('%H:%M') if rec.time_in else 'N/A',
                'time_out': rec.time_out.strftime('%H:%M') if rec.time_out else 'N/A',
                'hours_worked': rec.hours,
                'overtime': rec.overtime_hours,
                'was_late': rec.late_check,
                'location': f"{rec.location_lat}, {rec.location_lng}" if rec.location_lat else 'N/A'
            } for rec in attendance_records]
        })
    
    return {
        'records': records,
        'total_employees': len(employees),
        'selected_month': processing_date.strftime('%B %Y')
    }

def prepare_enhanced_template_data(payroll_data, selected_month, month_options, processing_date):
    """Prepare all data needed for the enhanced template"""
    return {
        'payroll_records': payroll_data['records'],
        'selected_month': selected_month,
        'month_options': month_options,
        'processing_date': processing_date,
        'total_employees': payroll_data['total_employees'],
        'month_year': payroll_data['selected_month'],
        'current_year': datetime.now().year,
        'current_month': datetime.now().month
    }
@app.template_filter('validate_month_input')
def validate_month_input_filter(value):
    try:
        datetime.strptime(value, '%Y-%m')
        return value
    except Exception:
        return datetime.utcnow().strftime('%Y-%m')
def validate_month_input(request):
    """Validate and return selected month from request"""
    selected_month = request.args.get('month') or request.form.get('month') or datetime.now(timezone.utc).strftime('%Y-%m')
    try:
        datetime.strptime(selected_month, '%Y-%m')
        return selected_month
    except ValueError:
        flash('Invalid month format. Defaulting to current month.', 'warning')
        return datetime.utcnow().strftime('%Y-%m')

def handle_payroll_post_requests(processing_date, selected_month):
    if 'process_payroll' in request.form:
        Thread(target=process_payroll_for_month, args=(selected_month,)).start()
        flash('Payroll processing started in background', 'info')
        return redirect(url_for('payroll_dashboard', month=selected_month))
    elif 'export_csv' in request.form:
        return export_payroll_csv(processing_date)  # <-- Pass the argument here
    elif 'edit_payroll' in request.form:
        return handle_payroll_edit(request.form)
    return redirect(url_for('payroll_dashboard', month=selected_month))

def process_payroll_for_month(month_year):
    """Process payroll for a specific month (runs in background)"""
    with app.app_context():
        try:
            processing_date = datetime.strptime(month_year, '%Y-%m')
            
            if is_payroll_processed(processing_date):
                flash(f"Payroll already processed for {month_year}", 'info')
                return

            employees = User.query.filter_by(is_active=True, is_admin=False).all()
            if not employees:
                flash("No active employees found", 'warning')
                return

            processed_count = 0
            
            for employee in employees:
                if not employee.salary_structure:
                    continue

                try:
                    payroll_data = calculate_employee_payroll(employee, month_year)
                    
                    payroll = Payroll(
                        user_id=employee.id,
                        pay_period=processing_date,
                        processed=True,
                        month=processing_date.month,
                        process_date=datetime.utcnow(),
                        **payroll_data
                    )
                    
                    db.session.add(payroll)
                    processed_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing payroll for {employee.username}: {str(e)}")
                    continue

            db.session.commit()
            flash(f"Processed payroll for {processed_count} employees", 'success')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Payroll processing failed: {str(e)}", exc_info=True)
            flash(f"Payroll processing failed: {str(e)}", 'danger')

def process_payroll_for_month(month_year):
    """Process payroll for a specific month (runs in background)"""
    with app.app_context():
        try:
            processing_date = datetime.strptime(month_year, '%Y-%m')
            
            if is_payroll_processed(processing_date):
                return False, f"Payroll already processed for {month_year}"

            employees = User.query.filter_by(is_active=True, is_admin=False).all()
            if not employees:
                return False, "No active employees found"

            processed_count = 0
            
            for employee in employees:
                if not employee.salary_structure:
                    continue

                try:
                    payroll_data = calculate_employee_payroll(employee, month_year)
                    
                    payroll = Payroll(
                        user_id=employee.id,
                        pay_period=processing_date,
                        processed=True,
                        month=processing_date.month,
                        process_date=datetime.utcnow(),
                        **payroll_data
                    )
                    
                    db.session.add(payroll)
                    processed_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing payroll for {employee.username}: {str(e)}")
                    continue

            db.session.commit()
            return True, f"Processed payroll for {processed_count} employees"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Payroll processing failed: {str(e)}", exc_info=True)
            return False, f"Payroll processing failed: {str(e)}"

def calculate_employee_payroll(employee, month_year):
    """Calculate all payroll components for an employee"""
    base_salary = float(employee.salary_structure)
    attendance = get_attendance_stats(employee.id, month_year)
    leave_days = get_approved_leave_days(employee.id, month_year)
    
    # Calculate components
    allowances = base_salary * 0.10  # 10% of base salary
    daily_salary = base_salary / attendance['total_days']
    
    absence_penalty = attendance['absent_days'] * daily_salary
    late_penalty = attendance['late_days'] * (daily_salary * 0.005)  # 0.5% penalty
    
    hourly_rate = base_salary / (attendance['total_days'] * 8)
    overtime_bonus = attendance['overtime_hours'] * (hourly_rate * 1.5)
    
    
    taxable_income = base_salary + allowances + overtime_bonus
    tax_amount = calculate_tax(taxable_income)
    
    net_pay = (
        base_salary
        + allowances
        + overtime_bonus
        - tax_amount
        - absence_penalty
        - late_penalty
    )
    
    return {
        'basic_salary': base_salary,
        'allowances': allowances,
        'bonuses': overtime_bonus,
        'deductions': 0,  # Can be customized
        'tax_amount': tax_amount,
        'absence_penalty': absence_penalty,
        'late_penalty': late_penalty,
        'net_pay': max(0, net_pay)
    }

def get_attendance_stats(user_id, month_year):
    """Get attendance statistics for payroll period"""
    processing_date = datetime.strptime(month_year, '%Y-%m')
    start_date = processing_date.replace(day=1)
    end_date = (processing_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    total_days = (end_date - start_date).days + 1
    present_days = sum(1 for r in records if r.present)
    
    return {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': total_days - present_days,
        'late_days': sum(1 for r in records if r.late_check),
        'overtime_hours': sum(r.overtime_hours or 0 for r in records)
    }
def fetch_enhanced_payroll_data(processing_date):
    """Fetch payroll data with employee details and attendance records"""
    employees = User.query.filter_by(is_active=True).all()
    
    records = []
    for employee in employees:
        payroll_record = Payroll.query.filter(
            Payroll.user_id == employee.id,
            func.strftime('%Y-%m', Payroll.pay_period) == processing_date.strftime('%Y-%m')
        ).first()
        attendance_records = Attendance.query.filter(
            Attendance.user_id == employee.id,
            func.strftime('%Y-%m', Attendance.date) == processing_date.strftime('%Y-%m')
        ).all()
        total_worked_hours = sum(rec.hours or 0 for rec in attendance_records)
        total_overtime = sum(rec.overtime_hours or 0 for rec in attendance_records)
        late_days = sum(1 for rec in attendance_records if rec.late_check)
        absences = sum(rec.absences or 0 for rec in attendance_records)

        # --- Calculate net salary using your function ---
        # Use employee.salary_structure as base_salary, and pass month_year as string
        try:
            base_salary = float(employee.salary_structure or 0)
        except Exception:
            base_salary = 0.0
        month_year = processing_date.strftime('%Y-%m')
        calculated_payroll = calculate_employee_payroll(employee, month_year)
        calculated_net_salary = calculated_payroll.get('net_pay', 0) if calculated_payroll else 0

        records.append({
            'employee_id': employee.id,
            'employee_name': employee.username,
            'employee_id_number': employee.employee_id,
            'designation': employee.designation,
            'department': employee.department.name if employee.department else 'N/A',
            'salary_structure': employee.salary_structure,
            'salary_structure_name': employee.salary_structure_name,
            'bank_account': employee.bank_account_details,
            'account_number': employee.account_number,
            'tax_id': employee.tax_id,
            'payroll_data': payroll_record,
            'attendance_summary': {
                'total_worked_hours': total_worked_hours,
                'total_overtime': total_overtime,
                'late_days': late_days,
                'absences': absences,
                'days_present': len([r for r in attendance_records if r.present])
            },
            'attendance_details': [{
                'date': rec.date.strftime('%Y-%m-%d'),
                'present': rec.present,
                'time_in': rec.time_in.strftime('%H:%M') if rec.time_in else 'N/A',
                'time_out': rec.time_out.strftime('%H:%M') if rec.time_out else 'N/A',
                'hours_worked': rec.hours,
                'overtime': rec.overtime_hours,
                'was_late': rec.late_check,
                'location': f"{rec.location_lat}, {rec.location_lng}" if rec.location_lat else 'N/A'
            } for rec in attendance_records],
            # --- Add calculated net salary here ---
            'calculated_net_salary': calculated_net_salary
        })
    
    return {
        'records': records,
        'total_employees': len(employees),
        'selected_month': processing_date.strftime('%B %Y')
    }
def get_approved_leave_days(user_id, month_year):
    """Get approved leave days for payroll period"""
    processing_date = datetime.strptime(month_year, '%Y-%m')
    start_date = processing_date.replace(day=1)
    end_date = (processing_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    leaves = LeaveRequest.query.filter(
        LeaveRequest.user_id == user_id,
        LeaveRequest.status == 'Approved',
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date
    ).all()
    
    total_days = 0
    for leave in leaves:
        effective_start = max(leave.start_date, start_date)
        effective_end = min(leave.end_date, end_date)
        total_days += (effective_end - effective_start).days + 1
        
    return total_days

def calculate_performance_bonus(base_salary, performance_rating):
    """Calculate performance bonus based on rating"""
    rates = {
        'Outstanding': 0.15,
        'Excellent': 0.10,
        'Good': 0.05,
        'Average': 0.0,
        'Poor': -0.05
    }
    return base_salary * rates.get(performance_rating, 0.0)

def calculate_tax(income):
    """Calculate tax based on progressive tax brackets"""
    if income <= 15000:
        return 0
    elif income <= 30000:
        return (income - 15000) * 0.1
    elif income <= 60000:
        return 1500 + (income - 30000) * 0.15
    else:
        return 6000 + (income - 60000) * 0.2

def fetch_payroll_data(processing_date):
    """Fetch all payroll data for the selected period"""
    summary = get_payroll_summary(processing_date)
    records = get_payroll_records(processing_date)
    is_processed = is_payroll_processed(processing_date)
    
    return {
        'summary': summary,
        'records': records,
        'is_processed': is_processed
    }

def get_payroll_summary(processing_date):
    """Get summary statistics for payroll period"""
    return db.session.query(
        func.sum(Payroll.basic_salary).label('total_basic'),
        func.sum(Payroll.allowances).label('total_allowances'),
        func.sum(Payroll.bonuses).label('total_bonuses'),
        func.sum(Payroll.tax_amount).label('total_tax'),
        func.sum(Payroll.net_pay).label('total_net_pay'),
        func.count(Payroll.id).label('employee_count')
    ).filter(
        extract('month', Payroll.pay_period) == processing_date.month,
        extract('year', Payroll.pay_period) == processing_date.year,
        Payroll.processed == True
    ).first()

def get_payroll_records(processing_date):
    """Get detailed payroll records for period"""
    return db.session.query(
        Payroll,
        User.employee_id,
        User.username,
        User.designation,
        User.department,
        User.salary_structure,
        User.bank_account_details,
        User.account_number
    ).join(
        User, Payroll.user_id == User.id
    ).filter(
        extract('month', Payroll.pay_period) == processing_date.month,
        extract('year', Payroll.pay_period) == processing_date.year
    ).order_by(
        User.username
    ).all()

def is_payroll_processed(processing_date):
    """Check if payroll is already processed for period"""
    return db.session.query(
        Payroll.query.filter(
            extract('month', Payroll.pay_period) == processing_date.month,
            extract('year', Payroll.pay_period) == processing_date.year,
            Payroll.processed == True
        ).exists()
    ).scalar()

def get_available_reporting_periods():
    """Get list of available payroll periods"""
    return db.session.query(
        func.strftime('%Y-%m', Payroll.pay_period).label('month')
    ).filter(
        Payroll.processed == True
    ).group_by(
        func.strftime('%Y-%m', Payroll.pay_period)
    ).order_by(
        func.strftime('%Y-%m', Payroll.pay_period).desc()
    ).all()

def redirect_to_most_recent(month_options):
    """Redirect to most recent payroll period"""
    selected_month = month_options[0]
    return redirect(url_for('payroll_dashboard', month=selected_month))

def prepare_template_data(payroll_data, selected_month, month_options, processing_date):
    """Prepare all data needed for template rendering"""
    return {
        'payroll_records': payroll_data['records'],
        'payroll_summary': payroll_data['summary'],
        'selected_month': selected_month,
        'month_options': month_options,
        'is_processed': payroll_data['is_processed'],
        'processing_date': processing_date
    }
@app.route('/export_payroll_csv')
def export_payroll_csv():
    """Export comprehensive payroll data as CSV file (with real calculations)"""
    try:
        # Get processing date from request or use current month
        processing_date_str = request.args.get('date')
        processing_date = datetime.strptime(processing_date_str, '%Y-%m') if processing_date_str else datetime.now()
        month_year = processing_date.strftime('%Y-%m')

        # Fetch all active employees
        employees = User.query.filter_by(is_active=True).all()

        # Prepare in-memory CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Employee ID', 'Full Name', 'Designation', 'Department',
            'Basic Salary', 'Allowances', 'Bonuses', 'Performance Bonus',
            'Total Hours Worked', 'Overtime Hours', 'Late Days',
            'Tax Amount', 'Absence Penalty', 'Late Penalty', 'Other Deductions',
            'Gross Pay', 'Total Deductions', 'Net Pay',
            'Bank Account', 'Account Number',
            'Pay Period', 'Status'
        ])

        for employee in employees:
            # Payroll record for this month
            payroll = Payroll.query.filter(
                Payroll.user_id == employee.id,
                func.strftime('%Y-%m', Payroll.pay_period) == month_year
            ).first()

            # Attendance records for this month
            attendance_records = Attendance.query.filter(
                Attendance.user_id == employee.id,
                func.strftime('%Y-%m', Attendance.date) == month_year
            ).all()

            total_hours = sum(rec.hours or 0 for rec in attendance_records)
            overtime_hours = sum(rec.overtime_hours or 0 for rec in attendance_records)
            late_days = sum(1 for rec in attendance_records if rec.late_check)

            # Calculate payroll (always up-to-date)
            calculated = calculate_employee_payroll(employee, month_year)
            performance_bonus = calculated.get('performance_bonus', 0)
            absence_penalty = calculated.get('absence_penalty', 0)
            late_penalty = calculated.get('late_penalty', 0)
            tax_amount = calculated.get('tax_amount', 0)
            net_pay = calculated.get('net_pay', 0)
            bonuses = calculated.get('bonuses', 0)
            allowances = calculated.get('allowances', 0)
            basic_salary = calculated.get('basic_salary', 0)
            total_deductions = absence_penalty + late_penalty + tax_amount
            gross_pay = basic_salary + allowances + bonuses + performance_bonus

            writer.writerow([
                employee.employee_id,
                employee.username,
                employee.designation,
                employee.department.name if employee.department else 'N/A',
                f"{basic_salary:.2f}",
                f"{allowances:.2f}",
                f"{bonuses:.2f}",
                f"{performance_bonus:.2f}",
                f"{total_hours:.2f}",
                f"{overtime_hours:.2f}",
                late_days,
                f"{tax_amount:.2f}",
                f"{absence_penalty:.2f}",
                f"{late_penalty:.2f}",
                "0.00",  # Other deductions (customize if needed)
                f"{gross_pay:.2f}",
                f"{total_deductions:.2f}",
                f"{net_pay:.2f}",
                employee.bank_account_details,
                employee.account_number,
                month_year,
                "Processed" if payroll and payroll.processed else "Pending"
            ])

        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hu_payroll_{month_year}_{timestamp}.csv"

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment;filename={filename}',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )

    except Exception as e:
        logger.error(f"Payroll CSV export error: {str(e)}", exc_info=True)
        flash('Error generating payroll export. Please try again or contact support.', 'danger')
        return redirect(url_for('payroll_dashboard'))
@app.route('/handle_payroll_edit')
def handle_payroll_edit(form_data):
    """Handle payroll record edits from admin"""
    try:
        payroll = Payroll.query.get_or_404(form_data.get('payroll_id'))
        
        # Update editable fields
        payroll.basic_salary = float(form_data.get('basic_salary', payroll.basic_salary))
        payroll.allowances = float(form_data.get('allowances', payroll.allowances))
        payroll.bonuses = float(form_data.get('bonuses', payroll.bonuses))
        payroll.deductions = float(form_data.get('deductions', payroll.deductions))
        payroll.performance_rating = form_data.get('performance_rating', payroll.performance_rating)
        
        # Recalculate dependent fields
        taxable_income = payroll.basic_salary + payroll.allowances + payroll.bonuses
        payroll.tax_amount = calculate_tax(taxable_income)
        
        payroll.net_pay = (
            payroll.basic_salary
            + payroll.allowances
            + payroll.bonuses
            - payroll.tax_amount
            - payroll.deductions
        )
        
        db.session.commit()
        flash('Payroll record updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Payroll edit error: {str(e)}", exc_info=True)
        flash('Error updating payroll record', 'danger')
    
    return redirect(url_for('payroll_dashboard', month=payroll.pay_period.strftime('%Y-%m')))

# Helper Functions
def validate_unique_payroll(employee_id, pay_period):
    """Check for existing payroll for same employee/month"""
    existing = Payroll.query.filter(
        Payroll.employee_id == employee_id,
        extract('month', Payroll.pay_period) == pay_period.month,
        extract('year', Payroll.pay_period) == pay_period.year
    ).first()
    
    if existing:
        raise ValueError(f'Payroll already exists for this employee in {pay_period.strftime("%B %Y")}')
def create_payroll_record(employee_id, pay_period, payroll_data):
    """Create and return payroll record with calculated values"""
    # Calculate payroll values directly here since calculate_payroll_values is not defined
    # Example calculation (customize as needed):
    calculations = {
        'net_pay': payroll_data.get('basic_salary', 0) + payroll_data.get('allowances', 0) + payroll_data.get('bonuses', 0)
                    - payroll_data.get('deductions', 0) - payroll_data.get('tax_amount', 0)
    }
    
    payroll = Payroll(
        employee_id=employee_id,
        pay_period=pay_period,
        **payroll_data,
        **calculations
    )
    db.session.add(payroll)
    return payroll
def create_attendance_record(employee_id, pay_period, payroll_data):
    """Create attendance record"""
    attendance = Attendance(
        user_id=employee_id,
        month_year=pay_period,
        days_worked=calculate_working_days(pay_period) - payroll_data['absences'],
        overtime_hours=0,
        absences=payroll_data['absences'],
        late_days=payroll_data['late_days']
    )
    db.session.add(attendance)

def calculate_working_days(pay_period):
    """Calculate actual working days in month (excluding weekends)"""
    import calendar
    year, month = pay_period.year, pay_period.month
    _, num_days = calendar.monthrange(year, month)
    working_days = 0
    
    for day in range(1, num_days + 1):
        if calendar.weekday(year, month, day) < 5:  # 0-4 = Monday-Friday
            working_days += 1
    
    return working_days

def notify_employee_payroll_update(employee, payroll):
    """Send notification to employee about payroll update"""
    subject = "Your Payroll Has Been Processed"
    body = f"""Dear {employee.username},
    
Your payroll for {payroll.pay_period.strftime('%B %Y')} has been processed:
- Base Salary: {payroll.basic_salary:,.2f}
- Allowances: {payroll.allowances:,.2f}
- Bonuses: {payroll.bonuses:,.2f}
- Deductions: {payroll.deductions:,.2f}
- Net Pay: {payroll.net_pay:,.2f}

Please contact HR if you have any questions.
"""
    send_email(subject, employee.email, body)
@app.route('/edit_net_salary', methods=['POST'])
def edit_net_salary():
    employee_id = request.form.get('employee_id')
    new_net_salary = request.form.get('net_salary')
    current_period = datetime.now().replace(day=1)
    # Find the payroll record for this employee and month
    payroll = Payroll.query.filter_by(employee_id=employee_id, pay_period=current_period).first()
    if payroll and new_net_salary:
        payroll.finalized_net_salary = float(new_net_salary)
        db.session.commit()
        flash('Net salary updated!', 'success')
    else:
        flash('Failed to update net salary.', 'danger')
    return redirect(url_for('payroll_dashboard'))
@app.route('/generate_payroll_report')
@login_required
def generate_payroll_report():
    try:
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        # Get payroll data for the month
        payroll_data = db.session.query(
            Payroll,
            User
        ).join(
            User, Payroll.employee_id == User.id
        ).filter(
            extract('month', Payroll.pay_period) == datetime.strptime(month, '%Y-%m').month,
            extract('year', Payroll.pay_period) == datetime.strptime(month, '%Y-%m').year
        ).all()

        if not payroll_data:
            flash(f'No payroll data found for {month}', 'warning')
            return redirect(url_for('payroll_dashboard'))

        # Generate report data
        report = {
            'month': datetime.strptime(month, '%Y-%m').strftime('%B %Y'),
            'total_employees': len(payroll_data),
            'total_payroll': sum(p.net_pay for p, _ in payroll_data),
            'total_tax': sum(p.tax_amount for p, _ in payroll_data),
            'total_absence_penalties': sum(p.absence_penalty for p, _ in payroll_data),
            'total_late_penalties': sum(p.late_penalty for p, _ in payroll_data),
            'total_performance_bonuses': sum(p.performance_bonus for p, _ in payroll_data),
            'employees': []
        }

        for payroll, user in payroll_data:
            report['employees'].append({
                'id': user.id,
                'name': user.username,
                'department': user.department,
                'base_salary': payroll.basic_salary,
                'allowances': payroll.allowances,
                'bonuses': payroll.bonuses,
                'performance_bonus': payroll.performance_bonus,
                'tax': payroll.tax_amount,
                'absence_penalty': payroll.absence_penalty,
                'late_penalty': payroll.late_penalty,
                'net_salary': payroll.net_pay,
                'performance': payroll.performance_rating
            })

        # Sort by highest net salary
        report['employees'].sort(key=lambda x: x['net_salary'], reverse=True)

        return render_template('payroll_report.html', report=report)

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        flash('Error generating payroll report', 'danger')
        return redirect(url_for('payroll_dashboard'))
    


@app.route('/download_payroll_report', methods=['GET'])
@login_required
def download_payroll_report():
    # Fetch payroll data
    employees = db.session.query(
        Payroll.id,
        User.username.label('name'),
        User.department,
        Payroll.basic_salary.label('salary'),
        Payroll.deductions.label('deductions'),
        Payroll.performance,
        Payroll.net_pay.label('adjusted_salary')
    ).join(User, Payroll.employee_id == User.id).all()

    # Create a CSV file in memory
    def generate_csv():
        data = [
            ['ID', 'Name', 'Department', 'Base Salary', 'Deductions', 'Performance', 'Adjusted Salary']
        ]
        for emp in employees:
            data.append([
                emp.id,
                emp.name,
                emp.department,
                emp.salary,
                emp.deductions,
                emp.performance,
                emp.adjusted_salary
            ])
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    # Return the CSV file as a response
    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=payroll_report.csv'}
    )
@app.route('/generate_salary_csv', methods=['GET'])
@login_required
def generate_salary_csv():
    if not session.get('is_admin'):
        flash('You are not authorized to perform this action', 'danger')
        return redirect('/payroll_dashboard')

    # Fetch employee salary details
    employees = db.session.query(
        Payroll.employee_id,
        User.username.label('name'),
        User.bank_account_details.label('bank_account'),
        Payroll.net_pay.label('amount')
    ).join(User, Payroll.employee_id == User.id).all()

    # Generate CSV content
    def generate_csv():
        # Write header
        yield 'Employee ID,Name,Bank Account Number,Amount,Payment Date\n'
        # Write employee data
        for emp in employees:
            yield f'{emp.employee_id},{emp.name},{emp.bank_account},{emp.amount},{datetime.utcnow().strftime("%Y-%m-%d")}\n'

    # Return the CSV file as a response
    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=employee_salary_details.csv'}
    )
def get_payroll_data(month, search_query=None):
    """Retrieve payroll data with explicit joins"""
    year, month_num = map(int, month.split('-'))
    
    # Explicit base query with select_from
    base_query = db.session.query(
        User.id,
        User.username,
        Department.name.label('department'),
        Payroll.basic_salary,
        Payroll.allowances,
        Payroll.bonuses,
        Payroll.deductions,
        Payroll.net_pay,
        Payroll.tax_amount,
        Payroll.performance_rating,
        Payroll.pay_period,
        Attendance.days_worked,
        Attendance.overtime_hours,
        Attendance.absences
    ).select_from(User)\
    .join(Department, User.department_id == Department.id, isouter=True)\
    .join(Payroll, User.id == Payroll.user_id)\
    .join(Attendance, and_(
        Payroll.user_id == Attendance.user_id,
        extract('month', Attendance.month_year) == extract('month', Payroll.pay_period),
        extract('year', Attendance.month_year) == extract('year', Payroll.pay_period)
    ), isouter=True)\
    .filter(
        extract('month', Payroll.pay_period) == month_num,
        extract('year', Payroll.pay_period) == year
    )
    
    if search_query:
        base_query = apply_search_filters(base_query, search_query)
    
    records = base_query.order_by(User.username).all()
    
    return {
        'employees': format_employee_records(records),
        'summary': calculate_summary(records),
        'payroll_period': format_payroll_period(month)
    }


def format_payroll_period(month_str):
    """Format month string for display"""
    return datetime.strptime(month_str, '%Y-%m').strftime('%B %Y')
def apply_search_filters(query, search_term):
    """Apply search filters with explicit joins"""
    return query.filter(or_(
        User.username.ilike(f"%{search_term}%"),
        User.department.ilike(f"%{search_term}%")
    ))

def format_employee_records(records):
    """Format database records for template"""
    return [{
        'id': emp.id,
        'name': emp.username,
        'department': emp.department or 'Unassigned',
        'base_salary': float(emp.basic_salary or 0),
        'allowances': float(emp.allowances or 0),
        'bonuses': float(emp.bonuses or 0),
        'deductions': float(emp.deductions or 0),
        'net_salary': float(emp.net_pay or 0),
        'tax_amount': float(emp.tax_amount or 0),
        'performance': emp.performance_rating or 'Not Rated',
        'days_worked': emp.days_worked or 0,
        'overtime_hours': emp.overtime_hours or 0,
        'absences': emp.absences or 0,
        'pay_period': emp.pay_period.strftime('%B %Y') if emp.pay_period else ''
    } for emp in records]

def calculate_summary(records):
    """Calculate summary statistics from records"""
    if not records:
        return None
    
    return {
        'total_employees': len(records),
        'total_payroll': sum(float(r.net_pay or 0) for r in records),
        'avg_salary': sum(float(r.net_pay or 0) for r in records) / len(records),
        'total_tax': sum(float(r.tax_amount or 0) for r in records),
        'total_absences': sum(r.absences or 0 for r in records)
    }

def validate_month(month_str):
    """Validate month format"""
    try:
        if month_str:
            datetime.strptime(month_str, '%Y-%m')
            return month_str
    except ValueError:
        pass
    return datetime.now().strftime('%Y-%m')

def get_reporting_periods():
    """Get available payroll periods with explicit join"""
    periods = db.session.query(
        extract('year', Payroll.pay_period).label('year'),
        extract('month', Payroll.pay_period).label('month')
    ).select_from(Payroll)\
    .distinct()\
    .order_by(
        extract('year', Payroll.pay_period).desc(),
        extract('month', Payroll.pay_period).desc()
    ).all()
    
    return [{
        'value': datetime(year=int(year), month=int(month), day=1).strftime('%Y-%m'),
        'display': datetime(year=int(year), month=int(month), day=1).strftime('%B %Y')
    } for year, month in periods] or [get_current_month_option()]

def handle_dashboard_error(error):
    """Error handling with fallback data"""
    flash('Error loading payroll data', 'danger')
    return render_template('payroll_dashboard.html',
                        employees=[],
                        summary=None,
                        current_month=datetime.now().strftime('%Y-%m'),
                        month_options=[get_current_month_option()])
def get_current_month_option():
    """Get current month as default option"""
    now = datetime.now()
    return {
        'value': now.strftime('%Y-%m'),
        'display': now.strftime('%B %Y')
    }
@app.route('/get_csrf', methods=['GET'])
def get_csrf():
    """Return CSRF token for AJAX requests"""
    return jsonify({'csrf_token': generate_csrf()})

@app.route('/api/employees', methods=['GET'])
@login_required
def get_employees():
    """Return list of employees for dropdown"""
    employees = User.query.filter_by(is_admin=False).order_by(User.username).all()
    return jsonify([{
        'id': emp.id,
        'username': emp.username,
        'employee_id': emp.employee_id,
        'salary': emp.salary_structure or 0
    } for emp in employees])

@app.route('/api/employee/<int:employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """Get details for a specific employee"""
    employee = User.query.get_or_404(employee_id)
    return jsonify({
        'id': employee.id,
        'username': employee.username,
        'salary': employee.salary_structure or 0,
        'department': employee.department
    })



@app.route('/manage_leave_requests', methods=['GET', 'POST'])
@login_required
def manage_leave_requests():
    if not current_user.is_admin:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('login'))

    # Handle POST requests for leave request actions
    if request.method == 'POST':
        leave_id = request.form.get('leave_id')
        action = request.form.get('action')
        admin_comment = request.form.get('admin_comment', '')

        if not leave_id or not action:
            flash('Invalid request parameters', 'danger')
            return redirect(url_for('manage_leave_requests'))

        leave_request = LeaveRequest.query.get_or_404(leave_id)
        
        if action == 'approve':
            leave_request.status = 'Approved'
            # Check for leave balance and deduct if needed
            if leave_request.leave_type in ['Vacation', 'Personal']:
                days_requested = (leave_request.end_date - leave_request.start_date).days + 1
                if leave_request.user.remaining_leave_days >= days_requested:
                    leave_request.user.remaining_leave_days -= days_requested
                else:
                    flash('Employee does not have enough leave days remaining', 'warning')
                    return redirect(url_for('manage_leave_requests'))
            flash('Leave request approved successfully', 'success')
        elif action == 'reject':
            leave_request.status = 'Rejected'
            flash('Leave request rejected', 'info')
        else:
            flash('Invalid action', 'danger')
            return redirect(url_for('manage_leave_requests'))
        
        leave_request.processed_by = current_user.id
        leave_request.processed_at = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Send notification to employee
            send_notification(
                user_id=leave_request.user_id,
                title=f"Leave Request {leave_request.status}",
                message=f"Your {leave_request.leave_type} request has been {leave_request.status.lower()}",
                url=f"/leave_status/{leave_request.id}"
            )
            
            # Log the action
            log_activity(
                user_id=current_user.id,
                activity_type='leave_processed',
                details=f"Processed leave request #{leave_request.id} as {leave_request.status}"
            )
            
        except Exception as e:
            db.session.rollback()
            flash('Error processing leave request', 'danger')
            current_app.logger.error(f"Error processing leave request: {str(e)}")
        
        return redirect(url_for('manage_leave_requests'))

    # Handle GET requests for displaying leave requests
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date_range', 'this_month')
    department_filter = request.args.get('department', 'all')
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Base query with joins
    query = db.session.query(
        LeaveRequest,
        User.username.label('employee_name'),
        Department.name.label('department_name')
    ).join(
        User, LeaveRequest.user_id == User.id
    ).outerjoin(
        Department, User.department_id == Department.id
    ).order_by(
        LeaveRequest.submitted_at.desc()
    )

    # Apply filters
    if status_filter != 'all':
        query = query.filter(LeaveRequest.status == status_filter)

    if department_filter != 'all':
        query = query.filter(Department.id == department_filter)

    if search_query:
        query = query.filter(or_(
            User.username.ilike(f'%{search_query}%'),
            LeaveRequest.leave_type.ilike(f'%{search_query}%'),
            LeaveRequest.reason.ilike(f'%{search_query}%')
        ))

    # Date range filtering
    today = datetime.today().date()
    if date_filter == 'today':
        query = query.filter(LeaveRequest.start_date == today)
    elif date_filter == 'this_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        query = query.filter(LeaveRequest.start_date >= start_date, LeaveRequest.start_date <= end_date)
    elif date_filter == 'this_month':
        start_date = today.replace(day=1)
        end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        query = query.filter(LeaveRequest.start_date >= start_date, LeaveRequest.start_date <= end_date)
    elif date_filter == 'upcoming':
        query = query.filter(LeaveRequest.start_date > today)

    # Pagination
    paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get departments for filter dropdown
    departments = Department.query.order_by(Department.name).all()

    # Calculate statistics for dashboard
    stats = {
        'pending': LeaveRequest.query.filter_by(status='Pending').count(),
        'approved': LeaveRequest.query.filter_by(status='Approved').count(),
        'rejected': LeaveRequest.query.filter_by(status='Rejected').count(),
        'total': LeaveRequest.query.count()
    }

    return render_template(
        'manage_leave_requests.html',
        leave_requests=paginated_data,
        departments=departments,
        stats=stats,
        filters={
            'status': status_filter,
            'date_range': date_filter,
            'department': department_filter,
            'search': search_query
        }
    )


@app.route('/api/leave_requests')
@login_required
def get_leave_requests():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Get filter parameters from request
        status_filter = request.args.get('status', 'all')
        date_filter = request.args.get('date_range', 'all')
        department_filter = request.args.get('department', 'all')
        search_query = request.args.get('search', '')
        
        # Base query
        query = db.session.query(
            LeaveRequest,
            User.username.label('employee_name'),
            User.id.label('employee_id'),
            Department.name.label('department_name'),
            Department.id.label('department_id')
        ).join(
            User, LeaveRequest.user_id == User.id
        ).outerjoin(
            Department, User.department_id == Department.id
        ).order_by(
            LeaveRequest.submitted_at.desc()
        )

        # Apply filters
        if status_filter != 'all':
            query = query.filter(LeaveRequest.status == status_filter)

        if department_filter != 'all':
            query = query.filter(Department.id == department_filter)

        if search_query:
            query = query.filter(or_(
                User.username.ilike(f'%{search_query}%'),
                LeaveRequest.leave_type.ilike(f'%{search_query}%'),
                LeaveRequest.reason.ilike(f'%{search_query}%')
            ))

        # Date range filtering
        today = datetime.today().date()
        if date_filter == 'today':
            query = query.filter(LeaveRequest.start_date == today)
        elif date_filter == 'this_week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            query = query.filter(LeaveRequest.start_date >= start_date, LeaveRequest.start_date <= end_date)
        elif date_filter == 'this_month':
            start_date = today.replace(day=1)
            end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
            query = query.filter(LeaveRequest.start_date >= start_date, LeaveRequest.start_date <= end_date)
        elif date_filter == 'upcoming':
            query = query.filter(LeaveRequest.start_date > today)

        # Execute query and format results
        results = query.all()
        leave_requests = []
        
        for lr, emp_name, emp_id, dept_name, dept_id in results:
            days_requested = (lr.end_date - lr.start_date).days + 1
            processed_by = User.query.get(lr.processed_by).username if lr.processed_by else None
            
            leave_requests.append({
                'id': lr.id,
                'employee': emp_name,
                'employee_id': emp_id,
                'department': dept_name,
                'department_id': dept_id,
                'leave_type': lr.leave_type,
                'start_date': lr.start_date.strftime('%Y-%m-%d'),
                'end_date': lr.end_date.strftime('%Y-%m-%d'),
                'days': days_requested,
                'reason': lr.reason,
                'status': lr.status,
                'submitted_at': lr.submitted_at.strftime('%Y-%m-%d %H:%M'),
                'processed_at': lr.processed_at.strftime('%Y-%m-%d %H:%M') if lr.processed_at else None,
                'processed_by': processed_by,
                'admin_comment': lr.admin_comment,
                'can_approve': lr.status == 'Pending' and current_user.is_admin
            })

        return jsonify({
            'success': True,
            'data': leave_requests,
            'stats': {
                'pending': LeaveRequest.query.filter_by(status='Pending').count(),
                'approved': LeaveRequest.query.filter_by(status='Approved').count(),
                'rejected': LeaveRequest.query.filter_by(status='Rejected').count(),
                'total': LeaveRequest.query.count()
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching leave requests: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching leave requests'
        }), 500
@app.route('/api/leave_stats')
@login_required
def get_leave_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = {
        'pending': LeaveRequest.query.filter_by(status='Pending').count(),
        'approved': LeaveRequest.query.filter_by(status='Approved').count(),
        'rejected': LeaveRequest.query.filter_by(status='Rejected').count(),
        'by_type': db.session.query(
            LeaveRequest.leave_type,
            func.count(LeaveRequest.id)
        )
        .group_by(LeaveRequest.leave_type)
        .all(),
        'by_department': db.session.query(
            Department.name,
            func.count(LeaveRequest.id)
        )
        .join(User, User.id == LeaveRequest.user_id)
        .join(Department, Department.id == User.department_id)
        .group_by(Department.name)
        .all()
    }
    
    return jsonify(stats)

@app.route('/employee_notifications', methods=['GET'])
@login_required
def employee_notifications():
    try:
        today = datetime.now(timezone.utc).date()
        thirty_days_later = today + timedelta(days=30)
        
        # Fetch all notifications for the logged-in employee
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        # Mark unread notifications as read when the page loads
        unread_notifications = [n for n in notifications if not n.is_read]
        if unread_notifications:
            for notification in unread_notifications:
                notification.is_read = True
            db.session.commit()
        
        # Fetch upcoming holidays (next 30 days)
        upcoming_holidays = Holiday.query.filter(
            Holiday.date >= today,
            Holiday.date <= thirty_days_later
        ).order_by(Holiday.date.asc()).all()
        
        # Fetch important system notifications (active ones)
        system_notifications = Notification.query.filter(
            Notification.is_system == True,
            Notification.expiry_date >= today,
            or_(
                Notification.user_id == None,
                Notification.user_id == current_user.id
            )
        ).order_by(Notification.priority.desc(), Notification.created_at.desc()).limit(10).all()
        
        # Fetch attendance alerts (last 7 days)
        seven_days_ago = today - timedelta(days=7)
        attendance_alerts = db.session.query(
            Attendance,
            case(
                (and_(Attendance.present == False, Attendance.date == today), 'Today - Absent'),
                (and_(Attendance.time_in > '09:00:00', Attendance.date == today), 'Today - Late Arrival'),
                (Attendance.hours < 8, 'Short Work Hours'),
                else_='Other Attendance Issue'
            ).label('alert_type')
        ).filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= seven_days_ago,
            or_(
                Attendance.present == False,
                Attendance.time_in > '09:00:00',
                Attendance.hours < 8
            )
        ).order_by(Attendance.date.desc()).limit(10).all()
        
        # Fetch recent leave request updates
        leave_updates = LeaveRequest.query.filter_by(
            user_id=current_user.id
        ).order_by(LeaveRequest.updated_at.desc()).limit(5).all()
        
        # Format leave updates as notifications
        leave_notifications = []
        for leave in leave_updates:
            status_change = "submitted" if leave.status == 'Pending' else leave.status.lower()
            leave_notifications.append({
                'id': f"leave_{leave.id}",
                'title': f"Leave Request {status_change.capitalize()}",
                'message': f"Your {leave.leave_type} leave from {leave.start_date} to {leave.end_date} has been {status_change}",
                'type': 'leave',
                'status': leave.status,
                'created_at': leave.updated_at if leave.status != 'Pending' else leave.submitted_at,
                'action_url': url_for('get_leave_requests')
            })
        
        # Fetch payroll updates (last 3 months)
        payroll_updates = Payroll.query.filter_by(
            user_id=current_user.id
        ).filter(
            Payroll.pay_period >= date(today.year, today.month - 2, 1)
        ).order_by(Payroll.pay_period.desc()).limit(3).all()
        
        # Format payroll updates as notifications
        payroll_notifications = []
        for payroll in payroll_updates:
            payroll_notifications.append({
                'id': f"payroll_{payroll.id}",
                'title': f"Payroll Processed for {payroll.pay_period.strftime('%B %Y')}",
                'message': f"Your net pay is ETB {payroll.net_pay:,.2f}",
                'type': 'payroll',
                'created_at': payroll.created_at,
                'action_url': url_for('payroll_details', payroll_id=payroll.id)
            })
        
        # Combine all notifications
        all_notifications = []
        
        # Add system notifications first (high priority)
        for notification in system_notifications:
            all_notifications.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': 'system',
                'priority': notification.priority,
                'created_at': notification.created_at,
                'is_read': notification.is_read,
                'action_url': notification.action_url
            })
        
        # Add leave notifications
        all_notifications.extend(leave_notifications)
        
        # Add payroll notifications
        all_notifications.extend(payroll_notifications)
        
        # Add regular notifications
        for notification in notifications:
            all_notifications.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'created_at': notification.created_at,
                'is_read': notification.is_read,
                'action_url': notification.action_url
            })
        
        # Sort all notifications by created_at (newest first)
        all_notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return render_template(
            'employee_notifications.html', 
            notifications=all_notifications,
            upcoming_holidays=upcoming_holidays,
            attendance_alerts=attendance_alerts,
            unread_count=len(unread_notifications),csrf_token = generate_csrf()
        )
        
    except Exception as e:
        current_app.logger.error(f"Error fetching notifications: {str(e)}", exc_info=True)
        flash("An error occurred while loading notifications. Please try again later.", "error")
        return redirect(url_for('employee_dashboard'))



@app.route('/trigger_attendance_alert', methods=['POST'])
def trigger_attendance_alert():
    employee_name = request.form.get('employee_name')
    alert_type = request.form.get('alert_type')  # e.g., "Absent", "Late Arrival"
    notify_attendance_alert(employee_name, alert_type)
    return jsonify({"success": True, "message": "Attendance alert notification sent."})
@app.route('/trigger_payroll_update', methods=['POST'])
def trigger_payroll_update():
    employee_name = request.form.get('employee_name')
    update_type = request.form.get('update_type')  # e.g., "Salary Processed", "Bonus Applied"
    notify_payroll_update(employee_name, update_type)
    return jsonify({"success": True, "message": "Payroll update notification sent."})
@app.route('/trigger_unauthorized_login', methods=['POST'])
def trigger_unauthorized_login():
    ip_address = request.remote_addr
    notify_unauthorized_login(ip_address)
    return jsonify({"success": True, "message": "Unauthorized login alert sent."})
def get_setting_value(setting_name, default=None):
    """Get setting with type conversion"""
    setting = Setting.query.filter_by(name=setting_name).first()
    if not setting:
        return default
        
    # Automatic type conversion
    if setting.value.lower() in ('true', 'false'):
        return setting.value.lower() == 'true'
    try:
        return int(setting.value)
    except ValueError:
        try:
            return float(setting.value)
        except ValueError:
            return setting.value

# Helper function to update setting
settings_bp = Blueprint('settings', __name__)

def get_setting_value(name, default=None):
    """Helper to get setting value with proper type conversion"""
    setting = Setting.query.filter_by(name=name).first()
    if not setting:
        return default
    
    # Try to convert to original type
    try:
        if setting.value.lower() in ('true', 'false'):
            return setting.value.lower() == 'true'
        try:
            return int(setting.value)
        except ValueError:
            try:
                return float(setting.value)
            except ValueError:
                return setting.value
    except:
        return setting.value

def update_setting(name, value):
    """Update setting with proper type handling and validation"""
    # Basic validation
    if not name or value is None:
        return False
    
    # Convert boolean values to string
    if isinstance(value, bool):
        value = 'true' if value else 'false'
    elif isinstance(value, (dict, list)):
        value = json.dumps(value)
    else:
        value = str(value)
    
    setting = Setting.query.filter_by(name=name).first()
    if not setting:
        setting = Setting(name=name, value=value)
        db.session.add(setting)
    else:
        setting.value = value
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating setting {name}: {str(e)}")
        return False

@settings_bp.route('/api/settings/<category>', methods=['GET', 'POST'])
@jwt_required()
def handle_settings(category):
    if request.method == 'GET':
        try:
            settings_map = {
                'general': {
                    'portal_name': get_setting_value('portal_name', 'Attendance Portal'),
                    'logo_url': get_setting_value('logo_url', '/static/logo.png'),
                    'admin_email': get_setting_value('admin_email', 'admin@example.com'),
                    'system_language': get_setting_value('system_language', 'en'),
                    'timezone': get_setting_value('timezone', 'UTC'),
                    'currency': get_setting_value('currency', 'USD'),
                    'date_format': get_setting_value('date_format', 'MM/DD/YYYY'),
                    'support_phone': get_setting_value('support_phone', ''),
                    'system_address': get_setting_value('system_address', '')
                },
                'attendance': {
                    'work_start_time': get_setting_value('work_start_time', '09:00'),
                    'work_end_time': get_setting_value('work_end_time', '17:00'),
                    'grace_period': get_setting_value('grace_period', 10),
                    'auto_absent_after': get_setting_value('auto_absent_after', 60),
                    'overtime_rules': json.loads(get_setting_value('overtime_rules', '{"after_hours": 8, "rate": 1.5}')),
                    'break_duration': get_setting_value('break_duration', 60),
                    'enable_weekends': get_setting_value('enable_weekends', False),
                    'face_recognition_sensitivity': get_setting_value('face_recognition_sensitivity', 0.8)
                },
                'face-recognition': {
                    'model_version': get_setting_value('face_model_version', '1.0'),
                    'confidence_threshold': get_setting_value('face_confidence_threshold', 0.75),
                    'enable_liveness': get_setting_value('face_enable_liveness', False),
                    'camera_source': get_setting_value('face_camera_source', '0')
                }
                # Add other categories as needed
            }
            
            if category not in settings_map:
                return jsonify({'error': 'Invalid settings category'}), 400
                
            return jsonify(settings_map[category])
            
        except Exception as e:
            current_app.logger.error(f"Error getting {category} settings: {str(e)}")
            return jsonify({'error': f'Failed to load {category} settings'}), 500
            
    else:  # POST
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            # Validate and save each setting
            success = True
            for key, value in data.items():
                if not update_setting(key, value):
                    success = False
                    current_app.logger.warning(f"Failed to update setting: {key}")
                    
            if success:
                return jsonify({
                    'success': True,
                    'message': f'{category.replace("-", " ").title()} settings updated',
                    'settings': data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Some settings failed to update'
                }), 400
                
        except Exception as e:
            current_app.logger.error(f"Error updating {category} settings: {str(e)}")
            return jsonify({'error': f'Failed to update {category} settings'}), 500

@settings_bp.route('/api/settings/upload-logo', methods=['POST'])
@jwt_required()
def upload_logo():
    if 'logo' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        try:
            # Secure the filename and create upload directory if needed
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            filepath = os.path.join(upload_folder, unique_filename)
            
            # Save the file
            file.save(filepath)
            
            # Update the logo URL setting
            logo_url = f"/static/uploads/{unique_filename}"
            update_setting('logo_url', logo_url)
            
            return jsonify({
                'success': True,
                'url': logo_url
            })
            
        except Exception as e:
            current_app.logger.error(f"Error uploading logo: {str(e)}")
            return jsonify({'error': 'Failed to upload logo'}), 500
            
    return jsonify({'error': 'Invalid file'}), 400
@app.route('/api/recent-activities')
def recent_activities():
    activities = []

    # Latest employee registration
    latest_employee = Employee.query.order_by(Employee.id.desc()).first()
    if latest_employee:
        activities.append({
            "title": "New employee registered",
            "time": latest_employee.id,
            "description": f"{latest_employee.name} was added to the system"
        })

    # Latest attendance record
    attendance = Attendance.query.order_by(desc(Attendance.timestamp)).first()
    if attendance:
        activities.append({
            "title": "Attendance marked",
            "time": attendance.timestamp,
            "description": f"Employee ID {attendance.user_id} clocked in at {attendance.time_in}"
        })

    # Latest leave request
    leave = LeaveRequest.query.order_by(desc(LeaveRequest.request_date)).first()
    if leave:
        activities.append({
            "title": "Leave request submitted",
            "time": leave.request_date,
            "description": f"User {leave.user_id} requested {leave.leave_type} from {leave.start_date} to {leave.end_date}"
        })

    # Latest payroll
    payroll = Payroll.query.order_by(desc(Payroll.created_at)).first()
    if payroll:
        activities.append({
            "title": "Payroll processed",
            "time": payroll.created_at,
            "description": f"Payroll for employee {payroll.employee_id} processed with net pay {payroll.net_pay}"
        })

    # System logs
    system_log = SystemLog.query.order_by(desc(SystemLog.timestamp)).first()
    if system_log:
        activities.append({
            "title": "System log entry",
            "time": system_log.timestamp,
            "description": f"{system_log.action}: {system_log.details}"
        })

    # Messages
    message = Message.query.order_by(desc(Message.timestamp)).first()
    if message:
        activities.append({
            "title": "New message",
            "time": message.timestamp,
            "description": f"Message from User {message.sender_id} to {message.recipient_id}"
        })

    # Contact messages
    contact_msg = ContactMessage.query.order_by(desc(ContactMessage.timestamp)).first()
    if contact_msg:
        activities.append({
            "title": "New contact message",
            "time": contact_msg.timestamp,
            "description": f"{contact_msg.name} sent a message"
        })

    # Permissions
    permission = Permission.query.order_by(desc(Permission.submitted_at)).first()
    if permission:
        activities.append({
            "title": "Permission request",
            "time": permission.submitted_at,
            "description": f"User {permission.user_id} requested {permission.permission_type} permission"
        })

    # Holidays
    holiday = Holiday.query.order_by(desc(Holiday.date)).first()
    if holiday:
        activities.append({
            "title": "New holiday added",
            "time": holiday.date,
            "description": f"{holiday.title}: {holiday.message}"
        })

    # Notifications
    notification = Notification.query.order_by(desc(Notification.date)).first()
    if notification:
        activities.append({
            "title": "Notification sent",
            "time": notification.date,
            "description": f"{notification.type} notification for employee {notification.employee_id}"
        })

    # Sort all by time descending
    activities.sort(key=lambda x: x['time'], reverse=True)

    return jsonify(activities)
@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    results = []

    if not query:
        return jsonify(results=[])

    # Example searches (expand as needed)
    employees = Employee.query.filter(Employee.name.ilike(f"%{query}%")).all()
    messages = Message.query.filter(Message.content.ilike(f"%{query}%")).all()
    leaves = LeaveRequest.query.filter(LeaveRequest.reason.ilike(f"%{query}%")).all()

    for emp in employees:
        results.append({"type": "Employee", "result": emp.name})

    for msg in messages:
        results.append({"type": "Message", "result": msg.content[:50]})

    for leave in leaves:
        results.append({"type": "Leave Request", "result": leave.reason[:50]})

    return jsonify(results=results)



@app.route('/api/attendance/weekly', methods=['GET'])
def get_weekly_attendance():
    # Get week offset from query param
    offset = int(request.args.get('week_offset', 0))
    
    # Calculate the start of the week (Monday)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
    
    data = {
        'days': [],
        'present': [],
        'absent': []
    }

    total_present = 0
    total_absent = 0

    # Get data for each day of the week
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        present_count = Attendance.query.filter_by(date=day, present=True).count()
        absent_count = Attendance.query.filter_by(date=day, present=False).count()
        
        data['days'].append(day.strftime('%A'))  # e.g., 'Monday'
        data['present'].append(present_count)
        data['absent'].append(absent_count)
        
        total_present += present_count
        total_absent += absent_count

    # Total number of students for percentage calculation
    total_entries = total_present + total_absent
    avg_presence = (total_present / total_entries * 100) if total_entries > 0 else 0

    # Build a list of week options
    available_weeks = []
    for w in range(0, 5):  # Last 5 weeks including current
        week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=w)
        label = f"Week of {week_start.strftime('%b %d')}"
        available_weeks.append({
            'offset': w,
            'label': label
        })

    return jsonify({
        'data': data,
        'stats': {
            'avg_presence': round(avg_presence, 1),
            'total_present': total_present,
            'total_absent': total_absent
        },
        'available_weeks': available_weeks
    })
@app.route('/settings')
def settings():
    tab = request.args.get('tab', 'general')
    
    return render_template('settings.html', active_tab=tab)
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
    print("Database initialized.")
    
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def reports_page():
    # Get all departments for the filter dropdown
    departments = Department.query.all()
    return render_template('reports.html', departments=departments)

@reports_bp.route('/api/attendance/dashboard', methods=['POST'])
def dashboard_data():
    data = request.json
    date_range = data.get('dateRange', 'week')
    department_id = data.get('departmentId', 'all')
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    # Calculate date range based on selection
    today = date.today()
    if date_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif date_range == 'last_week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif date_range == 'month':
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    elif date_range == 'last_month':
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1
        start_date = date(year, last_month, 1)
        end_date = date(year, last_month, calendar.monthrange(year, last_month)[1])
    elif date_range == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        # Default to current week if invalid selection
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    # Base query with date filter
    base_query = (
    db.session.query(
        Attendance.date,
        func.count(Attendance.id).label('count')
    )
    .filter(Attendance.date >= start_date, Attendance.date <= end_date)
    .group_by(Attendance.date)
    .order_by(Attendance.date))

    # Apply department filter if needed
    if department_id != 'all':
        base_query = base_query.join(User).filter(User.department_id == department_id)

    # Get trend data
    trend_data = base_query.all()
    
    # Generate all dates in range for complete trend line
    trend_labels = []
    trend_counts = []
    current_date = start_date
    while current_date <= end_date:
        trend_labels.append(current_date.strftime('%Y-%m-%d'))
        # Find count for this date if exists
        count = next((item.count for item in trend_data if item.date == current_date), 0)
        trend_counts.append(count)
        current_date += timedelta(days=1)

    # Get today's attendance stats
    today_query = db.session.query(
        func.sum(case([(Attendance.present == True, 1)], else_=0)).label('present'),
        func.sum(case([(Attendance.present == False, 1)], else_=0)).label('absent'),
        func.sum(case([(and_(Attendance.present == True, Attendance.time_in > '09:00:00'), 1)], else_=0)).label('late')
    ).filter(Attendance.date == today)

    if department_id != 'all':
        today_query = today_query.join(User).filter(User.department_id == department_id)

    today_stats = today_query.first()

    # Get department-wise performance
    dept_performance = db.session.query(
        Department.name.label('department'),
        func.avg(case([(Attendance.present == True, 100)], else_=0)).label('attendance_rate')
    ).join(User, User.department_id == Department.id).join(Attendance, Attendance.user_id == User.id).filter(Attendance.date >= start_date, Attendance.date <= end_date).group_by(Department.name).order_by(func.avg(case([(Attendance.present == True, 100)], else_=0)).desc()).all()

    # Get top performers (employees with best attendance)
    top_performers = (
        db.session.query(
            User.employee_id,
            User.username.label('name'),
            Department.name.label('department'),
            User.designation,
            func.avg(case([(Attendance.present == True, 100)], else_=0)).label('attendance_percentage')
        )
        .join(Attendance, Attendance.user_id == User.id)
        .join(Department, Department.id == User.department_id)
        .filter(Attendance.date >= start_date, Attendance.date <= end_date)
        .group_by(User.id, Department.name)
        .order_by(func.avg(case([(Attendance.present == True, 100)], else_=0)).desc())
        .limit(5)
        .all()
    )


    # Get total employee count
    total_employees = db.session.query(func.count(User.id))
    if department_id != 'all':
        total_employees = total_employees.filter(User.department_id == department_id)
    total_employees = total_employees.scalar()

    return jsonify({
        'summary': {
            'totalEmployees': total_employees,
            'presentCount': today_stats.present or 0,
            'absentCount': today_stats.absent or 0,
            'lateCount': today_stats.late or 0
        },
        'trend': {
            'labels': trend_labels,
            'data': trend_counts
        },
        'distribution': {
            'present': today_stats.present or 0,
            'absent': today_stats.absent or 0,
            'late': today_stats.late or 0
        },
        'departments': {
            'labels': [dept.department for dept in dept_performance],
            'data': [round(dept.attendance_rate, 1) for dept in dept_performance]
        },
        'topPerformers': [{
            'employee_id': emp.employee_id,
            'name': emp.name,
            'department': emp.department,
            'designation': emp.designation,
            'attendance_percentage': round(emp.attendance_percentage, 1)
        } for emp in top_performers]
    })

@reports_bp.route('/api/attendance/records', methods=['POST'])
def attendance_records():
    data = request.json
    date_range = data.get('dateRange', 'week')
    department_id = data.get('departmentId', 'all')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    page = data.get('page', 1)
    per_page = data.get('perPage', 10)

    # Calculate date range (same as dashboard endpoint)
    today = date.today()
    if date_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif date_range == 'last_week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif date_range == 'month':
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    elif date_range == 'last_month':
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1
        start_date = date(year, last_month, 1)
        end_date = date(year, last_month, calendar.monthrange(year, last_month)[1])
    elif date_range == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    # Base query
    query = (
        db.session.query(
            Attendance.id,
            User.employee_id,
            User.username.label('name'),
            Attendance.date,
            Attendance.present,
            Attendance.time_in,
            Attendance.time_out,
            Attendance.hours,
            case(
                [(and_(Attendance.present == True, Attendance.time_in > '09:00:00'), True)],
                else_=False
            ).label('late')
        )
        .join(User, User.id == Attendance.user_id)
        .filter(Attendance.date >= start_date, Attendance.date <= end_date)
        .order_by(Attendance.date.desc(), User.username)
    )


    # Apply department filter if needed
    if department_id != 'all':
        query = query.filter(User.department_id == department_id)

    # Pagination
    paginated_records = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format the records
    records = []
    for record in paginated_records.items:
        records.append({
            'id': record.id,
            'employee_id': record.employee_id,
            'name': record.name,
            'date': record.date.strftime('%Y-%m-%d'),
            'present': record.present,
            'clock_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'clock_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'hours_worked': round(record.hours, 2) if record.hours else None,
            'late': record.late
        })

    return jsonify({
        'records': records,
        'totalRecords': paginated_records.total
    })

@reports_bp.route('/api/attendance/details/<int:record_id>')
def attendance_details(record_id):
    # Get the attendance record with user details
    record = (
        db.session.query(
            Attendance,
            User.employee_id,
            User.username.label('name'),
            Department.name.label('department'),
            User.designation
        )
        .join(User, User.id == Attendance.user_id)
        .join(Department, Department.id == User.department_id)
        .filter(Attendance.id == record_id)
        .first()
    )

    if not record:
        return jsonify({'error': 'Record not found'}), 404

    attendance, employee_id, name, department, designation = record

    return jsonify({
        'id': attendance.id,
        'employee_id': employee_id,
        'name': name,
        'department': department,
        'designation': designation,
        'date': attendance.date.strftime('%Y-%m-%d'),
        'present': attendance.present,
        'clock_in': attendance.time_in.strftime('%H:%M:%S') if attendance.time_in else None,
        'clock_out': attendance.time_out.strftime('%H:%M:%S') if attendance.time_out else None,
        'hours_worked': round(attendance.hours, 2) if attendance.hours else None,
        'overtime_hours': round(attendance.overtime_hours, 2) if attendance.overtime_hours else None,
        'location_lat': attendance.location_lat,
        'location_lng': attendance.location_lng,
        'location_lat_out': attendance.location_lat_out,
        'location_lng_out': attendance.location_lng_out,
        'confidence': attendance.confidence,
        'late': attendance.time_in and attendance.time_in > datetime.strptime('09:00:00', '%H:%M:%S').time() if attendance.time_in else False,
        'notes': attendance.notes
    })

@reports_bp.route('/api/reports/generate', methods=['POST'])
def generate_report():
    data = request.json
    report_type = data.get('type')
    params = data.get('params', {})
    
    try:
        # Generate report based on type
        if report_type == 'attendance_summary':
            report_data = generate_attendance_summary(params)
        elif report_type == 'department_performance':
            report_data = generate_department_performance(params)
        else:
            return jsonify({'error': 'Invalid report type'}), 400

        # Save report to database
        new_report = Report(
            name=f"{report_type.replace('_', ' ').title()} Report",
            generated_by=current_user.username,
            date=date.today(),
            data=json.dumps(report_data)
        )
        db.session.add(new_report)
        db.session.commit()

        return jsonify({
            'success': True,
            'reportId': new_report.id,
            'reportName': new_report.name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_attendance_summary(params):
    # Similar to dashboard data but with more details
    # Implement based on your specific requirements
    pass

def generate_department_performance(params):
    # Similar to department performance in dashboard but with more details
    pass
notifications_db = []
users_db = {}
def notification_thread():
    """Simulate receiving real-time notifications"""
    notification_id = 1000
    while True:
        time.sleep(15)  # Send a notification every 15 seconds for demo
        
        # Create a sample notification
        notification_id += 1
        notification_type = NOTIFICATION_TYPES[notification_id % len(NOTIFICATION_TYPES)]
        
        new_notification = {
            'id': notification_id,
            'type': notification_type,
            'title': f"New {notification_type} notification",
            'message': f"This is a sample {notification_type} notification sent at {datetime.now().strftime('%H:%M:%S')}",
            'timestamp': datetime.now().isoformat(),
            'is_read': False
        }
        
        notifications_db.insert(0, new_notification)
        
        # Broadcast to all connected clients
        socketio.emit('new_notification', {
            'type': 'new_notification',
            'notification': new_notification
        })

if __name__ == '__main__':
    Thread(target=notification_thread, daemon=True).start()
    
    socketio.run(
        app,
        host='0.0.0.0',  # Allow external connections (optional)
        port=5000,       # Set a specific port (default is 5000)
        debug=True,      # Enable debug mode (auto-reload on changes)
        allow_unsafe_werkzeug=True  # Required if using Werkzeug in production-like environments
    )
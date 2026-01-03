from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from models import db, User, Classroom, Subject, Faculty, Batch, FacultySubject, Timetable, TimetableEntry
from timetable_optimizer import TimetableOptimizer

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration - Using SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/scheduler.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def init_db():
    """Initialize the database with required tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin/admin123")
        
        # Insert sample data if tables are empty
        if Classroom.query.count() == 0:
            insert_sample_data()

def insert_sample_data():
    """Insert sample data for demonstration"""
    try:
        # Sample classrooms
        classrooms_data = [
            Classroom(name='Room 101', capacity=50, type='regular', equipment='Projector, Whiteboard'),
            Classroom(name='Room 102', capacity=60, type='regular', equipment='Projector, Whiteboard, AC'),
            Classroom(name='Lab 201', capacity=30, type='lab', equipment='Computers, Projector'),
            Classroom(name='Lab 202', capacity=25, type='lab', equipment='Computers, Projector, AC'),
            Classroom(name='Auditorium', capacity=200, type='auditorium', equipment='Sound System, Projector')
        ]
        
        for classroom in classrooms_data:
            db.session.add(classroom)
        
        # Sample subjects
        subjects_data = [
            Subject(name='Data Structures', code='CS201', semester=3, department='Computer Science', credits=4, hours_per_week=4),
            Subject(name='Database Systems', code='CS301', semester=5, department='Computer Science', credits=3, hours_per_week=3),
            Subject(name='Web Development', code='CS401', semester=7, department='Computer Science', credits=4, hours_per_week=4),
            Subject(name='Mathematics III', code='MA301', semester=5, department='Mathematics', credits=4, hours_per_week=4),
            Subject(name='Physics II', code='PH201', semester=3, department='Physics', credits=3, hours_per_week=3)
        ]
        
        for subject in subjects_data:
            db.session.add(subject)
        
        # Sample faculty
        faculty_data = [
            Faculty(name='Dr. John Smith', department='Computer Science', email='john.smith@college.edu', max_hours_per_week=20),
            Faculty(name='Prof. Sarah Johnson', department='Computer Science', email='sarah.johnson@college.edu', max_hours_per_week=18),
            Faculty(name='Dr. Michael Brown', department='Mathematics', email='michael.brown@college.edu', max_hours_per_week=22),
            Faculty(name='Prof. Emily Davis', department='Physics', email='emily.davis@college.edu', max_hours_per_week=20),
            Faculty(name='Dr. Robert Wilson', department='Computer Science', email='robert.wilson@college.edu', max_hours_per_week=18)
        ]
        
        for faculty in faculty_data:
            db.session.add(faculty)
        
        # Sample batches
        batches_data = [
            Batch(name='CS-3A', department='Computer Science', semester=3, student_count=45, shift='morning'),
            Batch(name='CS-5B', department='Computer Science', semester=5, student_count=40, shift='morning'),
            Batch(name='CS-7A', department='Computer Science', semester=7, student_count=35, shift='afternoon'),
            Batch(name='MA-5A', department='Mathematics', semester=5, student_count=50, shift='morning'),
            Batch(name='PH-3B', department='Physics', semester=3, student_count=42, shift='morning')
        ]
        
        for batch in batches_data:
            db.session.add(batch)
        
        # Commit all the basic data first
        db.session.commit()
        
        # Create faculty-subject mappings
        faculty_subject_mappings = [
            (1, 1), (1, 2), (1, 3),  # Dr. John Smith - CS subjects
            (2, 1), (2, 2), (2, 3),  # Prof. Sarah Johnson - CS subjects  
            (3, 4),                   # Dr. Michael Brown - Mathematics
            (4, 5),                   # Prof. Emily Davis - Physics
            (5, 1), (5, 3)           # Dr. Robert Wilson - CS subjects
        ]
        
        for faculty_id, subject_id in faculty_subject_mappings:
            faculty_subject = FacultySubject(faculty_id=faculty_id, subject_id=subject_id)
            db.session.add(faculty_subject)
        
        db.session.commit()
        print("Sample data inserted successfully")
        
    except Exception as e:
        print(f"Error inserting sample data: {str(e)}")
        db.session.rollback()

# Authentication decorator
def login_required(f):
    """Decorator to require login for certain routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_field = request.form.get('login_field')
        password = request.form.get('password')
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == login_field) | (User.email == login_field)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password or not confirm_password:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
        
        try:
            # Create new user
            new_user = User(
                username=username,
                email=email,
                role='user'
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics using SQLAlchemy
    stats = {
        'classrooms': Classroom.query.count(),
        'subjects': Subject.query.count(),
        'faculty': Faculty.query.count(),
        'batches': Batch.query.count(),
        'timetables': Timetable.query.count()
    }
    
    # Get recent timetables
    recent_timetables_query = db.session.query(Timetable, Batch, User).join(
        Batch, Timetable.batch_id == Batch.id
    ).join(
        User, Timetable.created_by == User.id
    ).order_by(Timetable.created_at.desc()).limit(5).all()
    
    # Convert to dictionary format for template
    recent_timetables = []
    for timetable, batch, user in recent_timetables_query:
        recent_timetables.append({
            'name': timetable.name,
            'batch_name': batch.name,
            'semester': timetable.semester,
            'academic_year': timetable.academic_year,
            'status': 'active',  # Default status since model doesn't have status field
            'created_by_name': user.username,
            'created_at': timetable.created_at.strftime('%Y-%m-%d %H:%M') if timetable.created_at else 'Unknown'
        })
    
    return render_template('dashboard.html', stats=stats, recent_timetables=recent_timetables)

# API Routes for CRUD operations
@app.route('/api/classrooms', methods=['GET', 'POST'])
@login_required
def api_classrooms():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'capacity']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            classroom = Classroom(
                name=data['name'],
                capacity=int(data['capacity']),
                type=data.get('type', 'regular'),
                equipment=data.get('equipment', '')
            )
            db.session.add(classroom)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error adding classroom: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    try:
        classrooms = Classroom.query.order_by(Classroom.name).all()
        return jsonify([
            {
                'id': c.id,
                'name': c.name,
                'capacity': c.capacity,
                'type': c.type,
                'equipment': c.equipment,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in classrooms
        ])
    except Exception as e:
        print(f"Error fetching classrooms: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classrooms/<int:classroom_id>', methods=['PUT', 'DELETE'])
@login_required
def api_classroom_detail(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'capacity']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            classroom.name = data['name']
            classroom.capacity = int(data['capacity'])
            classroom.type = data.get('type', 'regular')
            classroom.equipment = data.get('equipment', '')
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error updating classroom: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(classroom)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting classroom: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects', methods=['GET', 'POST'])
@login_required
def api_subjects():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'code', 'semester', 'department']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            subject = Subject(
                name=data['name'],
                code=data['code'],
                semester=int(data['semester']),
                department=data['department'],
                credits=int(data.get('credits', 3)),
                hours_per_week=int(data.get('hours_per_week', 3))
            )
            db.session.add(subject)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error adding subject: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    try:
        subjects = Subject.query.order_by(Subject.department, Subject.semester, Subject.name).all()
        return jsonify([
            {
                'id': s.id,
                'name': s.name,
                'code': s.code,
                'semester': s.semester,
                'department': s.department,
                'credits': s.credits,
                'hours_per_week': s.hours_per_week,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in subjects
        ])
    except Exception as e:
        print(f"Error fetching subjects: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects/<int:subject_id>', methods=['PUT', 'DELETE'])
@login_required
def api_subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'code', 'semester', 'department']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            subject.name = data['name']
            subject.code = data['code']
            subject.semester = int(data['semester'])
            subject.department = data['department']
            subject.credits = int(data.get('credits', 3))
            subject.hours_per_week = int(data.get('hours_per_week', 3))
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error updating subject: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(subject)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting subject: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faculty', methods=['GET', 'POST'])
@login_required
def api_faculty():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'department']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            faculty = Faculty(
                name=data['name'],
                department=data['department'],
                email=data.get('email', ''),
                specialization=data.get('specialization', ''),
                max_hours_per_week=int(data.get('max_hours_per_week', 20))
            )
            db.session.add(faculty)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error adding faculty: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    try:
        faculty = Faculty.query.order_by(Faculty.department, Faculty.name).all()
        return jsonify([
            {
                'id': f.id,
                'name': f.name,
                'department': f.department,
                'email': f.email,
                'specialization': f.specialization,
                'max_hours_per_week': f.max_hours_per_week,
                'created_at': f.created_at.isoformat() if f.created_at else None
            } for f in faculty
        ])
    except Exception as e:
        print(f"Error fetching faculty: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faculty/<int:faculty_id>', methods=['PUT', 'DELETE'])
@login_required
def api_faculty_detail(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'department']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            faculty.name = data['name']
            faculty.department = data['department']
            faculty.email = data.get('email', '')
            faculty.specialization = data.get('specialization', '')
            faculty.max_hours_per_week = int(data.get('max_hours_per_week', 20))
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error updating faculty: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(faculty)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting faculty: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/batches', methods=['GET', 'POST'])
@login_required
def api_batches():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'department', 'semester', 'student_count']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            batch = Batch(
                name=data['name'],
                department=data['department'],
                semester=int(data['semester']),
                student_count=int(data['student_count']),
                shift=data.get('shift', 'morning'),
                academic_year=data.get('academic_year', '')
            )
            db.session.add(batch)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error adding batch: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    try:
        batches = Batch.query.order_by(Batch.department, Batch.semester, Batch.name).all()
        return jsonify([
            {
                'id': b.id,
                'name': b.name,
                'department': b.department,
                'semester': b.semester,
                'student_count': b.student_count,
                'shift': b.shift,
                'academic_year': b.academic_year,
                'created_at': b.created_at.isoformat() if b.created_at else None
            } for b in batches
        ])
    except Exception as e:
        print(f"Error fetching batches: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/batches/<int:batch_id>', methods=['PUT', 'DELETE'])
@login_required
def api_batch_detail(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['name', 'department', 'semester', 'student_count']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            batch.name = data['name']
            batch.department = data['department']
            batch.semester = int(data['semester'])
            batch.student_count = int(data['student_count'])
            batch.shift = data.get('shift', 'morning')
            batch.academic_year = data.get('academic_year', '')
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error updating batch: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(batch)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting batch: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-timetable', methods=['POST'])
@login_required
def generate_timetable():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'})
            
        batch_id = data.get('batch_id')
        semester = data.get('semester')
        academic_year = data.get('academic_year')
        
        if not batch_id or not semester or not academic_year:
            return jsonify({'success': False, 'error': 'Missing required parameters'})
        
        print(f"Generating timetable for batch_id: {batch_id}, semester: {semester}")
        
        optimizer = TimetableOptimizer()
        timetable_options = optimizer.generate_optimized_timetables(batch_id, semester)
        
        print(f"Generated {len(timetable_options)} timetable options")
        for i, option in enumerate(timetable_options):
            print(f"Option {i+1}: Score {option['score']}, Classes: {option['total_classes']}")
        
        return jsonify({
            'success': True,
            'options': timetable_options,
            'message': f'Generated {len(timetable_options)} optimized timetable options'
        })
    except Exception as e:
        print(f"Error generating timetable: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timetables', methods=['GET', 'POST'])
@login_required
def api_timetables():
    if request.method == 'GET':
        try:
            # Get all timetables with batch information
            timetables = db.session.query(Timetable, Batch, User).join(
                Batch, Timetable.batch_id == Batch.id
            ).join(
                User, Timetable.created_by == User.id
            ).order_by(Timetable.created_at.desc()).all()
            
            timetables_data = []
            for timetable, batch, user in timetables:
                timetables_data.append({
                    'id': timetable.id,
                    'name': timetable.name,
                    'batch_name': batch.name,
                    'semester': timetable.semester,
                    'academic_year': timetable.academic_year,
                    'created_by': user.username,
                    'created_at': timetable.created_at.strftime('%Y-%m-%d %H:%M') if timetable.created_at else None
                })
            
            return jsonify({'success': True, 'timetables': timetables_data})
        except Exception as e:
            print(f"Error fetching timetables: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timetables/<int:timetable_id>', methods=['GET', 'DELETE'])
@login_required
def api_timetable_detail(timetable_id):
    timetable = Timetable.query.get_or_404(timetable_id)
    
    if request.method == 'GET':
        try:
            # Get timetable entries with related data
            entries = db.session.query(
                TimetableEntry, Subject, Faculty, Classroom
            ).join(
                Subject, TimetableEntry.subject_id == Subject.id
            ).join(
                Faculty, TimetableEntry.faculty_id == Faculty.id
            ).join(
                Classroom, TimetableEntry.classroom_id == Classroom.id
            ).filter(
                TimetableEntry.timetable_id == timetable_id
            ).all()
            
            schedule = []
            for entry, subject, faculty, classroom in entries:
                schedule.append({
                    'day_index': entry.day_of_week,
                    'time_slot': entry.time_slot,
                    'subject_name': subject.name,
                    'subject_code': subject.code,
                    'faculty_name': faculty.name,
                    'classroom_name': classroom.name
                })
            
            return jsonify({
                'success': True,
                'timetable': {
                    'id': timetable.id,
                    'name': timetable.name,
                    'schedule': schedule
                }
            })
        except Exception as e:
            print(f"Error fetching timetable details: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Delete timetable entries first
            TimetableEntry.query.filter_by(timetable_id=timetable_id).delete()
            # Delete timetable
            db.session.delete(timetable)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Timetable deleted successfully'})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting timetable: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-timetable', methods=['POST'])
@login_required
def save_timetable():
    try:
        data = request.json
        
        # Create timetable record
        timetable = Timetable(
            name=data['name'],
            batch_id=data['batch_id'],
            semester=data['semester'],
            academic_year=data['academic_year'],
            created_by=session['user_id']
        )
        db.session.add(timetable)
        db.session.flush()  # Get the ID without committing
        
        # Save timetable entries
        for entry in data['entries']:
            timetable_entry = TimetableEntry(
                timetable_id=timetable.id,
                day_of_week=entry['day'],
                time_slot=entry['time_slot'],
                subject_id=entry['subject_id'],
                faculty_id=entry['faculty_id'],
                classroom_id=entry['classroom_id'],
                batch_id=entry['batch_id']
            )
            db.session.add(timetable_entry)
        
        db.session.commit()
        return jsonify({'success': True, 'timetable_id': timetable.id})
    except Exception as e:
        db.session.rollback()
        print(f"Error saving timetable: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/manage/classrooms')
@login_required
def manage_classrooms():
    return render_template('manage_classrooms.html', entity='classrooms')

@app.route('/manage/subjects')
@login_required
def manage_subjects():
    return render_template('manage_subjects.html', entity='subjects')

@app.route('/manage/faculty')
@login_required
def manage_faculty():
    return render_template('manage_faculty.html', entity='faculty')

@app.route('/manage/batches')
@login_required
def manage_batches():
    return render_template('manage_batches.html', entity='batches')

@app.route('/manage/timetables')
@login_required
def manage_timetables():
    return render_template('manage_timetables.html', entity='timetables')

@app.route('/manage/<string:entity>')
@login_required
def manage_entity(entity):
    valid_entities = ['classrooms', 'subjects', 'faculty', 'batches', 'timetables']
    if entity not in valid_entities:
        return redirect(url_for('dashboard'))
    
    return render_template(f'manage_{entity}.html', entity=entity)

@app.route('/timetable-generator')
@login_required
def timetable_generator():
    return render_template('timetable_generator.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

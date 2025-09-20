from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, Subject, Faculty, Classroom, Batch, Timetable, TimetableEntry, FacultySubject
from timetable_optimizer import TimetableOptimizer
import json
from functools import wraps
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration - MySQL
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def init_db():
    """Initialize the database with required tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
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
        # Check if it's an AJAX request
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        if is_ajax:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form['username']
            password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            if is_ajax:
                return jsonify({
                    'success': True,
                    'message': 'Login successful! Welcome to Smart Classroom Scheduler.',
                    'redirect_url': url_for('dashboard')
                })
            else:
                flash('Login successful! Welcome to Smart Classroom Scheduler.', 'success')
                return redirect(url_for('dashboard'))
        else:
            if is_ajax:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            else:
                flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get statistics
        stats = {
            'classrooms_count': Classroom.query.count(),
            'subjects_count': Subject.query.count(),
            'faculty_count': Faculty.query.count(),
            'batches_count': Batch.query.count(),
            'timetables_count': Timetable.query.count()
        }
        
        # Get recent timetables with proper error handling
        recent_timetables = []
        try:
            recent_timetables_query = db.session.query(Timetable).join(
                Batch, Timetable.batch_id == Batch.id, isouter=True
            ).join(
                User, Timetable.created_by == User.id, isouter=True
            ).order_by(Timetable.created_at.desc()).limit(5).all()
            
            # Format the data for template
            for timetable in recent_timetables_query:
                recent_timetables.append({
                    'id': timetable.id,
                    'name': timetable.name,
                    'batch_name': timetable.batch.name if timetable.batch else 'Unknown',
                    'semester': timetable.semester,
                    'academic_year': timetable.academic_year,
                    'created_by': timetable.creator.username if timetable.creator else 'Unknown',
                    'created_at': timetable.created_at.strftime('%Y-%m-%d %H:%M') if timetable.created_at else 'Unknown',
                    'status': 'active'  # Default status since we don't have this field in the model
                })
        except Exception as e:
            print(f"Error fetching recent timetables: {e}")
            recent_timetables = []
        
        return render_template('dashboard.html', stats=stats, recent_timetables=recent_timetables)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html', stats={'classrooms_count': 0, 'subjects_count': 0, 'faculty_count': 0, 'batches_count': 0, 'timetables_count': 0}, recent_timetables=[])

# Management routes
@app.route('/manage/classrooms')
@login_required
def manage_classrooms():
    return render_template('manage_classrooms.html')

@app.route('/manage/subjects')
@login_required
def manage_subjects():
    return render_template('manage_subjects.html')

@app.route('/manage/faculty')
@login_required
def manage_faculty():
    return render_template('manage_faculty.html')

@app.route('/manage/batches')
@login_required
def manage_batches():
    return render_template('manage_batches.html')

@app.route('/manage/timetables')
@login_required
def manage_timetables():
    return render_template('manage_timetables.html')

@app.route('/timetable-generator')
@login_required
def timetable_generator():
    return render_template('timetable_generator.html')

# API Routes for Classrooms
@app.route('/api/classrooms', methods=['GET', 'POST'])
@login_required
def api_classrooms():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            classroom = Classroom(
                name=data['name'],
                capacity=data['capacity'],
                type=data.get('type', 'regular'),
                equipment=data.get('equipment', '')
            )
            db.session.add(classroom)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Classroom added successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    classrooms = Classroom.query.order_by(Classroom.name).all()
    return jsonify({
        'success': True,
        'classrooms': [{
            'id': c.id,
            'name': c.name,
            'capacity': c.capacity,
            'type': c.type,
            'equipment': c.equipment,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in classrooms]
    })

@app.route('/api/classrooms/<int:classroom_id>', methods=['PUT', 'DELETE'])
@login_required
def api_classroom_detail(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            classroom.name = data.get('name', classroom.name)
            classroom.capacity = data.get('capacity', classroom.capacity)
            classroom.type = data.get('type', classroom.type)
            classroom.equipment = data.get('equipment', classroom.equipment)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Classroom updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(classroom)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Classroom deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Subjects
@app.route('/api/subjects', methods=['GET', 'POST'])
@login_required
def api_subjects():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            subject = Subject(
                name=data['name'],
                code=data['code'],
                semester=data['semester'],
                department=data['department'],
                credits=data.get('credits', 3),
                hours_per_week=data.get('hours_per_week', 3),
                requires_lab=data.get('requires_lab', False),
                scheduling_preference=data.get('scheduling_preference', 'single'),
                continuous_block_size=data.get('continuous_block_size', 2)
            )
            db.session.add(subject)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Subject added successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    subjects = Subject.query.order_by(Subject.department, Subject.semester, Subject.name).all()
    return jsonify({
        'success': True,
        'subjects': [{
            'id': s.id,
            'name': s.name,
            'code': s.code,
            'semester': s.semester,
            'department': s.department,
            'credits': s.credits,
            'hours_per_week': s.hours_per_week,
            'requires_lab': s.requires_lab,
            'created_at': s.created_at.isoformat() if s.created_at else None
        } for s in subjects]
    })

@app.route('/api/subjects/<int:subject_id>', methods=['PUT', 'DELETE'])
@login_required
def api_subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            subject.name = data.get('name', subject.name)
            subject.code = data.get('code', subject.code)
            subject.semester = data.get('semester', subject.semester)
            subject.department = data.get('department', subject.department)
            subject.credits = data.get('credits', subject.credits)
            subject.hours_per_week = data.get('hours_per_week', subject.hours_per_week)
            subject.requires_lab = data.get('requires_lab', subject.requires_lab)
            subject.scheduling_preference = data.get('scheduling_preference', subject.scheduling_preference)
            subject.continuous_block_size = data.get('continuous_block_size', subject.continuous_block_size)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subject updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(subject)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subject deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Faculty
@app.route('/api/faculty', methods=['GET', 'POST'])
@login_required
def api_faculty():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            faculty = Faculty(
                name=data['name'],
                department=data['department'],
                email=data.get('email', ''),
                max_hours_per_day=data.get('max_hours_per_day', 6),
                max_hours_per_week=data.get('max_hours_per_week', 20),
                avg_leaves_per_month=data.get('avg_leaves_per_month', 2)
            )
            db.session.add(faculty)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Faculty added successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    faculty = Faculty.query.order_by(Faculty.department, Faculty.name).all()
    return jsonify({
        'success': True,
        'faculty': [{
            'id': f.id,
            'name': f.name,
            'department': f.department,
            'email': f.email,
            'max_hours_per_day': f.max_hours_per_day,
            'max_hours_per_week': f.max_hours_per_week,
            'avg_leaves_per_month': f.avg_leaves_per_month,
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in faculty]
    })

@app.route('/api/faculty/<int:faculty_id>', methods=['PUT', 'DELETE'])
@login_required
def api_faculty_detail(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            faculty.name = data.get('name', faculty.name)
            faculty.department = data.get('department', faculty.department)
            faculty.email = data.get('email', faculty.email)
            faculty.max_hours_per_day = data.get('max_hours_per_day', faculty.max_hours_per_day)
            faculty.max_hours_per_week = data.get('max_hours_per_week', faculty.max_hours_per_week)
            faculty.avg_leaves_per_month = data.get('avg_leaves_per_month', faculty.avg_leaves_per_month)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Faculty updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(faculty)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Faculty deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Batches
@app.route('/api/batches', methods=['GET', 'POST'])
@login_required
def api_batches():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            batch = Batch(
                name=data['name'],
                department=data['department'],
                semester=data['semester'],
                student_count=data['student_count']
                # shift will be automatically assigned during timetable generation
            )
            db.session.add(batch)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Batch added successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    batches = Batch.query.order_by(Batch.department, Batch.semester, Batch.name).all()
    return jsonify({
        'success': True,
        'batches': [{
            'id': b.id,
            'name': b.name,
            'department': b.department,
            'semester': b.semester,
            'student_count': b.student_count,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in batches]
    })

@app.route('/api/batches/<int:batch_id>', methods=['PUT', 'DELETE'])
@login_required
def api_batch_detail(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            batch.name = data.get('name', batch.name)
            batch.department = data.get('department', batch.department)
            batch.semester = data.get('semester', batch.semester)
            batch.student_count = data.get('student_count', batch.student_count)
            # shift is no longer user-configurable
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Batch updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(batch)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Batch deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Timetables
@app.route('/api/timetables', methods=['GET'])
@login_required
def api_timetables():
    timetables = db.session.query(Timetable, Batch).join(
        Batch, Timetable.batch_id == Batch.id
    ).order_by(Timetable.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'timetables': [{
            'id': t.Timetable.id,
            'name': t.Timetable.name,
            'batch_name': t.Batch.name,
            'semester': t.Timetable.semester,
            'academic_year': t.Timetable.academic_year,
            'status': 'active',
            'created_at': t.Timetable.created_at.isoformat() if t.Timetable.created_at else None
        } for t in timetables]
    })

@app.route('/api/timetables/<int:timetable_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_timetable_detail(timetable_id):
    timetable = Timetable.query.get_or_404(timetable_id)
    
    if request.method == 'GET':
        entries = TimetableEntry.query.filter_by(timetable_id=timetable_id).all()
        
        # Get timing configuration from timetable model
        timing_config = None
        if timetable.timing_config:
            try:
                timing_config = json.loads(timetable.timing_config)
            except:
                timing_config = None
        
        # Format entries with proper names for frontend display
        formatted_entries = []
        for e in entries:
            # Get related objects
            subject = Subject.query.get(e.subject_id) if e.subject_id else None
            faculty = Faculty.query.get(e.faculty_id) if e.faculty_id else None
            classroom = Classroom.query.get(e.classroom_id) if e.classroom_id else None
            
            # Convert day_of_week number to day name
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[e.day_of_week] if e.day_of_week < len(day_names) else 'Unknown'
            
            formatted_entry = {
                'id': e.id,
                'day': day_name,
                'time_slot': e.time_slot,
                'subject_id': e.subject_id,
                'subject_name': subject.name if subject else 'Unknown Subject',
                'subject_code': subject.code if subject else 'N/A',
                'faculty_id': e.faculty_id,
                'faculty_name': faculty.name if faculty else 'Unknown Faculty',
                'classroom_id': e.classroom_id,
                'classroom_name': classroom.name if classroom else 'Unknown Room',
                'batch_id': e.batch_id,
                'is_fixed': False
            }
            formatted_entries.append(formatted_entry)
        
        return jsonify({
            'success': True,
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'batch_id': timetable.batch_id,
                'semester': timetable.semester,
                'academic_year': timetable.academic_year,
                'status': timetable.status,
                'schedule': formatted_entries,  # Use 'schedule' key instead of 'entries'
                'timing_config': timing_config  # Also provide timing config separately
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'})
            
            # Update timetable basic info
            timetable.name = data.get('name', timetable.name)
            timetable.semester = data.get('semester', timetable.semester)
            timetable.academic_year = data.get('academic_year', timetable.academic_year)
            timetable.status = data.get('status', timetable.status)
            
            # Update timetable entries if provided
            if 'entries' in data:
                # Delete existing entries
                TimetableEntry.query.filter_by(timetable_id=timetable_id).delete()
                
                # Add new entries
                for entry_data in data['entries']:
                    # Validate required fields
                    subject_id = entry_data.get('subject_id')
                    faculty_id = entry_data.get('faculty_id')
                    classroom_id = entry_data.get('classroom_id')
                    day_of_week = entry_data.get('day_of_week')
                    time_slot = entry_data.get('time_slot')
                    batch_id = entry_data.get('batch_id')
                    
                    # Skip entries with missing required data
                    if not all([subject_id, faculty_id, classroom_id, day_of_week is not None, time_slot, batch_id]):
                        print(f"WARNING: Skipping entry with missing data - subject_id: {subject_id}, faculty_id: {faculty_id}, classroom_id: {classroom_id}, day_of_week: {day_of_week}, time_slot: {time_slot}, batch_id: {batch_id}")
                        continue
                        
                    entry = TimetableEntry(
                        timetable_id=timetable_id,
                        day_of_week=day_of_week,
                        time_slot=time_slot,
                        subject_id=subject_id,
                        faculty_id=faculty_id,
                        classroom_id=classroom_id,
                        batch_id=batch_id
                    )
                    db.session.add(entry)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Timetable updated successfully'})
        except Exception as e:
            db.session.rollback()
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
            return jsonify({'success': False, 'error': str(e)}), 500

# Timetable generation and saving
@app.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    try:
        data = request.get_json()
        batch_id = data.get('batch_id')
        semester = data.get('semester')
        academic_year = data.get('academic_year')
        college_name = data.get('college_name', '')
        include_short_break = data.get('include_short_break', False)
        short_break_duration = data.get('short_break_duration', 10)
        college_start_time = data.get('college_start_time', '09:00')
        college_end_time = data.get('college_end_time', '16:30')
        lunch_break_duration = data.get('lunch_break_duration', 60)
        lunch_break_start_time = data.get('lunch_break_start_time', '12:15')
        
        print(f"Received timing parameters: start={college_start_time}, end={college_end_time}, lunch_duration={lunch_break_duration}, lunch_start={lunch_break_start_time}")
        
        if not all([batch_id, semester, academic_year]):
            return jsonify({
                'success': False,
                'message': 'Missing required parameters'
            }), 400
        
        # Initialize optimizer with all timing configurations
        optimizer = TimetableOptimizer(
            include_short_break=include_short_break,
            short_break_duration=short_break_duration,
            college_start_time=college_start_time,
            college_end_time=college_end_time,
            lunch_break_duration=lunch_break_duration,
            lunch_break_start_time=lunch_break_start_time
        )
        
        # Generate timetable options
        options = optimizer.generate_optimized_timetables(
            batch_id=batch_id,
            semester=semester,
            include_short_break=include_short_break,
            short_break_duration=short_break_duration,
            college_start_time=college_start_time,
            college_end_time=college_end_time,
            lunch_break_duration=lunch_break_duration,
            lunch_break_start_time=lunch_break_start_time
        )
        
        if not options:
            return jsonify({
                'success': False,
                'message': 'No timetable options could be generated'
            }), 400
        
        return jsonify({
            'success': True,
            'options': options,
            'message': f'Generated {len(options)} timetable options'
        })
        
    except Exception as e:
        print(f"Error generating timetable: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating timetable: {str(e)}'
        }), 500

@app.route('/api/save-timetable', methods=['POST'])
@login_required
def save_timetable():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'})
        
        name = data.get('name')
        batch_id = data.get('batch_id')
        semester = data.get('semester')
        academic_year = data.get('academic_year')
        college_name = data.get('college_name', '')
        print(f"DEBUG: Saving timetable with college_name: '{college_name}'")
        entries = data.get('entries', [])
        
        # Extract timing configuration from request
        timing_config = {
            'college_start_time': data.get('college_start_time', '09:00'),
            'college_end_time': data.get('college_end_time', '16:30'),
            'lunch_break_start_time': data.get('lunch_break_start_time', '12:15'),
            'lunch_break_duration': data.get('lunch_break_duration', 60),
            'include_short_break': data.get('include_short_break', False),
            'short_break_duration': data.get('short_break_duration', 10)
        }
        
        if not all([name, batch_id, semester, academic_year]):
            return jsonify({'success': False, 'error': 'Missing required parameters'})
        
        # Create new timetable with timing configuration
        timetable = Timetable(
            name=name,
            batch_id=batch_id,
            semester=semester,
            academic_year=academic_year,
            college_name=college_name,
            timing_config=json.dumps(timing_config),
            created_by=session['user_id']
        )
        db.session.add(timetable)
        db.session.flush()  # Get the timetable ID
        
        # Add timetable entries
        for entry in entries:
            # Validate required fields
            subject_id = entry.get('subject_id')
            faculty_id = entry.get('faculty_id')
            classroom_id = entry.get('classroom_id')
            day = entry.get('day')
            time_slot = entry.get('time_slot')
            
            # Skip entries with missing required data
            if not all([subject_id, faculty_id, classroom_id, day is not None, time_slot]):
                print(f"WARNING: Skipping entry with missing data - subject_id: {subject_id}, faculty_id: {faculty_id}, classroom_id: {classroom_id}, day: {day}, time_slot: {time_slot}")
                continue
                
            timetable_entry = TimetableEntry(
                timetable_id=timetable.id,
                day_of_week=day,
                time_slot=time_slot,
                subject_id=subject_id,
                faculty_id=faculty_id,
                classroom_id=classroom_id,
                batch_id=batch_id
            )
            db.session.add(timetable_entry)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Timetable "{name}" saved successfully!',
            'timetable_id': timetable.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/insert-sample-data', methods=['POST'])
@login_required
def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Sample Classrooms
        classrooms = [
            {'name': 'Room 101', 'capacity': 60, 'type': 'Lecture Hall', 'has_projector': True, 'has_whiteboard': True},
            {'name': 'Room 102', 'capacity': 40, 'type': 'Classroom', 'has_projector': True, 'has_whiteboard': True},
            {'name': 'Lab 201', 'capacity': 30, 'type': 'Computer Lab', 'has_projector': True, 'has_whiteboard': False},
            {'name': 'Room 203', 'capacity': 50, 'type': 'Classroom', 'has_projector': False, 'has_whiteboard': True}
        ]
        
        for classroom_data in classrooms:
            if not Classroom.query.filter_by(name=classroom_data['name']).first():
                classroom = Classroom(**classroom_data)
                db.session.add(classroom)
        
        # Sample Subjects
        subjects = [
            {'name': 'Data Structures', 'code': 'CS201', 'semester': 3, 'department': 'Computer Science', 'credits': 4, 'hours_per_week': 4, 'requires_lab': True},
            {'name': 'Database Management', 'code': 'CS301', 'semester': 5, 'department': 'Computer Science', 'credits': 3, 'hours_per_week': 3, 'requires_lab': True},
            {'name': 'Mathematics III', 'code': 'MA301', 'semester': 3, 'department': 'Mathematics', 'credits': 4, 'hours_per_week': 4, 'requires_lab': False},
            {'name': 'Software Engineering', 'code': 'CS401', 'semester': 7, 'department': 'Computer Science', 'credits': 3, 'hours_per_week': 3, 'requires_lab': False}
        ]
        
        for subject_data in subjects:
            if not Subject.query.filter_by(code=subject_data['code']).first():
                subject = Subject(**subject_data)
                db.session.add(subject)
        
        # Sample Faculty
        faculty_members = [
            {'name': 'Dr. John Smith', 'department': 'Computer Science', 'email': 'john.smith@university.edu', 'max_hours_per_day': 6, 'max_hours_per_week': 20, 'avg_leaves_per_month': 2},
            {'name': 'Prof. Sarah Johnson', 'department': 'Computer Science', 'email': 'sarah.johnson@university.edu', 'max_hours_per_day': 5, 'max_hours_per_week': 18, 'avg_leaves_per_month': 1},
            {'name': 'Dr. Michael Brown', 'department': 'Mathematics', 'email': 'michael.brown@university.edu', 'max_hours_per_day': 6, 'max_hours_per_week': 22, 'avg_leaves_per_month': 2},
            {'name': 'Dr. Emily Davis', 'department': 'Computer Science', 'email': 'emily.davis@university.edu', 'max_hours_per_day': 5, 'max_hours_per_week': 16, 'avg_leaves_per_month': 3}
        ]
        
        for faculty_data in faculty_members:
            if not Faculty.query.filter_by(email=faculty_data['email']).first():
                faculty = Faculty(**faculty_data)
                db.session.add(faculty)
        
        # Sample Batches
        batches = [
            {'name': 'CS-A-2023', 'department': 'Computer Science', 'semester': 3, 'student_count': 45, 'shift': 'Morning'},
            {'name': 'CS-B-2023', 'department': 'Computer Science', 'semester': 3, 'student_count': 42, 'shift': 'Morning'},
            {'name': 'CS-A-2022', 'department': 'Computer Science', 'semester': 5, 'student_count': 38, 'shift': 'Afternoon'},
            {'name': 'CS-A-2021', 'department': 'Computer Science', 'semester': 7, 'student_count': 35, 'shift': 'Morning'}
        ]
        
        for batch_data in batches:
            if not Batch.query.filter_by(name=batch_data['name']).first():
                batch = Batch(**batch_data)
                db.session.add(batch)
        
        db.session.commit()
        
        # Create Faculty-Subject associations
        faculty_subject_mappings = [
            ('john.smith@university.edu', 'CS201'),
            ('john.smith@university.edu', 'CS301'),
            ('sarah.johnson@university.edu', 'CS301'),
            ('sarah.johnson@university.edu', 'CS401'),
            ('michael.brown@university.edu', 'MA301'),
            ('emily.davis@university.edu', 'CS201'),
            ('emily.davis@university.edu', 'CS401')
        ]
        
        for faculty_email, subject_code in faculty_subject_mappings:
            faculty = Faculty.query.filter_by(email=faculty_email).first()
            subject = Subject.query.filter_by(code=subject_code).first()
            
            if faculty and subject:
                existing = FacultySubject.query.filter_by(faculty_id=faculty.id, subject_id=subject.id).first()
                if not existing:
                    faculty_subject = FacultySubject(faculty_id=faculty.id, subject_id=subject.id)
                    db.session.add(faculty_subject)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sample data inserted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def convert_24_to_12_hour(time_str):
    """Convert 24-hour time format to 12-hour format with AM/PM"""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    except:
        return time_str

@app.route('/api/download-timetable-pdf/<int:timetable_id>')
@login_required
def download_timetable_pdf(timetable_id):
    try:
        # Get timetable data
        timetable = Timetable.query.get_or_404(timetable_id)
        entries = TimetableEntry.query.filter_by(timetable_id=timetable_id).all()
        
        # Get batch info
        batch = Batch.query.get(timetable.batch_id)
        
        # Parse timing configuration
        timing_config = json.loads(timetable.timing_config) if timetable.timing_config else {}
        
        # Create PDF buffer with landscape orientation for better timetable display
        from reportlab.lib.pagesizes import landscape
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # College header style
        college_style = ParagraphStyle(
            'CollegeHeader',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=5,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        # Department style
        dept_style = ParagraphStyle(
            'DeptHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        # Add configurable college name - FORCE USE WHAT USER ENTERED
        college_name = timetable.college_name if timetable.college_name and timetable.college_name.strip() else "SRKR Engg. College (A) (Affiliated to JNTU Kakinada), Bhimavaram-534 204, India"
        print(f"DEBUG: Using college name: '{college_name}' (from timetable.college_name: '{timetable.college_name}')")
        college_para = Paragraph(college_name, college_style)
        elements.append(college_para)
        
        # Add department name - ALWAYS
        department_name = "Department of Computer Science and Engineering"
        dept_para = Paragraph(department_name, dept_style)
        elements.append(dept_para)
        
        # Extract section from batch name (e.g., "CSE-A-2025" -> "Sec-A")
        section = "Sec-A"  # Default section
        if batch and batch.name:
            # Try to extract section from batch name patterns like "CSE-A", "CSE-A-2025", etc.
            parts = batch.name.split('-')
            if len(parts) >= 2:
                section = f"Sec-{parts[1]}"
            elif len(parts) == 1 and len(batch.name) > 3:
                # Handle cases like "CSEA" -> "Sec-A"
                section = f"Sec-{batch.name[-1]}"
        
        # Create info table with timetable details
        info_data = [
            [f"{section}", f"B.Tech. AIML: {timetable.academic_year} {timetable.semester}{'st' if timetable.semester == 1 else 'nd' if timetable.semester == 2 else 'rd' if timetable.semester == 3 else 'th'} Semester", f"w.e.f. {datetime.now().strftime('%d-%m-%Y')}", f"Room: H-301"]
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 15))
        
        # Generate timetable grid
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        # FIXED TIMING CONFIGURATION - FORCE LUNCH BREAK 12:00-13:30
        college_start = '09:00'
        college_end = '16:30'
        lunch_start = '12:00'  # FIXED lunch start time
        lunch_end = '13:30'    # FIXED lunch end time
        lunch_duration = 90    # FIXED 90 minutes (1.5 hours) for lunch break
        
        # Generate complete time slots MATCHING REFERENCE IMAGE
        def generate_complete_time_slots_with_labs():
            slots = []
            
            # Based on reference image - create all time slots
            slots.append("09:00-09:45")   # 1st period
            slots.append("09:45-10:30")   # 2nd period  
            slots.append("10:30-11:15")   # 3rd period
            slots.append("11:15-12:00")   # 4th period
            slots.append("12:00-13:30")   # Lunch break
            slots.append("01:30-02:15")   # 5th period
            slots.append("02:15-03:00")   # 6th period
            slots.append("03:00-03:45")   # 7th period
            slots.append("03:45-04:30")   # 8th period
            slots.append("04:30-05:15")   # 9th period (Sports/Counselling)
            
            return slots
        
        time_slots = generate_complete_time_slots_with_labs()
        
        # Function to map database time slots to PDF time slots
        def map_db_time_to_pdf_time(db_time):
            """Map database time format to PDF time format"""
            time_mapping = {
                "09:00-09:45": "09:00-09:45",
                "09:45-10:30": "09:45-10:30", 
                "10:30-11:15": "10:30-11:15",
                "11:15-12:00": "11:15-12:00",
                "12:00-13:30": "12:00-13:30",
                "13:30-14:15": "01:30-02:15",
                "14:15-15:00": "02:15-03:00",
                "15:00-15:45": "03:00-03:45",
                "15:45-16:30": "03:45-04:30",
                "16:30-17:15": "04:30-05:15",
                # Alternative formats
                "01:30-02:15": "01:30-02:15",
                "02:15-03:00": "02:15-03:00",
                "03:00-03:45": "03:00-03:45",
                "03:45-04:30": "03:45-04:30",
                "04:30-05:15": "04:30-05:15",
            }
            return time_mapping.get(db_time, db_time)
        
        # Debug: Print time slots to see what's generated
        print(f"DEBUG: Generated time slots: {time_slots}")
        print(f"DEBUG: Lunch start: {lunch_start}, Duration: {lunch_duration}")
        print(f"DEBUG: College: {college_name}")
        print(f"DEBUG: Department: {department_name}")
        print(f"DEBUG: Section: {section}")
        
        # Format entries exactly like the web interface does
        formatted_entries = []
        for e in entries:
            # Get related objects
            subject = Subject.query.get(e.subject_id) if e.subject_id else None
            faculty = Faculty.query.get(e.faculty_id) if e.faculty_id else None
            classroom = Classroom.query.get(e.classroom_id) if e.classroom_id else None
            
            # Convert day_of_week number to day name
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[e.day_of_week] if e.day_of_week < len(day_names) else 'Unknown'
            
            formatted_entry = {
                'day': day_name,
                'time_slot': e.time_slot,
                'subject_id': e.subject_id,  # Include subject_id for lab checking
                'subject_name': subject.name if subject else 'Unknown Subject',
                'subject_code': subject.code if subject else 'N/A',
                'faculty_name': faculty.name if faculty else 'Unknown Faculty',
                'classroom_name': classroom.name if classroom else 'Unknown Room',
                'requires_lab': subject.requires_lab if subject else False  # Include lab flag
            }
            formatted_entries.append(formatted_entry)
        
        print(f"DEBUG: Processing {len(formatted_entries)} formatted entries")
        for entry in formatted_entries:
            print(f"DEBUG: Entry - Day: {entry['day']}, Time: {entry['time_slot']}, Subject: {entry['subject_name']}")
        
        # Create timetable data structure using formatted entries
        timetable_data = {}
        
        # Initialize grid with empty slots for each day
        for day_idx, day_name in enumerate(days):
            timetable_data[day_name] = {}
        
        # Use the same time slot generation as web interface
        # Get timing configuration from timetable model
        timing_config = None
        if timetable.timing_config:
            try:
                timing_config = json.loads(timetable.timing_config)
            except:
                timing_config = None
        
        # Use timing config or defaults
        college_start = timing_config.get('college_start_time', '09:00') if timing_config else '09:00'
        college_end = timing_config.get('college_end_time', '16:30') if timing_config else '16:30'
        lunch_start = timing_config.get('lunch_break_start_time', '12:00') if timing_config else '12:00'
        lunch_duration = timing_config.get('lunch_break_duration', 90) if timing_config else 90
        
        print(f"DEBUG: Using timing config - Start: {college_start}, End: {college_end}, Lunch: {lunch_start}, Duration: {lunch_duration}")
        
        # Populate grid with formatted entries - handle lab sessions properly
        for entry in formatted_entries:
            day = entry['day']
            time_slot = entry['time_slot']
            subject_name = entry['subject_name']
            
            # Check if this is a lab subject
            is_lab = entry.get('requires_lab', False)
            
            if day in timetable_data:
                if is_lab and time_slot in ["09:00-12:00", "13:30-16:30"]:
                    # For lab sessions, mark the entire 3-hour block
                    timetable_data[day][time_slot] = f"{subject_name} (LAB)"
                    print(f"DEBUG: Placed LAB {subject_name} at {day} {time_slot} (3-hour block)")
                else:
                    # For regular classes
                    timetable_data[day][time_slot] = subject_name
                    print(f"DEBUG: Placed {subject_name} at {day} {time_slot}")
        
        print(f"DEBUG: Final timetable_data: {timetable_data}")
        
        # Create table data for PDF
        table_data = []
        
        # Header row with time slots - MATCHING REFERENCE IMAGE
        header_row = ['Day/Time']
        for slot in time_slots:
            if slot == "09:00-09:45":
                header_row.append("09:00-09:45")
            elif slot == "09:45-10:30":
                header_row.append("09:45-10:30")
            elif slot == "10:30-11:15":
                header_row.append("10:30-11:15")
            elif slot == "11:15-12:00":
                header_row.append("11:15-12:00")
            elif slot == "12:00-13:30":
                header_row.append("12:00-01:30")
            elif slot == "01:30-02:15":
                header_row.append("01:30-02:15")
            elif slot == "02:15-03:00":
                header_row.append("02:15-03:00")
            elif slot == "03:00-03:45":
                header_row.append("03:00-03:45")
            elif slot == "03:45-04:30":
                header_row.append("03:45-04:30")
            elif slot == "04:30-05:15":
                header_row.append("04:30-05:15")
            else:
                header_row.append(slot)
        table_data.append(header_row)
        
        # Add rows for each day - USE ACTUAL TIMETABLE DATA WITH DAY NAMES
        for day_name in days:
            row = [day_name]
            for time_slot in time_slots:
                if time_slot == "12:00-13:30":
                    row.append("LUNCH BREAK")
                elif time_slot == "04:30-05:15":
                    # Last period - check if there's actual scheduled content
                    cell_content = timetable_data.get(day_name, {}).get(time_slot, "")
                    if cell_content:
                        row.append(cell_content)
                    else:
                        row.append("---")
                else:
                    # Get actual class content from timetable data (using day names as keys)
                    cell_content = timetable_data.get(day_name, {}).get(time_slot, "")
                    row.append(cell_content)
            table_data.append(row)
        
        # Calculate optimal column widths for landscape orientation
        available_width = landscape(A4)[0] - 72  # Total width minus margins
        day_col_width = 0.8*inch
        time_col_width = (available_width - day_col_width) / len(time_slots)
        col_widths = [day_col_width] + [time_col_width] * len(time_slots)
        
        table = Table(table_data, colWidths=col_widths)
        
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            
            # Day column styling
            ('BACKGROUND', (0, 1), (0, -1), colors.lightblue),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 8),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.darkblue),
            
            # Data cells styling
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            
            # Alternating row colors for better readability
            ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        # Special styling for lunch break cells and class cells
        for row_idx in range(1, len(table_data)):
            for col_idx, time_slot in enumerate(time_slots):
                if time_slot == "12:00-13:30":
                    # Lunch break styling
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (col_idx + 1, row_idx), (col_idx + 1, row_idx), colors.orange),
                        ('FONTNAME', (col_idx + 1, row_idx), (col_idx + 1, row_idx), 'Helvetica-Bold'),
                        ('TEXTCOLOR', (col_idx + 1, row_idx), (col_idx + 1, row_idx), colors.white),
                    ]))
                else:
                    # Check if this cell has class data (including lab data)
                    day_idx = row_idx - 1
                    cell_content = table_data[row_idx][col_idx + 1]  # Get actual cell content from table
                    if cell_content and cell_content.strip():
                        # Determine if it's a lab or regular class
                        is_lab = "LAB" in cell_content.upper()
                        if is_lab:
                            # Lab cell styling (blue background)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (col_idx + 1, row_idx), (col_idx + 1, row_idx), colors.lightblue),
                                ('FONTNAME', (col_idx + 1, row_idx), (col_idx + 1, row_idx), 'Helvetica-Bold'),
                            ]))
                        else:
                            # Regular class cell styling (light green)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (col_idx + 1, row_idx), (col_idx + 1, row_idx), colors.lightgreen),
                                ('FONTNAME', (col_idx + 1, row_idx), (col_idx + 1, row_idx), 'Helvetica-Bold'),
                            ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add Course Details Table (matching reference image)
        course_title_style = ParagraphStyle(
            'CourseTitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        course_title = Paragraph("Course Details", course_title_style)
        elements.append(course_title)
        
        # Get ONLY subjects that are actually scheduled in this timetable
        scheduled_subject_ids = set()
        for entry in entries:
            if entry.subject_id:
                scheduled_subject_ids.add(entry.subject_id)
        
        # Get only the subjects that are actually in the timetable
        subjects = []
        for subject_id in scheduled_subject_ids:
            subject = Subject.query.get(subject_id)
            if subject:
                subjects.append(subject)
        
        print(f"DEBUG: Found {len(subjects)} scheduled subjects: {[s.name for s in subjects]}")
        
        # Create course details table
        course_data = [
            ['Course Code', 'Course (Credits)', 'Teacher', 'Lec.', 'Tut.', 'Lab']
        ]
        
        total_lec = 0
        total_tut = 0
        total_lab = 0
        
        for subject in subjects:
            # Get faculty for this subject
            faculty_subjects = FacultySubject.query.filter_by(subject_id=subject.id).first()
            faculty_name = "TBD"
            if faculty_subjects:
                faculty = Faculty.query.get(faculty_subjects.faculty_id)
                if faculty:
                    faculty_name = faculty.name
            
            # Calculate hours based on subject type
            lec_hours = subject.hours_per_week if not subject.requires_lab else max(0, subject.hours_per_week - 3)
            tut_hours = 1 if subject.credits >= 3 and not subject.requires_lab else 0
            lab_hours = 3 if subject.requires_lab else 0
            
            total_lec += lec_hours
            total_tut += tut_hours
            total_lab += lab_hours
            
            course_data.append([
                subject.code,
                f"{subject.name} ({subject.credits})",
                faculty_name,
                str(lec_hours),
                str(tut_hours),
                str(lab_hours)
            ])
        
        # Add total row
        course_data.append([
            '',
            'Total',
            '',
            str(total_lec),
            str(total_tut),
            str(total_lab)
        ])
        
        # Create course table
        course_table = Table(course_data, colWidths=[1*inch, 4*inch, 2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        course_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Total row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
        ]))
        
        elements.append(course_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="timetable_{timetable.name}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Database already initialized with fix_db.py script
    # init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

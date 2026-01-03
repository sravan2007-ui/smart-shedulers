"""
Enhanced Database Models for Complex Timetable Management
Supports fixed classrooms, lab sharing, and advanced allocation logic
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Computer Science and Engineering"
    code = db.Column(db.String(10), nullable=False)   # e.g., "CSE"
    head_of_department = db.Column(db.String(100))
    
    # Relationships
    batches = db.relationship('Batch', backref='dept', lazy=True)
    subjects = db.relationship('Subject', backref='dept', lazy=True)
    faculty = db.relationship('Faculty', backref='dept', lazy=True)

class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Artificial Intelligence and Machine Learning"
    code = db.Column(db.String(10), nullable=False)   # e.g., "AIML"
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Relationships
    batches = db.relationship('Batch', backref='branch_info', lazy=True)

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    building = db.Column(db.String(50))
    floor = db.Column(db.Integer)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Enhanced classroom properties
    room_type = db.Column(db.String(20), default='theory')  # theory, lab, seminar, auditorium
    equipment = db.Column(db.Text)  # JSON string of available equipment
    is_fixed_allocation = db.Column(db.Boolean, default=False)  # For fixed classrooms
    fixed_for_batches = db.Column(db.Text)  # JSON array of batch IDs this room is fixed for
    
    # Lab-specific properties
    lab_type = db.Column(db.String(50))  # programming, hardware, research, etc.
    software_available = db.Column(db.Text)  # JSON array of software
    
    # Availability
    is_active = db.Column(db.Boolean, default=True)
    maintenance_schedule = db.Column(db.Text)  # JSON for maintenance windows
    
    def get_equipment_list(self):
        """Get equipment as Python list"""
        if self.equipment:
            try:
                return json.loads(self.equipment)
            except:
                return []
        return []
    
    def set_equipment_list(self, equipment_list):
        """Set equipment from Python list"""
        self.equipment = json.dumps(equipment_list)
    
    def get_fixed_batches(self):
        """Get fixed batch IDs as Python list"""
        if self.fixed_for_batches:
            try:
                return json.loads(self.fixed_for_batches)
            except:
                return []
        return []
    
    def set_fixed_batches(self, batch_ids):
        """Set fixed batch IDs from Python list"""
        self.fixed_for_batches = json.dumps(batch_ids)

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    # Enhanced subject properties
    subject_type = db.Column(db.String(20), default='theory')  # theory, lab, project, seminar
    credits = db.Column(db.Integer, default=3)
    
    # Hours per week
    theory_hours = db.Column(db.Integer, default=0)
    lab_hours = db.Column(db.Integer, default=0)
    tutorial_hours = db.Column(db.Integer, default=0)
    
    # Requirements
    requires_lab = db.Column(db.Boolean, default=False)
    required_lab_type = db.Column(db.String(50))  # programming, hardware, etc.
    required_software = db.Column(db.Text)  # JSON array
    min_room_capacity = db.Column(db.Integer, default=30)
    
    # Scheduling preferences
    preferred_time_slots = db.Column(db.Text)  # JSON array of preferred slots
    avoid_time_slots = db.Column(db.Text)  # JSON array of slots to avoid
    
    def get_required_software(self):
        """Get required software as Python list"""
        if self.required_software:
            try:
                return json.loads(self.required_software)
            except:
                return []
        return []

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Enhanced faculty properties
    designation = db.Column(db.String(50))  # Professor, Associate Professor, etc.
    specialization = db.Column(db.String(200))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer, default=0)
    
    # Availability and preferences
    max_hours_per_week = db.Column(db.Integer, default=20)
    preferred_subjects = db.Column(db.Text)  # JSON array of subject IDs
    unavailable_slots = db.Column(db.Text)  # JSON array of unavailable time slots
    
    # Contact information
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    def get_preferred_subjects(self):
        """Get preferred subject IDs as Python list"""
        if self.preferred_subjects:
            try:
                return json.loads(self.preferred_subjects)
            except:
                return []
        return []

class Batch(db.Model):
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "AIML-A"
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Basic properties
    semester = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)  # e.g., "2024-25"
    student_count = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(5), nullable=False)  # A, B, C, D
    
    # Enhanced properties
    year_of_study = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    shift = db.Column(db.String(10), default='morning')  # morning, evening
    
    # Classroom allocation
    has_fixed_classroom = db.Column(db.Boolean, default=False)
    fixed_classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=True)
    priority_for_allocation = db.Column(db.Integer, default=1)  # Higher number = higher priority
    
    # Scheduling preferences
    preferred_start_time = db.Column(db.String(10))  # e.g., "09:00"
    preferred_end_time = db.Column(db.String(10))    # e.g., "16:30"
    lunch_break_duration = db.Column(db.Integer, default=60)  # minutes
    
    # Relationships
    fixed_classroom = db.relationship('Classroom', foreign_keys=[fixed_classroom_id])
    timetables = db.relationship('Timetable', backref='batch', lazy=True)

class FacultySubjectMapping(db.Model):
    __tablename__ = 'faculty_subject_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    
    # Mapping properties
    is_primary_faculty = db.Column(db.Boolean, default=True)
    handles_theory = db.Column(db.Boolean, default=True)
    handles_lab = db.Column(db.Boolean, default=False)
    handles_tutorial = db.Column(db.Boolean, default=False)
    
    # Relationships
    faculty = db.relationship('Faculty', backref='subject_mappings')
    subject = db.relationship('Subject', backref='faculty_mappings')
    batch = db.relationship('Batch', backref='faculty_mappings')

class Timetable(db.Model):
    __tablename__ = 'timetables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    
    # Enhanced properties
    college_name = db.Column(db.String(200))
    department_name = db.Column(db.String(100))
    effective_from = db.Column(db.Date)
    effective_to = db.Column(db.Date)
    
    # Status and metadata
    status = db.Column(db.String(20), default='draft')  # draft, active, archived
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration
    timing_config = db.Column(db.Text)  # JSON for timing configuration
    
    # Relationships
    entries = db.relationship('TimetableEntry', backref='timetable', lazy=True, cascade='all, delete-orphan')

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    
    # Time and day
    day_of_week = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    time_slot = db.Column(db.String(20), nullable=False)    # e.g., "09:00-09:50"
    period_number = db.Column(db.Integer, nullable=False)   # 1, 2, 3, etc.
    
    # Subject and faculty
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    
    # Classroom allocation
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=True)
    is_shared_classroom = db.Column(db.Boolean, default=False)  # If classroom is shared with other batches
    
    # Entry type and properties
    entry_type = db.Column(db.String(20), default='class')  # class, lab, break, lunch, free
    is_lab_session = db.Column(db.Boolean, default=False)
    lab_batch_division = db.Column(db.String(10))  # For dividing batch into smaller groups
    
    # Special entries
    is_break = db.Column(db.Boolean, default=False)
    break_type = db.Column(db.String(20))  # short_break, lunch_break
    is_free_period = db.Column(db.Boolean, default=False)
    
    # Notes and additional info
    notes = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    
    # Relationships
    subject = db.relationship('Subject')
    faculty = db.relationship('Faculty')
    classroom = db.relationship('Classroom')

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # User properties
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # admin, user, faculty
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    created_timetables = db.relationship('Timetable', backref='creator', lazy=True)

# Helper function to create all tables
def create_enhanced_tables(app):
    """Create all enhanced tables"""
    with app.app_context():
        db.create_all()
        print("Enhanced database tables created successfully!")

# Migration function to add new columns to existing tables
def migrate_existing_database(app):
    """Add new columns to existing tables without losing data"""
    with app.app_context():
        try:
            # Add new columns to existing tables
            db.engine.execute("""
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS room_type VARCHAR(20) DEFAULT 'theory';
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS equipment TEXT;
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS is_fixed_allocation BOOLEAN DEFAULT FALSE;
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS fixed_for_batches TEXT;
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS lab_type VARCHAR(50);
                ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS software_available TEXT;
                
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS subject_type VARCHAR(20) DEFAULT 'theory';
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 3;
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS theory_hours INTEGER DEFAULT 0;
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS lab_hours INTEGER DEFAULT 0;
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS requires_lab BOOLEAN DEFAULT FALSE;
                
                ALTER TABLE batches ADD COLUMN IF NOT EXISTS branch_id INTEGER;
                ALTER TABLE batches ADD COLUMN IF NOT EXISTS year_of_study INTEGER DEFAULT 1;
                ALTER TABLE batches ADD COLUMN IF NOT EXISTS has_fixed_classroom BOOLEAN DEFAULT FALSE;
                ALTER TABLE batches ADD COLUMN IF NOT EXISTS fixed_classroom_id INTEGER;
                
                ALTER TABLE timetable_entries ADD COLUMN IF NOT EXISTS is_shared_classroom BOOLEAN DEFAULT FALSE;
                ALTER TABLE timetable_entries ADD COLUMN IF NOT EXISTS is_lab_session BOOLEAN DEFAULT FALSE;
                ALTER TABLE timetable_entries ADD COLUMN IF NOT EXISTS entry_type VARCHAR(20) DEFAULT 'class';
            """)
            print("Database migration completed successfully!")
        except Exception as e:
            print(f"Migration error (may be expected if columns already exist): {e}")

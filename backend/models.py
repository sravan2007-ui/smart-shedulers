from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), default='regular')  # 'regular', 'lab', 'auditorium'
    equipment = db.Column(db.Text)
    is_fixed_allocation = db.Column(db.Boolean, default=False)  # True if assigned to specific batch
    fixed_batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)  # Fixed batch assignment
    priority_level = db.Column(db.Integer, default=1)  # 1=High, 2=Medium, 3=Low priority for allocation
    can_be_shared = db.Column(db.Boolean, default=True)  # Can be temporarily allocated to others
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fixed_batch = db.relationship('Batch', backref='fixed_classrooms', foreign_keys=[fixed_batch_id])

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, default=3)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    hours_per_week = db.Column(db.Integer, default=3)
    requires_lab = db.Column(db.Boolean, default=False)
    scheduling_preference = db.Column(db.String(20), default='single')  # 'single', 'continuous', 'mixed'
    continuous_block_size = db.Column(db.Integer, default=2)  # Number of classes in continuous block
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    max_hours_per_day = db.Column(db.Integer, default=6)
    max_hours_per_week = db.Column(db.Integer, default=20)
    avg_leaves_per_month = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Batch(db.Model):
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "CSE-A-2025"
    department = db.Column(db.String(100), nullable=False)  # e.g., "Computer Science"
    branch = db.Column(db.String(100), nullable=False)  # e.g., "CSE", "ECE", "MECH"
    section = db.Column(db.String(10), nullable=False)  # e.g., "A", "B", "C"
    semester = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(20), nullable=True)
    student_count = db.Column(db.Integer, default=60)
    shift = db.Column(db.String(20), default='morning')
    priority_for_allocation = db.Column(db.Integer, default=2)  # 1=High, 2=Medium, 3=Low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FacultySubject(db.Model):
    __tablename__ = 'faculty_subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    department = db.Column(db.String(100), nullable=True)  # Department for which this assignment is valid
    branch = db.Column(db.String(100), nullable=True)  # Branch for which this assignment is valid
    semester = db.Column(db.Integer, nullable=True)  # Semester for which this assignment is valid
    is_primary = db.Column(db.Boolean, default=True)  # Primary faculty for this subject
    priority = db.Column(db.Integer, default=1)  # 1=High, 2=Medium, 3=Low priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    faculty = db.relationship('Faculty', backref=db.backref('faculty_subjects', cascade='all, delete-orphan'))
    subject = db.relationship('Subject', backref=db.backref('faculty_subjects', cascade='all, delete-orphan'))

class Timetable(db.Model):
    __tablename__ = 'timetables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    timing_config = db.Column(db.Text, nullable=True)  # JSON string for timing configuration
    college_name = db.Column(db.String(200), nullable=True)  # Configurable college name
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    batch = db.relationship('Batch', backref='timetables')
    creator = db.relationship('User', backref='created_timetables')

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    time_slot = db.Column(db.String(20), nullable=False)    # 09:00-10:00
    is_temporary_allocation = db.Column(db.Boolean, default=False)  # True if using borrowed classroom
    original_classroom_owner_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)  # Original owner batch
    allocation_reason = db.Column(db.String(100), nullable=True)  # 'lab_session', 'capacity_need', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    timetable = db.relationship('Timetable', backref='entries')
    batch = db.relationship('Batch', backref='timetable_entries', foreign_keys=[batch_id])
    subject = db.relationship('Subject', backref='timetable_entries')
    faculty = db.relationship('Faculty', backref='timetable_entries')
    classroom = db.relationship('Classroom', backref='timetable_entries')
    original_owner = db.relationship('Batch', backref='borrowed_classroom_entries', foreign_keys=[original_classroom_owner_id])

class ClassroomAllocation(db.Model):
    __tablename__ = 'classroom_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    time_slot = db.Column(db.String(20), nullable=False)
    allocation_type = db.Column(db.String(20), default='regular')  # 'fixed', 'temporary', 'shared'
    priority_score = db.Column(db.Integer, default=0)  # Higher score = higher priority
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    classroom = db.relationship('Classroom', backref='allocations')
    batch = db.relationship('Batch', backref='classroom_allocations')

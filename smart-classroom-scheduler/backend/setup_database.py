#!/usr/bin/env python3
"""
Database setup script for Smart Classroom Scheduler
This script creates the PostgreSQL database and populates it with sample data
"""

import os
import sys
import pymysql
from dotenv import load_dotenv
from flask import Flask
from models import db, User, Classroom, Subject, Faculty, Batch, FacultySubject
from werkzeug.security import generate_password_hash

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:sravan167@localhost:3306/smart_classroom_scheduler')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    # Sample Classrooms
    classrooms_data = [
        {'name': 'Room A101', 'capacity': 60, 'type': 'regular', 'equipment': 'Projector, Whiteboard'},
        {'name': 'Room A102', 'capacity': 50, 'type': 'regular', 'equipment': 'Projector, Whiteboard'},
        {'name': 'Lab B201', 'capacity': 30, 'type': 'lab', 'equipment': 'Computers, Projector'},
        {'name': 'Lab B202', 'capacity': 25, 'type': 'lab', 'equipment': 'Computers, Projector'},
        {'name': 'Hall C301', 'capacity': 100, 'type': 'auditorium', 'equipment': 'Audio System, Projector'},
    ]
    
    for classroom_data in classrooms_data:
        if not Classroom.query.filter_by(name=classroom_data['name']).first():
            classroom = Classroom(**classroom_data)
            db.session.add(classroom)
    
    # Sample Subjects
    subjects_data = [
        {'name': 'Data Structures', 'code': 'CS201', 'credits': 4, 'department': 'Computer Science', 'semester': 3, 'hours_per_week': 4},
        {'name': 'Database Systems', 'code': 'CS301', 'credits': 3, 'department': 'Computer Science', 'semester': 5, 'hours_per_week': 3},
        {'name': 'Operating Systems', 'code': 'CS302', 'credits': 4, 'department': 'Computer Science', 'semester': 5, 'hours_per_week': 4},
        {'name': 'Computer Networks', 'code': 'CS401', 'credits': 3, 'department': 'Computer Science', 'semester': 7, 'hours_per_week': 3},
        {'name': 'Software Engineering', 'code': 'CS402', 'credits': 3, 'department': 'Computer Science', 'semester': 7, 'hours_per_week': 3},
        {'name': 'Circuit Analysis', 'code': 'EE201', 'credits': 4, 'department': 'Electrical Engineering', 'semester': 3, 'hours_per_week': 4},
        {'name': 'Digital Electronics', 'code': 'EE301', 'credits': 3, 'department': 'Electrical Engineering', 'semester': 5, 'hours_per_week': 3},
        {'name': 'Power Systems', 'code': 'EE401', 'credits': 4, 'department': 'Electrical Engineering', 'semester': 7, 'hours_per_week': 4},
    ]
    
    for subject_data in subjects_data:
        if not Subject.query.filter_by(code=subject_data['code']).first():
            subject = Subject(**subject_data)
            db.session.add(subject)
    
    # Sample Faculty
    faculty_data = [
        {'name': 'Dr. John Smith', 'email': 'john.smith@university.edu', 'department': 'Computer Science', 'specialization': 'Data Structures, Algorithms', 'max_hours_per_week': 20},
        {'name': 'Prof. Sarah Johnson', 'email': 'sarah.johnson@university.edu', 'department': 'Computer Science', 'specialization': 'Database Systems, Software Engineering', 'max_hours_per_week': 18},
        {'name': 'Dr. Michael Brown', 'email': 'michael.brown@university.edu', 'department': 'Computer Science', 'specialization': 'Operating Systems, Networks', 'max_hours_per_week': 22},
        {'name': 'Prof. Emily Davis', 'email': 'emily.davis@university.edu', 'department': 'Electrical Engineering', 'specialization': 'Circuit Analysis, Power Systems', 'max_hours_per_week': 20},
        {'name': 'Dr. Robert Wilson', 'email': 'robert.wilson@university.edu', 'department': 'Electrical Engineering', 'specialization': 'Digital Electronics, Control Systems', 'max_hours_per_week': 19},
    ]
    
    for faculty_info in faculty_data:
        if not Faculty.query.filter_by(email=faculty_info['email']).first():
            faculty = Faculty(**faculty_info)
            db.session.add(faculty)
    
    # Sample Batches
    batches_data = [
        {'name': 'CS-2022-A', 'department': 'Computer Science', 'semester': 3, 'academic_year': '2024-25', 'shift': 'morning'},
        {'name': 'CS-2021-A', 'department': 'Computer Science', 'semester': 5, 'academic_year': '2023-24', 'shift': 'morning'},
        {'name': 'CS-2020-A', 'department': 'Computer Science', 'semester': 7, 'academic_year': '2022-23', 'shift': 'afternoon'},
        {'name': 'EE-2022-A', 'department': 'Electrical Engineering', 'semester': 3, 'academic_year': '2024-25', 'shift': 'morning'},
        {'name': 'EE-2021-A', 'department': 'Electrical Engineering', 'semester': 5, 'academic_year': '2023-24', 'shift': 'afternoon'},
        {'name': 'EE-2020-A', 'department': 'Electrical Engineering', 'semester': 7, 'academic_year': '2022-23', 'shift': 'evening'},
    ]
    
    # Clear existing batches first to avoid column mismatch
    db.session.query(Batch).delete()
    db.session.commit()
    
    for batch_data in batches_data:
        batch = Batch(**batch_data)
        db.session.add(batch)
    
    db.session.commit()
    print("Sample batches created successfully!")
    
    # Commit all data
    db.session.commit()
    print("Sample data created successfully!")
    
    # Create Faculty-Subject mappings
    print("Creating faculty-subject mappings...")
    
    # Get subjects and faculty for mapping
    cs_subjects = Subject.query.filter_by(department='Computer Science').all()
    ee_subjects = Subject.query.filter_by(department='Electrical Engineering').all()
    cs_faculty = Faculty.query.filter_by(department='Computer Science').all()
    ee_faculty = Faculty.query.filter_by(department='Electrical Engineering').all()
    
    # Map CS faculty to CS subjects
    for faculty in cs_faculty:
        for subject in cs_subjects:
            if not FacultySubject.query.filter_by(faculty_id=faculty.id, subject_id=subject.id).first():
                mapping = FacultySubject(faculty_id=faculty.id, subject_id=subject.id)
                db.session.add(mapping)
    
    # Map EE faculty to EE subjects
    for faculty in ee_faculty:
        for subject in ee_subjects:
            if not FacultySubject.query.filter_by(faculty_id=faculty.id, subject_id=subject.id).first():
                mapping = FacultySubject(faculty_id=faculty.id, subject_id=subject.id)
                db.session.add(mapping)
    
    db.session.commit()
    print("Faculty-subject mappings created successfully!")

def setup_database():
    """Setup database with tables and sample data"""
    print("Setting up database...")
    
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Create admin user if not exists
        admin_user = User(
            username='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin/admin123")
        
        # Create sample data
        create_sample_data()
            
        print("\n" + "="*50)
        print("DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("Login credentials: admin/admin123")
        print("Database URL:", app.config['SQLALCHEMY_DATABASE_URI'])
        print("="*50)

if __name__ == '__main__':
    try:
        setup_database()
    except Exception as e:
        print(f"Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

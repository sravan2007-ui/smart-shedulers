#!/usr/bin/env python3
"""
MySQL Database Initialization Script for Smart Classroom Scheduler
This script creates the MySQL database and initializes it with tables and sample data.
"""

import pymysql
import os
from dotenv import load_dotenv
from app import app, db, init_db
from models import User, Classroom, Subject, Faculty, Batch, FacultySubject

# Load environment variables
load_dotenv()

def create_mysql_database():
    """Create the MySQL database if it doesn't exist"""
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_port = int(os.getenv('MYSQL_PORT', '3306'))
    mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{mysql_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{mysql_database}' created or already exists")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def initialize_tables_and_data():
    """Initialize database tables and insert sample data"""
    try:
        with app.app_context():
            # Drop all tables and recreate them
            print("Dropping existing tables...")
            db.drop_all()
            
            print("Creating database tables...")
            db.create_all()
            
            # Create default admin user
            print("Creating admin user...")
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', role='admin')
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created (username: admin, password: admin123)")
            
            # Insert sample data
            print("Inserting sample data...")
            insert_sample_data()
            
            print("Database initialization completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Sample Classrooms
        classrooms = [
            {'name': 'Room 101', 'capacity': 60, 'type': 'Lecture Hall', 'equipment': 'Projector, Whiteboard, AC'},
            {'name': 'Room 102', 'capacity': 40, 'type': 'Classroom', 'equipment': 'Projector, Whiteboard'},
            {'name': 'Lab 201', 'capacity': 30, 'type': 'Computer Lab', 'equipment': 'Computers, Projector'},
            {'name': 'Room 203', 'capacity': 50, 'type': 'Classroom', 'equipment': 'Whiteboard, AC'}
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
        print("Sample data inserted successfully!")
        
    except Exception as e:
        db.session.rollback()
        raise e

def main():
    """Main function to initialize MySQL database"""
    print("Starting MySQL Database Initialization...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_mysql_database():
        print("Failed to create database. Please check your MySQL connection.")
        return False
    
    # Step 2: Initialize tables and data
    if not initialize_tables_and_data():
        print("Failed to initialize database tables and data.")
        return False
    
    print("=" * 50)
    print("MySQL Database setup completed successfully!")
    print("\nSummary:")
    print("- Database: smart_classroom_scheduler")
    print("- Admin Login: admin / admin123")
    print("- Sample data: 4 classrooms, 4 subjects, 4 faculty, 4 batches")
    print("- Faculty-Subject mappings: 7 associations")
    print("\nYou can now start the application with: python app.py")
    
    return True

if __name__ == '__main__':
    main()

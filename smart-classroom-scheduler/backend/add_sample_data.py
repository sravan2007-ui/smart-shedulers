#!/usr/bin/env python3
"""
Script to add sample data for timetable generation testing
"""
import sqlite3
import os

# Connect to the database
db_path = 'instance/scheduler.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add sample classrooms
    classrooms = [
        ('Room 101', 60, 'Lecture Hall', 1, 1, 'Projector, Sound System'),
        ('Room 102', 40, 'Classroom', 1, 1, 'Whiteboard'),
        ('Lab 201', 30, 'Computer Lab', 1, 0, '30 Computers, Projector'),
        ('Room 203', 50, 'Classroom', 0, 1, 'Whiteboard')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO classrooms (name, capacity, type, has_projector, has_whiteboard, equipment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', classrooms)
    
    # Add sample subjects
    subjects = [
        ('Data Structures', 'CS201', 4, 'Computer Science', 3, 4, 1),
        ('Database Management', 'CS301', 3, 'Computer Science', 5, 3, 1),
        ('Mathematics III', 'MA301', 4, 'Mathematics', 3, 4, 0),
        ('Software Engineering', 'CS401', 3, 'Computer Science', 7, 3, 0),
        ('Operating Systems', 'CS302', 4, 'Computer Science', 5, 4, 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO subjects (name, code, credits, department, semester, hours_per_week, requires_lab)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', subjects)
    
    # Add sample faculty
    faculty = [
        ('Dr. John Smith', 'john.smith@university.edu', 'Computer Science', 'Data Structures, Algorithms', 6, 20, 2),
        ('Prof. Sarah Johnson', 'sarah.johnson@university.edu', 'Computer Science', 'Database Systems', 5, 18, 1),
        ('Dr. Michael Brown', 'michael.brown@university.edu', 'Mathematics', 'Applied Mathematics', 6, 22, 2),
        ('Dr. Emily Davis', 'emily.davis@university.edu', 'Computer Science', 'Software Engineering', 5, 16, 3),
        ('Prof. Robert Wilson', 'robert.wilson@university.edu', 'Computer Science', 'Operating Systems', 6, 20, 2)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO faculty (name, email, department, specialization, max_hours_per_day, max_hours_per_week, avg_leaves_per_month)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', faculty)
    
    # Add sample batches
    batches = [
        ('CS-A-2023', 'Computer Science', 3, '2023-24', 45, 'Morning'),
        ('CS-B-2023', 'Computer Science', 3, '2023-24', 42, 'Morning'),
        ('CS-A-2022', 'Computer Science', 5, '2022-23', 38, 'Afternoon'),
        ('CS-A-2021', 'Computer Science', 7, '2021-22', 35, 'Morning')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO batches (name, department, semester, academic_year, student_count, shift)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', batches)
    
    # Get IDs for faculty-subject mappings
    cursor.execute("SELECT id, email FROM faculty")
    faculty_map = {email: id for id, email in cursor.fetchall()}
    
    cursor.execute("SELECT id, code FROM subjects")
    subject_map = {code: id for id, code in cursor.fetchall()}
    
    # Add faculty-subject associations
    faculty_subjects = [
        (faculty_map.get('john.smith@university.edu'), subject_map.get('CS201')),
        (faculty_map.get('john.smith@university.edu'), subject_map.get('CS301')),
        (faculty_map.get('sarah.johnson@university.edu'), subject_map.get('CS301')),
        (faculty_map.get('sarah.johnson@university.edu'), subject_map.get('CS302')),
        (faculty_map.get('michael.brown@university.edu'), subject_map.get('MA301')),
        (faculty_map.get('emily.davis@university.edu'), subject_map.get('CS401')),
        (faculty_map.get('robert.wilson@university.edu'), subject_map.get('CS302'))
    ]
    
    for faculty_id, subject_id in faculty_subjects:
        if faculty_id and subject_id:
            cursor.execute('''
                INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id)
                VALUES (?, ?)
            ''', (faculty_id, subject_id))
    
    conn.commit()
    print("Sample data added successfully!")
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM classrooms")
    print(f"Classrooms: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM subjects")
    print(f"Subjects: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM faculty")
    print(f"Faculty: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM batches")
    print(f"Batches: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM faculty_subjects")
    print(f"Faculty-Subject mappings: {cursor.fetchone()[0]}")

except Exception as e:
    print(f"Error adding sample data: {e}")
    conn.rollback()

finally:
    conn.close()

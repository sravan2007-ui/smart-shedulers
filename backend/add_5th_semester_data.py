#!/usr/bin/env python3
"""
Script to add comprehensive sample data for 5th semester and other missing semesters
"""
from app import app, db
from models import Subject, Faculty, Batch, FacultySubject, Classroom
from datetime import datetime

def add_comprehensive_sample_data():
    with app.app_context():
        try:
            # Add more subjects for different semesters
            subjects_data = [
                # 5th Semester Computer Science
                ('Computer Networks', 'CS501', 4, 'Computer Science', 5, 4, False),
                ('Software Engineering', 'CS502', 3, 'Computer Science', 5, 3, False),
                ('Database Management Systems', 'CS503', 4, 'Computer Science', 5, 3, True),
                ('Operating Systems', 'CS504', 4, 'Computer Science', 5, 4, True),
                ('Theory of Computation', 'CS505', 3, 'Computer Science', 5, 3, False),
                ('Web Technologies', 'CS506', 3, 'Computer Science', 5, 2, True),
                
                # 3rd Semester Computer Science
                ('Data Structures', 'CS301', 4, 'Computer Science', 3, 4, True),
                ('Digital Logic Design', 'CS302', 3, 'Computer Science', 3, 3, True),
                ('Computer Organization', 'CS303', 4, 'Computer Science', 3, 4, False),
                ('Discrete Mathematics', 'CS304', 3, 'Computer Science', 3, 3, False),
                
                # 7th Semester Computer Science
                ('Machine Learning', 'CS701', 4, 'Computer Science', 7, 3, True),
                ('Compiler Design', 'CS702', 4, 'Computer Science', 7, 4, True),
                ('Computer Graphics', 'CS703', 3, 'Computer Science', 7, 2, True),
                ('Network Security', 'CS704', 3, 'Computer Science', 7, 3, False),
                
                # Electronics subjects
                ('Analog Electronics', 'EC301', 4, 'Electronics', 3, 4, True),
                ('Digital Signal Processing', 'EC501', 4, 'Electronics', 5, 4, True),
                ('Microprocessors', 'EC502', 4, 'Electronics', 5, 3, True),
                ('Communication Systems', 'EC503', 3, 'Electronics', 5, 3, False),
                
                # Mathematics subjects
                ('Linear Algebra', 'MA301', 4, 'Mathematics', 3, 4, False),
                ('Calculus III', 'MA501', 4, 'Mathematics', 5, 4, False),
                ('Probability and Statistics', 'MA502', 3, 'Mathematics', 5, 3, False),
                
                # Physics subjects
                ('Quantum Physics', 'PH301', 4, 'Physics', 3, 4, True),
                ('Thermodynamics', 'PH501', 4, 'Physics', 5, 4, True),
                
                # Chemistry subjects
                ('Organic Chemistry', 'CH301', 4, 'Chemistry', 3, 3, True),
                ('Physical Chemistry', 'CH501', 4, 'Chemistry', 5, 4, True),
            ]
            
            print("Adding subjects...")
            for name, code, credits, dept, sem, hours, lab in subjects_data:
                existing = Subject.query.filter_by(code=code).first()
                if not existing:
                    subject = Subject(
                        name=name,
                        code=code,
                        credits=credits,
                        department=dept,
                        semester=sem,
                        hours_per_week=hours,
                        requires_lab=lab,
                        scheduling_preference='single',
                        continuous_block_size=2
                    )
                    db.session.add(subject)
                    print(f"Added subject: {name} ({code})")
                else:
                    print(f"Subject {code} already exists")
            
            # Add more faculty
            faculty_data = [
                ('Dr. Alice Cooper', 'alice.cooper@college.edu', 'Computer Science', 'Networks, Security', 6, 20, 2),
                ('Prof. Bob Martin', 'bob.martin@college.edu', 'Computer Science', 'Software Engineering', 6, 18, 1),
                ('Dr. Carol White', 'carol.white@college.edu', 'Computer Science', 'Database Systems', 5, 20, 2),
                ('Prof. David Brown', 'david.brown@college.edu', 'Computer Science', 'Operating Systems', 6, 22, 1),
                ('Dr. Eva Green', 'eva.green@college.edu', 'Computer Science', 'Machine Learning', 5, 18, 2),
                ('Prof. Frank Miller', 'frank.miller@college.edu', 'Electronics', 'Analog Circuits', 6, 20, 2),
                ('Dr. Grace Lee', 'grace.lee@college.edu', 'Electronics', 'Digital Systems', 5, 18, 1),
                ('Prof. Henry Davis', 'henry.davis@college.edu', 'Mathematics', 'Applied Math', 6, 22, 2),
                ('Dr. Ivy Wilson', 'ivy.wilson@college.edu', 'Physics', 'Quantum Physics', 5, 20, 1),
                ('Prof. Jack Taylor', 'jack.taylor@college.edu', 'Chemistry', 'Organic Chemistry', 6, 18, 2),
            ]
            
            print("Adding faculty...")
            for name, email, dept, spec, max_day, max_week, leaves in faculty_data:
                existing = Faculty.query.filter_by(email=email).first()
                if not existing:
                    faculty = Faculty(
                        name=name,
                        email=email,
                        department=dept,
                        specialization=spec,
                        max_hours_per_day=max_day,
                        max_hours_per_week=max_week,
                        avg_leaves_per_month=leaves
                    )
                    db.session.add(faculty)
                    print(f"Added faculty: {name}")
                else:
                    print(f"Faculty {email} already exists")
            
            # Add more batches
            batch_data = [
                ('CS-5A-2024', 'Computer Science', 'CSE', 'A', 5, '2024-25', 45, 'morning', 1),
                ('CS-5B-2024', 'Computer Science', 'CSE', 'B', 5, '2024-25', 42, 'morning', 1),
                ('CS-3A-2024', 'Computer Science', 'CSE', 'A', 3, '2024-25', 48, 'morning', 1),
                ('CS-7A-2024', 'Computer Science', 'CSE', 'A', 7, '2024-25', 38, 'morning', 1),
                ('EC-5A-2024', 'Electronics', 'ECE', 'A', 5, '2024-25', 40, 'morning', 1),
                ('EC-3A-2024', 'Electronics', 'ECE', 'A', 3, '2024-25', 45, 'morning', 1),
            ]
            
            print("Adding batches...")
            for name, dept, branch, section, sem, year, count, shift, priority in batch_data:
                existing = Batch.query.filter_by(name=name).first()
                if not existing:
                    batch = Batch(
                        name=name,
                        department=dept,
                        branch=branch,
                        section=section,
                        semester=sem,
                        academic_year=year,
                        student_count=count,
                        shift=shift,
                        priority_for_allocation=priority
                    )
                    db.session.add(batch)
                    print(f"Added batch: {name}")
                else:
                    print(f"Batch {name} already exists")
            
            # Add more classrooms
            classroom_data = [
                ('Room 301', 50, 'regular', 'Projector, Whiteboard, AC', False, None, 1, True),
                ('Room 302', 45, 'regular', 'Projector, Whiteboard', False, None, 2, True),
                ('Lab 303', 30, 'lab', '30 Computers, Projector, AC', False, None, 1, True),
                ('Lab 304', 25, 'lab', '25 Computers, Projector', False, None, 2, True),
                ('Room 401', 60, 'regular', 'Smart Board, Projector, AC', False, None, 1, True),
                ('Auditorium', 200, 'auditorium', 'Sound System, Projector, AC', False, None, 1, False),
            ]
            
            print("Adding classrooms...")
            for name, capacity, room_type, equipment, is_fixed, fixed_batch_id, priority, can_share in classroom_data:
                existing = Classroom.query.filter_by(name=name).first()
                if not existing:
                    classroom = Classroom(
                        name=name,
                        capacity=capacity,
                        type=room_type,
                        equipment=equipment,
                        is_fixed_allocation=is_fixed,
                        fixed_batch_id=fixed_batch_id,
                        priority_level=priority,
                        can_be_shared=can_share
                    )
                    db.session.add(classroom)
                    print(f"Added classroom: {name}")
                else:
                    print(f"Classroom {name} already exists")
            
            # Commit all the basic data first
            db.session.commit()
            print("Basic data committed successfully!")
            
            # Now add faculty-subject mappings
            print("Adding faculty-subject mappings...")
            
            # Get all subjects and faculty for mapping
            subjects = Subject.query.all()
            faculty_members = Faculty.query.all()
            
            # Create mappings based on department and specialization
            mappings = []
            
            for faculty in faculty_members:
                for subject in subjects:
                    if faculty.department == subject.department:
                        # Check if specialization matches or is general
                        specialization = faculty.specialization or ''
                        if (subject.name.lower() in specialization.lower() or 
                            any(keyword in specialization.lower() 
                                for keyword in ['general', 'all', subject.department.lower()]) or
                            faculty.department == subject.department):
                            
                            # Check if mapping already exists
                            existing_mapping = FacultySubject.query.filter_by(
                                faculty_id=faculty.id,
                                subject_id=subject.id
                            ).first()
                            
                            if not existing_mapping:
                                mapping = FacultySubject(
                                    faculty_id=faculty.id,
                                    subject_id=subject.id,
                                    department=subject.department,
                                    semester=subject.semester,
                                    is_primary=True,
                                    priority=1
                                )
                                mappings.append(mapping)
                                print(f"Mapped {faculty.name} -> {subject.name}")
            
            # Add all mappings
            for mapping in mappings:
                db.session.add(mapping)
            
            db.session.commit()
            print("Faculty-subject mappings added successfully!")
            
            # Print summary
            print("\n=== DATA SUMMARY ===")
            print(f"Total Subjects: {Subject.query.count()}")
            print(f"Total Faculty: {Faculty.query.count()}")
            print(f"Total Batches: {Batch.query.count()}")
            print(f"Total Classrooms: {Classroom.query.count()}")
            print(f"Total Faculty-Subject Mappings: {FacultySubject.query.count()}")
            
            # Print subjects by semester
            for sem in range(1, 9):
                count = Subject.query.filter_by(semester=sem).count()
                print(f"Semester {sem} subjects: {count}")
            
            print("\nSample data added successfully!")
            
        except Exception as e:
            print(f"Error adding sample data: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_comprehensive_sample_data()

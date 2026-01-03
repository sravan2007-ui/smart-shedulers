from app import app, db
from models import Subject, Faculty, Batch, FacultySubject, Classroom

def seed_data():
    with app.app_context():
        print("Starting data seeding...")

        # --- 1. Subjects ---
        subjects_data = [
            {"name": "Optimization Techniques", "code": "OT", "credits": 2, "hours": 3},
            {"name": "Probability & Statistics", "code": "PS", "credits": 3, "hours": 3},
            {"name": "Machine Learning", "code": "ML", "credits": 3, "hours": 3},
            {"name": "Adv Data Structures & Algorithms", "code": "ADSAA", "credits": 3, "hours": 3},
            {"name": "Digital Logic & Comp Org", "code": "DLCO", "credits": 3, "hours": 3},
            {"name": "Design Thinking & Innovation", "code": "DTI", "credits": 2, "hours": 2},
            {"name": "Environmental Science", "code": "ES", "credits": 0, "hours": 2},
            {"name": "AIML Lab", "code": "AIML LAB", "credits": 1.5, "hours": 3, "requires_lab": True},
            {"name": "ADSAA Lab", "code": "ADSAA LAB", "credits": 1.5, "hours": 3, "requires_lab": True},
            {"name": "Full Stack Dev-I Lab", "code": "FSD-I LAB", "credits": 2, "hours": 3, "requires_lab": True},
        ]

        subjects = {}
        for s_data in subjects_data:
            subject = Subject.query.filter_by(code=s_data['code']).first()
            if not subject:
                subject = Subject(
                    name=s_data['name'],
                    code=s_data['code'],
                    credits=s_data['credits'],
                    hours_per_week=s_data['hours'],
                    requires_lab=s_data.get('requires_lab', False),
                    department="CSE" # Assuming CSE department for all
                )
                db.session.add(subject)
                print(f"Added Subject: {subject.name}")
            else:
                 print(f"Subject exists: {subject.name}")
            subjects[s_data['code']] = subject
        
        db.session.commit() # Commit subjects first to get IDs if needed

        # --- 2. Batches ---
        batches_data = [
            {"name": "II B.Tech AIML Sec-A", "sec": "A"},
            {"name": "II B.Tech AIML Sec-B", "sec": "B"},
            {"name": "II B.Tech AIML Sec-C", "sec": "C"},
        ]
        
        batches = {}
        for b_data in batches_data:
            batch = Batch.query.filter_by(name=b_data['name']).first()
            if not batch:
                batch = Batch(
                    name=b_data['name'],
                    department="CSE",
                    branch="AIML",
                    section=b_data['sec'],
                    semester=4, # 2nd Sem of 2nd Year = 4th Sem usually, or user said "2nd Semester" implying Year 1? 
                                # Image says "II B.Tech AIML: 2025-26 2nd Semester". Usually means 2-2 (4th sem).
                    academic_year="2025-26"
                )
                db.session.add(batch)
                print(f"Added Batch: {batch.name}")
            else:
                print(f"Batch exists: {batch.name}")
            batches[b_data['sec']] = batch
        
        db.session.commit()

        # --- 3. Faculty & Mappings ---
        # Format: "Name": [("SubjectCode", "Section")]
        faculty_allocations = {
            # Section A
            "Dr. K Suresh Babu": [("OT", "A")],
            "Dr. N U B Varma": [("PS", "A")],
            "Smt. D Hema Latha": [("ML", "A"), ("AIML LAB", "A")], # Lab too
            "Dr. P Bharat Siva Varma": [("ADSAA", "A"), ("ADSAA LAB", "A")],
            "Smt. P Neelima": [("DLCO", "A")],
            "Smt. V Anjani Kranti": [("DTI", "A")],
            "Sri J Jeevan Kumar": [("ES", "A"), ("ES", "C")], # Also for C
            "Dr. B N V Narasimha Raju": [("AIML LAB", "A")],
            "Smt. P Saroja": [("ADSAA LAB", "A"), ("FSD-I LAB", "A")],
            "Smt. D Sravani": [("ADSAA LAB", "A")],
            "Smt. K Raja Rajeswari": [("FSD-I LAB", "A")],
            "Miss. L Padma": [("FSD-I LAB", "A")],

            # Section B
            "Dr. Ch Rama Bhadri Raju": [("OT", "B")],
            "Dr. G Santhi": [("PS", "B")],
            "Dr. G N V G Sirisha": [("ML", "B"), ("AIML LAB", "B")],
            "Smt. K Durga Bhavani": [("ADSAA", "B"), ("ADSAA LAB", "B")],
            "Smt. A Neelima": [("DLCO", "B")],
            "Smt. P Jahnavi": [("AIML LAB", "B"), ("AIML LAB", "C")],
            "Dr. G Mahesh": [("ADSAA LAB", "B")],
            "Dr. K D V Pavan Kumar Varma": [("FSD-I LAB", "B")],
            "Miss K V Rishitha": [("FSD-I LAB", "B")],
            "Smt. S Ravali": [("FSD-I LAB", "B"), ("ADSAA LAB", "C")],
            "Miss. Ch Suma": [("DTI", "B")], # Deduced from table rows

            # Section C
            "Sri. Ch Gopala Raju": [("OT", "C")],
            "Dr. G Vidyasagar": [("PS", "C")],
            "Smt. A L Lavanya": [("ML", "C"), ("AIML LAB", "C")],
            "Smt. M Jeevana Sujitha": [("ADSAA", "C"), ("ADSAA LAB", "C")],
            "Dr. K Ramaprasada Raju": [("DLCO", "C")],
            "Smt. P Sandhya": [("DTI", "C")],
            "Smt. B Rekha Madhavi": [("DTI", "C")],
            "Sri. T Srinivasa Rao": [("FSD-I LAB", "C")],
            "Smt. M Prasanna Kumari": [("FSD-I LAB", "C")],
            "Smt. N Soudhamini": [("FSD-I LAB", "C")],
        }

        # Helper to get subject object
        def get_subject_id(code):
            return subjects[code].id if code in subjects else None

        for f_name, allocations in faculty_allocations.items():
            faculty = Faculty.query.filter_by(name=f_name).first()
            if not faculty:
                faculty = Faculty(name=f_name, department="CSE")
                db.session.add(faculty)
                db.session.flush() # Get ID
                print(f"Added Faculty: {faculty.name}")
            else:
                 print(f"Faculty exists: {faculty.name}")

            # Add FacultySubject mappings
            for sub_code, sec in allocations:
                sub_id = get_subject_id(sub_code)
                if sub_id:
                    # Check if mapping exists
                    mapping = FacultySubject.query.filter_by(
                        faculty_id=faculty.id, 
                        subject_id=sub_id, 
                        branch='AIML', 
                        department='CSE'
                        # Note: we aren't filtering by section/batch in FacultySubject model directly in this loop 
                        # because the model uses simple fields. 
                        # Ideally, we should add a specific section if the model supported it, 
                        # but typically FacultySubject is "Can Teach".
                        # Here I'll just ensure they are mapped as "Primary"
                    ).first()
                    
                    if not mapping:
                        mapping = FacultySubject(
                            faculty_id=faculty.id,
                            subject_id=sub_id,
                            department="CSE",
                            branch="AIML",
                            is_primary=True
                        )
                        db.session.add(mapping)
                        print(f"  -> Mapped to {sub_code}")

        db.session.commit()
        print("Data seeding completed successfully!")

if __name__ == "__main__":
    seed_data()

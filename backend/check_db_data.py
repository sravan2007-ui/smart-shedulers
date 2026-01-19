from app import app
from models import db, User, Faculty, Subject, Classroom, Batch, Timetable

def check_data():
    with app.app_context():
        print("\n--- DATABASE CONTENTS (PostgreSQL) ---\n")
        
        # 1. Users
        users = User.query.all()
        print(f"Users ({len(users)}):")
        for u in users:
            print(f" - {u.username} ({u.role})")
        
        print("-" * 30)

        # 2. Faculty
        faculty = Faculty.query.all()
        print(f"Faculty ({len(faculty)}):")
        for f in faculty:
            print(f" - {f.name} ({f.department})")
            
        print("-" * 30)
            
        # 3. Subjects
        subjects = Subject.query.all()
        print(f"Subjects ({len(subjects)}):")
        for s in subjects:
            print(f" - {s.name} ({s.code})")

        print("-" * 30)

        # 4. Batches
        batches = Batch.query.all()
        print(f"Batches ({len(batches)}):")
        for b in batches:
            print(f" - {b.name} ({b.department})")

        print("-" * 30)

        # 5. Classrooms
        classrooms = Classroom.query.all()
        print(f"Classrooms ({len(classrooms)}):")
        for c in classrooms:
            print(f" - {c.name} (Cap: {c.capacity})")
            
if __name__ == "__main__":
    check_data()

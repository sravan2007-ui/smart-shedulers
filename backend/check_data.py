from app import app
from models import Batch, Subject

with app.app_context():
    print("=== BATCHES ===")
    batches = Batch.query.all()
    for b in batches:
        print(f'Batch {b.id}: {b.name}, Department: {b.department}, Students: {b.student_count}')
    
    print("\n=== SUBJECTS ===")
    subjects = Subject.query.all()
    for s in subjects:
        print(f'Subject {s.id}: {s.name}, Department: {s.department}, Semester: {s.semester}, Hours: {s.hours_per_week}')

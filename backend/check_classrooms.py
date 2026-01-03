from app import app
from models import Classroom, Batch

with app.app_context():
    print("=== CLASSROOMS ===")
    classrooms = Classroom.query.all()
    for c in classrooms:
        print(f'Classroom {c.id}: {c.name}, Capacity: {c.capacity}, Type: {c.type}')
    
    print("\n=== BATCH CAPACITY CHECK ===")
    batch = Batch.query.get(1)
    if batch:
        print(f'Batch 1 has {batch.student_count} students')
        suitable_classrooms = Classroom.query.filter(Classroom.capacity >= batch.student_count).all()
        print(f'Suitable classrooms: {len(suitable_classrooms)}')
        for c in suitable_classrooms:
            print(f'  - {c.name}: capacity {c.capacity}')
    else:
        print('Batch 1 not found')

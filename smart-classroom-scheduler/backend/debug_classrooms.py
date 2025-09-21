from app import app
from timetable_optimizer import TimetableOptimizer

with app.app_context():
    try:
        opt = TimetableOptimizer()
        
        # Test classroom availability for Data Structures (subject ID 1)
        print("Testing classroom availability...")
        classrooms = opt.get_available_classrooms(1, False)  # batch_id=1, requires_lab=False
        print(f'Available classrooms for batch 1: {len(classrooms)}')
        for c in classrooms:
            print(f'  - {c["name"]}: capacity {c["capacity"]}, type {c["type"]}')
        
        # Test with lab requirement
        lab_classrooms = opt.get_available_classrooms(1, True)  # requires_lab=True
        print(f'\nAvailable lab classrooms for batch 1: {len(lab_classrooms)}')
        for c in lab_classrooms:
            print(f'  - {c["name"]}: capacity {c["capacity"]}, type {c["type"]}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

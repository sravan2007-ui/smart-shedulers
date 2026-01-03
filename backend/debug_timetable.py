from app import app
from timetable_optimizer import TimetableOptimizer

with app.app_context():
    try:
        opt = TimetableOptimizer()
        subjects = opt.get_batch_subjects(1, 3)  # Use semester 3 where subjects exist
        print(f'Subjects found: {len(subjects)}')
        
        for s in subjects:
            print(f'- {s["name"]}: {s["hours_per_week"]}h, pref: {s["scheduling_preference"]}')
            blocks = opt.calculate_subject_blocks(s)
            print(f'  Blocks: {blocks}')
        
        if subjects:
            print('\nTesting timetable generation...')
            schedule = opt.generate_single_timetable(1, 3)
            print(f'Generated schedule with {len(schedule)} entries')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

from app import app
from models import Timetable, TimetableEntry, Subject, Faculty, Classroom
import json

with app.app_context():
    # Get a timetable and debug its PDF generation
    timetable = Timetable.query.first()
    if timetable:
        print(f"=== TIMETABLE: {timetable.name} ===")
        print(f"ID: {timetable.id}")
        print(f"Timing Config: {timetable.timing_config}")
        
        entries = TimetableEntry.query.filter_by(timetable_id=timetable.id).all()
        print(f"\n=== ENTRIES ({len(entries)}) ===")
        
        # Parse timing config
        timing_config = json.loads(timetable.timing_config) if timetable.timing_config else {}
        print(f"Parsed timing config: {timing_config}")
        
        # Show all entries with details
        for entry in entries:
            subject = Subject.query.get(entry.subject_id)
            faculty = Faculty.query.get(entry.faculty_id)
            classroom = Classroom.query.get(entry.classroom_id)
            
            print(f"  Day {entry.day_of_week} ({['Mon','Tue','Wed','Thu','Fri','Sat'][entry.day_of_week]})")
            print(f"    Time: {entry.time_slot}")
            print(f"    Subject: {subject.name if subject else 'N/A'}")
            print(f"    Faculty: {faculty.name if faculty else 'N/A'}")
            print(f"    Classroom: {classroom.name if classroom else 'N/A'}")
            print()
        
        # Show what time slots would be generated
        time_slots = set()
        for entry in entries:
            time_slots.add(entry.time_slot)
        
        lunch_start = timing_config.get('lunch_break_start_time', '12:15')
        lunch_slot = f"{lunch_start}-{timing_config.get('lunch_break_end_time', '13:15')}"
        time_slots.add(lunch_slot)
        
        time_slots = sorted(list(time_slots), key=lambda x: x.split('-')[0])
        print(f"=== TIME SLOTS FOR PDF ({len(time_slots)}) ===")
        for slot in time_slots:
            print(f"  {slot}")
            
    else:
        print("No timetables found")

from app import app
from models import Timetable, TimetableEntry

with app.app_context():
    # Get a timetable and its entries
    timetable = Timetable.query.first()
    if timetable:
        print(f"Timetable: {timetable.name} (ID: {timetable.id})")
        entries = TimetableEntry.query.filter_by(timetable_id=timetable.id).all()
        print(f"Entries found: {len(entries)}")
        
        for entry in entries:
            print(f"  Day {entry.day_of_week}, Time: {entry.time_slot}, Subject: {entry.subject_id}, Faculty: {entry.faculty_id}, Classroom: {entry.classroom_id}")
    else:
        print("No timetables found")

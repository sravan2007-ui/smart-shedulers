from app import app
from models import Timetable, TimetableEntry, Subject, Faculty, Classroom, Batch
import json

with app.app_context():
    # Test what's actually being generated in the PDF
    timetable = Timetable.query.first()
    if timetable:
        print(f"=== TESTING PDF DATA FOR: {timetable.name} ===")
        
        entries = TimetableEntry.query.filter_by(timetable_id=timetable.id).all()
        batch = Batch.query.get(timetable.batch_id)
        timing_config = json.loads(timetable.timing_config) if timetable.timing_config else {}
        
        print(f"Batch: {batch.name if batch else 'N/A'}")
        print(f"Entries: {len(entries)}")
        
        # Test timetable data structure creation
        timetable_data = {}
        for entry in entries:
            day_idx = entry.day_of_week
            time_slot = entry.time_slot
            
            if day_idx not in timetable_data:
                timetable_data[day_idx] = {}
            
            # Get subject, faculty, and classroom info
            subject = Subject.query.get(entry.subject_id)
            faculty = Faculty.query.get(entry.faculty_id)
            classroom = Classroom.query.get(entry.classroom_id)
            
            cell_content = f"{subject.name if subject else 'N/A'}\n{faculty.name if faculty else 'N/A'}\n{classroom.name if classroom else 'N/A'}"
            timetable_data[day_idx][time_slot] = cell_content
            
            print(f"Day {day_idx}: {time_slot} -> {cell_content.replace(chr(10), ' | ')}")
        
        # Test complete time slots
        college_start = timing_config.get('college_start_time', '09:00')
        college_end = timing_config.get('college_end_time', '16:30')
        lunch_start = timing_config.get('lunch_break_start_time', '12:15')
        lunch_duration = timing_config.get('lunch_break_duration', 60)
        
        print(f"\nTiming: {college_start} to {college_end}, Lunch: {lunch_start} ({lunch_duration}min)")
        
        # Show what would be in the PDF table
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        print(f"\n=== PDF TABLE PREVIEW ===")
        
        # Generate time slots like in PDF
        def generate_complete_time_slots(start_time, end_time, lunch_start_time, lunch_duration):
            slots = []
            current_time = start_time
            end_minutes = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])
            lunch_start_minutes = int(lunch_start_time.split(':')[0]) * 60 + int(lunch_start_time.split(':')[1])
            lunch_end_minutes = lunch_start_minutes + lunch_duration
            
            while True:
                current_minutes = int(current_time.split(':')[0]) * 60 + int(current_time.split(':')[1])
                
                if current_minutes >= end_minutes:
                    break
                
                if current_minutes == lunch_start_minutes:
                    lunch_end_hour = lunch_end_minutes // 60
                    lunch_end_min = lunch_end_minutes % 60
                    lunch_end_time = f"{lunch_end_hour:02d}:{lunch_end_min:02d}"
                    slots.append(f"{lunch_start_time}-{lunch_end_time}")
                    current_time = lunch_end_time
                    continue
                
                if lunch_start_minutes <= current_minutes < lunch_end_minutes:
                    current_time = f"{lunch_end_minutes // 60:02d}:{lunch_end_minutes % 60:02d}"
                    continue
                
                slot_end_minutes = current_minutes + 45
                slot_end_hour = slot_end_minutes // 60
                slot_end_min = slot_end_minutes % 60
                slot_end_time = f"{slot_end_hour:02d}:{slot_end_min:02d}"
                
                slots.append(f"{current_time}-{slot_end_time}")
                current_time = slot_end_time
            
            return slots
        
        time_slots = generate_complete_time_slots(college_start, college_end, lunch_start, lunch_duration)
        
        # Show header
        header = "Day/Time".ljust(12) + "".join([slot.split('-')[0].ljust(12) for slot in time_slots])
        print(header)
        print("-" * len(header))
        
        # Show each day
        for day_idx, day_name in enumerate(days):
            row = day_name.ljust(12)
            for time_slot in time_slots:
                if lunch_start in time_slot:
                    cell = "LUNCH"
                else:
                    cell_content = timetable_data.get(day_idx, {}).get(time_slot, '')
                    cell = cell_content.split('\n')[0][:10] if cell_content else ''
                row += cell.ljust(12)
            print(row)
            
    else:
        print("No timetables found")

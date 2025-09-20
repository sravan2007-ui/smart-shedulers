from app import app
from models import Timetable, TimetableEntry
import json

with app.app_context():
    # Test the new complete time slot generation
    timetable = Timetable.query.first()
    if timetable:
        timing_config = json.loads(timetable.timing_config) if timetable.timing_config else {}
        
        college_start = timing_config.get('college_start_time', '09:00')
        college_end = timing_config.get('college_end_time', '16:30')
        lunch_start = timing_config.get('lunch_break_start_time', '12:15')
        lunch_duration = timing_config.get('lunch_break_duration', 60)
        
        print(f"College hours: {college_start} to {college_end}")
        print(f"Lunch: {lunch_start} for {lunch_duration} minutes")
        
        # Generate complete time slots
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
        
        print(f"\n=== COMPLETE TIME SLOTS ({len(time_slots)}) ===")
        for i, slot in enumerate(time_slots):
            print(f"{i+1:2d}. {slot}")
        
        # Show actual entries
        entries = TimetableEntry.query.filter_by(timetable_id=timetable.id).all()
        print(f"\n=== ACTUAL ENTRIES ({len(entries)}) ===")
        for entry in entries:
            print(f"Day {entry.day_of_week}: {entry.time_slot}")
            
    else:
        print("No timetables found")

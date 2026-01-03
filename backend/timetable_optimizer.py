from models import db, Subject, Faculty, Classroom, Batch, FacultySubject
from classroom_allocator import SmartClassroomAllocator
import random
from datetime import datetime, timedelta
from collections import defaultdict
import itertools

class TimetableOptimizer:
    def __init__(self, include_short_break=False, short_break_duration=10, college_start_time='09:00', college_end_time='16:30', lunch_break_duration=60, lunch_break_start_time='12:15'):
        # Generate dynamic time slots based on college timing
        self.college_start_time = college_start_time
        self.college_end_time = college_end_time
        self.lunch_break_duration = lunch_break_duration
        self.lunch_break_start_time = lunch_break_start_time
        self.time_slots = self.generate_time_slots(college_start_time, college_end_time, lunch_break_duration, lunch_break_start_time)
        
        # Configure break slots based on parameters
        self.break_slots = {}
        
        # Use specified lunch break start time
        lunch_start_time = lunch_break_start_time
        lunch_end_time = self.add_minutes_to_time(lunch_start_time, lunch_break_duration)
        self.break_slots[f'{lunch_start_time}-{lunch_end_time}'] = 'Lunch Break'
        
        # Optionally include short break
        if include_short_break:
            short_break_start_time = self.calculate_short_break_start_time(college_start_time)
            short_break_end_time = self.add_minutes_to_time(short_break_start_time, short_break_duration)
            self.break_slots[f'{short_break_start_time}-{short_break_end_time}'] = 'Short Break'
        
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.max_classes_per_day = 6
        self.include_short_break = include_short_break
        self.short_break_duration = short_break_duration
        
        # Initialize smart classroom allocator
        self.classroom_allocator = SmartClassroomAllocator()
        
    
    def calculate_subject_blocks(self, subject):
        """Calculate how many blocks a subject needs based on scheduling preference and lab requirements"""
        hours_per_week = subject.get('hours_per_week', 3)
        preference = subject.get('scheduling_preference', 'single')
        block_size = subject.get('continuous_block_size', 2)
        requires_lab = subject.get('requires_lab', False)
        
        # Special handling for lab subjects - always 3-hour blocks
        if requires_lab:
            # Lab sessions are always 3-hour continuous blocks
            # If hours_per_week is 3 or more, create 3-hour blocks
            blocks = []
            remaining = hours_per_week
            while remaining >= 3:
                blocks.append(3)  # 3-hour lab block
                remaining -= 3
            if remaining > 0:
                blocks.append(remaining)  # Any remaining hours as smaller block
            return blocks
        
        if preference == 'single':
            # All classes are single 45-minute slots (1 period)
            return [1] * hours_per_week
        elif preference == 'double':
            # 90-minute blocks (2 periods)
            blocks = []
            remaining = hours_per_week
            while remaining >= 2:
                blocks.append(2)
                remaining -= 2
            if remaining > 0:
                blocks.append(remaining)
            return blocks
        elif preference == 'triple':
            # 135-minute blocks (3 periods)
            blocks = []
            remaining = hours_per_week
            while remaining >= 3:
                blocks.append(3)
                remaining -= 3
            if remaining > 0:
                blocks.append(remaining)
            return blocks
        elif preference == 'lab':
            # 180-minute blocks (4 periods)
            blocks = []
            remaining = hours_per_week
            while remaining >= 4:
                blocks.append(4)
                remaining -= 4
            if remaining > 0:
                blocks.append(remaining)
            return blocks
        
        return [1] * hours_per_week  # Default to single classes

    def get_batch_subjects(self, batch_id, semester):
        """Get subjects for a specific batch and semester"""
        try:
            # Get batch department first
            batch = Batch.query.get(batch_id)
            if not batch:
                print(f"No batch found with id {batch_id}")
                return []
            
            print(f"Found batch department: {batch.department}")
            
            # Get subjects for the batch's department and semester
            subjects = Subject.query.filter_by(
                department=batch.department, 
                semester=semester
            ).all()
            
            print(f"Found {len(subjects)} subjects for department {batch.department}, semester {semester}")
            subjects_data = []
            for subject in subjects:
                print(f"  - {subject.name} ({subject.code})")
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'credits': subject.credits,
                    'department': subject.department,
                    'semester': subject.semester,
                    'hours_per_week': subject.hours_per_week,
                    'requires_lab': subject.requires_lab,
                    'scheduling_preference': getattr(subject, 'scheduling_preference', 'single'),
                    'continuous_block_size': getattr(subject, 'continuous_block_size', 2)
                })
            
            return subjects_data
        except Exception as e:
            print(f"Error getting batch subjects: {e}")
            return []
    
    def get_available_faculty(self, subject_id, batch_id=None):
        """Get faculty members who can teach a specific subject, prioritizing by exact match"""
        try:
            # Get the subject and batch information
            subject = Subject.query.get(subject_id)
            if not subject:
                print(f"Subject with id {subject_id} not found")
                return []
            
            batch = None
            if batch_id:
                batch = Batch.query.get(batch_id)
            
            subject_department = subject.department
            print(f"Looking for faculty for subject: {subject.name} in department: {subject_department}")
            if batch:
                print(f"For batch: {batch.name} (Branch: {batch.branch}, Semester: {batch.semester})")
            
            faculty_list = []
            
            # Priority 1: Get faculty specifically assigned to this subject for this batch/department/branch
            if batch:
                specific_assignments = FacultySubject.query.filter_by(
                    subject_id=subject_id,
                    department=batch.department,
                    branch=batch.branch,
                    semester=batch.semester
                ).order_by(FacultySubject.priority.asc(), FacultySubject.is_primary.desc()).all()
                
                if specific_assignments:
                    print(f"Found {len(specific_assignments)} specific faculty assignments for this batch")
                    for fs in specific_assignments:
                        faculty = fs.faculty
                        faculty_list.append({
                            'id': faculty.id,
                            'name': faculty.name,
                            'email': faculty.email,
                            'department': faculty.department,
                            'specialization': getattr(faculty, 'specialization', ''),
                            'max_hours_per_week': faculty.max_hours_per_week,
                            'max_hours_per_day': faculty.max_hours_per_day,
                            'is_primary': fs.is_primary,
                            'priority': fs.priority,
                            'match_type': 'exact_match'
                        })
            
            # Priority 2: Get faculty assigned to this subject for the same department
            if not faculty_list:
                dept_assignments = FacultySubject.query.filter_by(
                    subject_id=subject_id,
                    department=subject_department
                ).order_by(FacultySubject.priority.asc(), FacultySubject.is_primary.desc()).all()
                
                if dept_assignments:
                    print(f"Found {len(dept_assignments)} department-specific faculty assignments")
                    for fs in dept_assignments:
                        faculty = fs.faculty
                        faculty_list.append({
                            'id': faculty.id,
                            'name': faculty.name,
                            'email': faculty.email,
                            'department': faculty.department,
                            'specialization': getattr(faculty, 'specialization', ''),
                            'max_hours_per_week': faculty.max_hours_per_week,
                            'max_hours_per_day': faculty.max_hours_per_day,
                            'is_primary': fs.is_primary,
                            'priority': fs.priority,
                            'match_type': 'department_match'
                        })
            
            # Priority 3: Get any faculty assigned to this subject
            if not faculty_list:
                general_assignments = FacultySubject.query.filter_by(
                    subject_id=subject_id
                ).order_by(FacultySubject.priority.asc(), FacultySubject.is_primary.desc()).all()
                
                if general_assignments:
                    print(f"Found {len(general_assignments)} general faculty assignments")
                    for fs in general_assignments:
                        faculty = fs.faculty
                        faculty_list.append({
                            'id': faculty.id,
                            'name': faculty.name,
                            'email': faculty.email,
                            'department': faculty.department,
                            'specialization': getattr(faculty, 'specialization', ''),
                            'max_hours_per_week': faculty.max_hours_per_week,
                            'max_hours_per_day': faculty.max_hours_per_day,
                            'is_primary': fs.is_primary,
                            'priority': fs.priority,
                            'match_type': 'subject_match'
                        })
            
            # Priority 4: Get faculty from same department (fallback)
            if not faculty_list and subject_department:
                print(f"No faculty-subject mapping found, looking for faculty in {subject_department} department")
                department_faculty = Faculty.query.filter_by(department=subject_department).all()
                for faculty in department_faculty:
                    faculty_list.append({
                        'id': faculty.id,
                        'name': faculty.name,
                        'email': faculty.email,
                        'department': faculty.department,
                        'specialization': getattr(faculty, 'specialization', ''),
                        'max_hours_per_week': faculty.max_hours_per_week,
                        'max_hours_per_day': faculty.max_hours_per_day,
                        'is_primary': False,
                        'priority': 3,
                        'match_type': 'department_fallback'
                    })
            
            # Priority 5: Get all faculty as last resort
            if not faculty_list:
                print("No department-specific faculty found, using all faculty as fallback")
                all_faculty = Faculty.query.all()
                for faculty in all_faculty:
                    faculty_list.append({
                        'id': faculty.id,
                        'name': faculty.name,
                        'email': faculty.email,
                        'department': faculty.department,
                        'specialization': getattr(faculty, 'specialization', ''),
                        'max_hours_per_week': faculty.max_hours_per_week,
                        'max_hours_per_day': faculty.max_hours_per_day,
                        'is_primary': False,
                        'priority': 4,
                        'match_type': 'general_fallback'
                    })
            
            print(f"Found {len(faculty_list)} available faculty members for subject {subject.name}")
            return faculty_list
            
        except Exception as e:
            print(f"Error getting available faculty: {e}")
            return []
    
    def get_available_classrooms(self, batch_id, requires_lab=False, day_of_week=None, time_slot=None, subject_id=None):
        """Get available classrooms for a batch using smart allocation"""
        try:
            # Get batch info
            batch = Batch.query.get(batch_id)
            if not batch:
                print(f"No batch found with id {batch_id}")
                return []
            
            # If specific time slot is provided, use smart allocator
            if day_of_week is not None and time_slot is not None:
                available_classrooms = self.classroom_allocator.find_available_classrooms(
                    batch_id, day_of_week, time_slot, subject_id
                )
                
                classrooms_data = []
                for allocation_info in available_classrooms:
                    classroom = allocation_info['classroom']
                    classrooms_data.append({
                        'id': classroom.id,
                        'name': classroom.name,
                        'capacity': classroom.capacity,
                        'type': classroom.type,
                        'equipment': classroom.equipment,
                        'priority_score': allocation_info['priority_score'],
                        'allocation_type': allocation_info['allocation_type'],
                        'can_borrow': allocation_info.get('can_borrow', False),
                        'is_temporary': allocation_info['allocation_type'] == 'temporary_borrow'
                    })
                
                return classrooms_data
            
            # Fallback to original logic for general queries
            if requires_lab:
                classrooms = Classroom.query.filter(
                    Classroom.type == 'lab',
                    Classroom.capacity >= batch.student_count
                ).order_by(Classroom.capacity.asc()).all()
            else:
                classrooms = Classroom.query.filter(
                    Classroom.capacity >= batch.student_count
                ).order_by(Classroom.capacity.asc()).all()
            
            classrooms_data = []
            for classroom in classrooms:
                classrooms_data.append({
                    'id': classroom.id,
                    'name': classroom.name,
                    'capacity': classroom.capacity,
                    'type': classroom.type,
                    'equipment': classroom.equipment
                })
            
            return classrooms_data
        except Exception as e:
            print(f"Error getting available classrooms: {e}")
            return []
    
    def get_fixed_slots(self, batch_id):
        """Get fixed time slots that cannot be changed"""
        # For now, return empty list as we don't have fixed_slots table in the new schema
        # This can be implemented later if needed
        return []
    
    def can_schedule_block(self, day_idx, start_time_slot, faculty_id, classroom_id, existing_schedule, block_size):
        """Check if a continuous block can be scheduled"""
        if block_size == 1:
            return self.is_slot_available(day_idx, start_time_slot, faculty_id, classroom_id, existing_schedule)
        
        # Special handling for lab sessions (4-period blocks, 180 mins)
        if block_size == 4 and start_time_slot in self.get_lab_start_times():
            # For lab sessions, we need to check if 4 consecutive slots starting from start_time_slot are available
            consecutive_slots = self.get_consecutive_slots(start_time_slot, 4)
            if not consecutive_slots or len(consecutive_slots) != 4:
                return False
                
            for slot in consecutive_slots:
                if not self.is_slot_available(day_idx, slot, faculty_id, classroom_id, existing_schedule):
                    return False
            return True
        
        # Get consecutive time slots for regular blocks
        consecutive_slots = self.get_consecutive_slots(start_time_slot, block_size)
        if not consecutive_slots or len(consecutive_slots) != block_size:
            return False
        
        # Check if all slots in the block are available
        for slot in consecutive_slots:
            if not self.is_slot_available(day_idx, slot, faculty_id, classroom_id, existing_schedule):
                return False
        
        return True
    
    def get_consecutive_slots(self, start_slot, block_size):
        """Get consecutive time slots starting from start_slot"""
        try:
            start_idx = self.time_slots.index(start_slot)
        except ValueError:
            return []
        
        consecutive_slots = []
        for i in range(block_size):
            if start_idx + i >= len(self.time_slots):
                return []  # Not enough consecutive slots available
            
            slot = self.time_slots[start_idx + i]
            # Skip break slots
            if slot in self.break_slots:
                return []
            
            consecutive_slots.append(slot)
        
        return consecutive_slots

    def is_slot_available(self, day_idx, time_slot, faculty_id, classroom_id, existing_schedule):
        """Check if a time slot is available for faculty and classroom"""
        slot_key = (day_idx, time_slot)
        
        # Check faculty availability
        for entry in existing_schedule:
            if (entry['day_of_week'] == day_idx and 
                entry['time_slot'] == time_slot and 
                entry['faculty_id'] == faculty_id):
                return False
        
        # Check classroom availability
        for entry in existing_schedule:
            if (entry['day_of_week'] == day_idx and 
                entry['time_slot'] == time_slot and 
                entry['classroom_id'] == classroom_id):
                return False
        
        return True
    
    def calculate_faculty_workload(self, faculty_id, existing_schedule):
        """Calculate current workload for a faculty member"""
        daily_hours = defaultdict(int)
        total_hours = 0
        
        for entry in existing_schedule:
            if entry['faculty_id'] == faculty_id:
                daily_hours[entry['day_of_week']] += 1
                total_hours += 1
        
        return daily_hours, total_hours
    
    def assign_random_shift(self, batch_id):
        """Assign a random shift to a batch during timetable generation"""
        import random
        shifts = ['morning', 'afternoon']
        assigned_shift = random.choice(shifts)
        
        # Update the batch with the assigned shift
        try:
            from models import Batch
            batch = Batch.query.get(batch_id)
            if batch:
                batch.shift = assigned_shift
                from models import db
                db.session.commit()
                print(f"Assigned {assigned_shift} shift to batch {batch.name}")
            return assigned_shift
        except Exception as e:
            print(f"Error assigning shift: {e}")
            return 'morning'  # Default fallback
    
    def generate_single_timetable(self, batch_id, semester):
        """Generate a single optimized timetable"""
        print(f"Starting timetable generation for batch {batch_id}, semester {semester}")
        
        # Assign random shift to batch
        assigned_shift = self.assign_random_shift(batch_id)
        print(f"Batch assigned to {assigned_shift} shift")
        
        subjects = self.get_batch_subjects(batch_id, semester)
        print(f"Found {len(subjects)} subjects for this batch/semester")
        
        if not subjects:
            print("No subjects found for this batch/semester combination")
            return []
        
        fixed_slots = self.get_fixed_slots(batch_id)
        print(f"Found {len(fixed_slots)} fixed slots")
        
        schedule = []
        
        # Add fixed slots first
        for slot in fixed_slots:
            if slot['batch_id'] == batch_id or slot['batch_id'] is None:
                if slot['subject_id'] and slot['faculty_id'] and slot['classroom_id']:
                    schedule.append({
                        'day_of_week': slot['day_of_week'],
                        'time_slot': slot['time_slot'],
                        'subject_id': slot['subject_id'],
                        'faculty_id': slot['faculty_id'],
                        'classroom_id': slot['classroom_id'],
                        'batch_id': batch_id,
                        'is_fixed': True
                    })
        
        # Create a list of all required classes based on scheduling preferences
        required_classes = []
        for subject in subjects:
            # Calculate blocks based on scheduling preference
            blocks = self.calculate_subject_blocks(subject)
            
            for block_size in blocks:
                # Create a class entry for each block
                class_entry = subject.copy()
                class_entry['block_size'] = block_size
                class_entry['is_continuous_block'] = block_size > 1
                required_classes.append(class_entry)
        
        print(f"Need to schedule {len(required_classes)} total classes")
        
        # Shuffle for randomization
        random.shuffle(required_classes)
        
        scheduled_count = 0
        # Try to schedule each class
        for subject in required_classes:
            scheduled = False
            available_faculty = self.get_available_faculty(subject['id'], batch_id)
            available_classrooms = self.get_available_classrooms(batch_id, subject.get('requires_lab', False))
            block_size = subject.get('block_size', 1)
            
            print(f"Scheduling {subject['name']} (block size: {block_size}): {len(available_faculty)} faculty, {len(available_classrooms)} classrooms")
            
            if not available_faculty:
                print(f"No faculty available for {subject['name']}")
                continue
                
            if not available_classrooms:
                print(f"No classrooms available for {subject['name']}")
                continue
            
            # Try different combinations of day, time, faculty, and classroom
            attempts = 0
            max_attempts = 100
            
            while not scheduled and attempts < max_attempts:
                day_idx = random.randint(0, len(self.days) - 1)
                faculty = random.choice(available_faculty)
                classroom = random.choice(available_classrooms)
                
                # Special handling for lab subjects - use lab-specific time slots
                if subject.get('requires_lab', False) and block_size == 4:
                    # For lab sessions, use specific lab start times
                    lab_start_times = self.get_lab_start_times()
                    time_slot = random.choice(lab_start_times)
                else:
                    # For regular classes, use normal time slots
                    time_slot = random.choice(self.time_slots)
                
                # Check if continuous block can be scheduled
                if self.can_schedule_block(day_idx, time_slot, faculty['id'], classroom['id'], schedule, block_size):
                    # Check faculty workload constraints
                    daily_hours, total_hours = self.calculate_faculty_workload(faculty['id'], schedule)
                    
                    if (daily_hours[day_idx] + block_size <= faculty.get('max_hours_per_day', 6) and 
                        total_hours + block_size <= faculty.get('max_hours_per_week', 20)):
                        
                        # Check if batch doesn't exceed max classes per day
                        batch_daily_classes = sum(1 for entry in schedule 
                                                if entry['day_of_week'] == day_idx and 
                                                   entry.get('batch_id') == batch_id)
                        
                        if batch_daily_classes + block_size <= self.max_classes_per_day:
                            
                            # Validate all required IDs are present
                            if not all([subject.get('id'), faculty.get('id'), classroom.get('id'), batch_id]):
                                print(f"ERROR: Missing required IDs - subject: {subject.get('id')}, faculty: {faculty.get('id')}, room: {classroom.get('id')}")
                                attempts += 1
                                continue
                                
                            # Schedule the block (lab or regular)
                            # Get consecutive slots starting from time_slot
                            block_slots = self.get_consecutive_slots(time_slot, block_size)
                            
                            for i, slot in enumerate(block_slots):
                                schedule.append({
                                    'day_of_week': day_idx,
                                    'time_slot': slot,
                                    'subject_id': subject['id'],
                                    'faculty_id': faculty['id'],
                                    'classroom_id': classroom['id'],
                                    'batch_id': batch_id,
                                    'is_fixed': False,
                                    'block_size': block_size,
                                    'is_continuous_block': True if block_size > 1 else False,
                                    'is_lab': subject.get('requires_lab', False)
                                })
                            
                            scheduled = True
                            scheduled_count += block_size
                
                attempts += 1
            
            if not scheduled:
                print(f"Could not schedule {subject['name']} after {max_attempts} attempts")
        
        print(f"Successfully scheduled {scheduled_count} out of {len(required_classes)} classes")
        print(f"Timetable generated for {assigned_shift} shift")
        return schedule
    
    def evaluate_timetable(self, schedule):
        """Evaluate the quality of a timetable"""
        score = 100
        
        # Penalty for uneven distribution across days
        daily_classes = defaultdict(int)
        for entry in schedule:
            if not entry.get('is_fixed', False):
                daily_classes[entry['day_of_week']] += 1
        
        if daily_classes:
            avg_classes = sum(daily_classes.values()) / len(daily_classes)
            for day_classes in daily_classes.values():
                score -= abs(day_classes - avg_classes) * 2
        
        # Penalty for faculty overload
        faculty_workload = defaultdict(int)
        for entry in schedule:
            faculty_workload[entry['faculty_id']] += 1
        
        for workload in faculty_workload.values():
            if workload > 20:  # Assuming 20 is max weekly hours
                score -= (workload - 20) * 5
        
        # Bonus for classroom utilization
        classroom_usage = defaultdict(int)
        for entry in schedule:
            classroom_usage[entry['classroom_id']] += 1
        
        if classroom_usage:
            avg_usage = sum(classroom_usage.values()) / len(classroom_usage)
            score += avg_usage * 2
        
        return max(0, score)
    
    def format_timetable_for_display(self, schedule):
        """Format timetable for frontend display"""
        formatted_schedule = []
        for entry in schedule:
            # Validate entry has required fields
            if not all([entry.get('subject_id'), entry.get('faculty_id'), entry.get('classroom_id')]):
                print(f"WARNING: Skipping entry with missing IDs - subject_id: {entry.get('subject_id')}, faculty_id: {entry.get('faculty_id')}, classroom_id: {entry.get('classroom_id')}")
                continue
                
            # Get subject, faculty, and classroom details using SQLAlchemy
            subject = Subject.query.get(entry['subject_id'])
            faculty = Faculty.query.get(entry['faculty_id'])
            classroom = Classroom.query.get(entry['classroom_id'])
            
            # Skip if any of the referenced objects don't exist
            if not all([subject, faculty, classroom]):
                print(f"WARNING: Skipping entry with invalid references - subject: {subject}, faculty: {faculty}, classroom: {classroom}")
                continue
            
            formatted_entry = {
                'day': self.days[entry['day_of_week']],
                'day_index': entry['day_of_week'],
                'time_slot': entry['time_slot'],
                'subject_name': subject.name,
                'subject_code': subject.code,
                'faculty_name': faculty.name,
                'classroom_name': classroom.name,
                'is_fixed': entry.get('is_fixed', False),
                'subject_id': entry['subject_id'],
                'faculty_id': entry['faculty_id'],
                'classroom_id': entry['classroom_id']
            }
            formatted_schedule.append(formatted_entry)
        
        return formatted_schedule
    
    def generate_time_slots(self, start_time, end_time, lunch_break_duration, lunch_break_start_time='12:15'):
        """Generate time slots based on college timing with proper Indian college format"""
        slots = []
        current_time = start_time
        end_time_minutes = self.time_to_minutes(end_time)
        lunch_start_time = lunch_break_start_time
        lunch_end_time = self.add_minutes_to_time(lunch_start_time, lunch_break_duration)
        
        # Standard Indian college periods (45 minutes each with 0-minute breaks)
        period_duration = 45
        break_duration = 0
        
        period_count = 1
        
        while self.time_to_minutes(current_time) < end_time_minutes:
            slot_end_time = self.add_minutes_to_time(current_time, period_duration)
            
            # Check if this period would overlap with lunch break
            if (self.time_to_minutes(current_time) < self.time_to_minutes(lunch_start_time) and 
                self.time_to_minutes(slot_end_time) > self.time_to_minutes(lunch_start_time)):
                # This period would overlap with lunch, so skip to end of lunch break
                current_time = lunch_end_time
                continue
                
            # Check if we're in lunch break period
            if (self.time_to_minutes(current_time) >= self.time_to_minutes(lunch_start_time) and 
                self.time_to_minutes(current_time) < self.time_to_minutes(lunch_end_time)):
                # Skip to end of lunch break
                current_time = lunch_end_time
                continue
                
            # Add the time slot if it doesn't exceed end time
            if self.time_to_minutes(slot_end_time) <= end_time_minutes:
                slot = f"{current_time}-{slot_end_time}"
                slots.append(slot)
                
                # Move to next period (add period duration + break)
                current_time = self.add_minutes_to_time(current_time, period_duration + break_duration)
                period_count += 1
            else:
                break
        
        return slots
    
    def get_lab_time_slots(self):
        """DEPRECATED: Use get_lab_start_times instead"""
        return self.get_lab_start_times()

    def get_lab_start_times(self):
        """Get valid start times for lab sessions (Morning 9:00, Afternoon 1:30)"""
        return [
            "09:00-09:45",  # Start of Morning Session (runs 9:00-12:00)
            "13:30-14:15"   # Start of Afternoon Session (runs 1:30-4:30)
        ]
    
    def can_schedule_lab_block(self, timetable, day_idx, lab_slot, faculty_id, classroom_id):
        """Check if a 3-hour lab block can be scheduled at the given time"""
        # Check if the lab slot is available for the batch, faculty, and classroom
        for existing_entry in timetable:
            if (existing_entry['day'] == day_idx and 
                existing_entry['time_slot'] == lab_slot and
                (existing_entry['faculty_id'] == faculty_id or 
                 existing_entry['classroom_id'] == classroom_id)):
                return False
        return True
    
    def calculate_lunch_start_time(self, start_time, end_time):
        """Calculate lunch break start time (middle of the day)"""
        start_minutes = self.time_to_minutes(start_time)
        end_minutes = self.time_to_minutes(end_time)
        total_minutes = end_minutes - start_minutes
        lunch_start_minutes = start_minutes + (total_minutes // 2)
        
        # Round to nearest 15-minute interval
        rounded = round(lunch_start_minutes / 15) * 15
        return self.minutes_to_time(rounded)
    
    def calculate_short_break_start_time(self, start_time):
        """Calculate short break start time (approximately 1.5 hours after start)"""
        start_minutes = self.time_to_minutes(start_time)
        break_minutes = start_minutes + 90  # 1.5 hours
        return self.minutes_to_time(break_minutes)
    
    def add_minutes_to_time(self, time_str, minutes):
        """Add minutes to a time string"""
        total_minutes = self.time_to_minutes(time_str) + minutes
        return self.minutes_to_time(total_minutes)
    
    def time_to_minutes(self, time_str):
        """Convert time string to minutes"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def minutes_to_time(self, total_minutes):
        """Convert minutes to time string"""
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def generate_optimized_timetables(self, batch_id, semester, num_options=3, include_short_break=False, short_break_duration=10, college_start_time='09:00', college_end_time='16:30', lunch_break_duration=60, lunch_break_start_time='12:15'):
        """Generate multiple optimized timetable options"""
        options = []
        
        try:
            for i in range(num_options):
                print(f"Generating timetable option {i+1}")
                schedule = self.generate_single_timetable(batch_id, semester)
                
                if not schedule:
                    print(f"No schedule generated for option {i+1}")
                    continue
                    
                score = self.evaluate_timetable(schedule)
                formatted_schedule = self.format_timetable_for_display(schedule)
                
                options.append({
                    'option_id': i + 1,
                    'score': score,
                    'schedule': formatted_schedule,
                    'total_classes': len([entry for entry in schedule if not entry.get('is_fixed', False)]),
                    'utilization_stats': self.get_utilization_stats(schedule)
                })
                print(f"Option {i+1} generated successfully with score {score}")
            
            # Sort by score (best first)
            options.sort(key=lambda x: x['score'], reverse=True)
            print(f"Generated {len(options)} total options")
            
            return options
            
        except Exception as e:
            print(f"Error in generate_optimized_timetables: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_utilization_stats(self, schedule):
        """Get utilization statistics for a timetable"""
        faculty_hours = defaultdict(int)
        classroom_hours = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for entry in schedule:
            if not entry.get('is_fixed', False):
                faculty_hours[entry['faculty_id']] += 1
                classroom_hours[entry['classroom_id']] += 1
                daily_distribution[entry['day_of_week']] += 1
        
        return {
            'faculty_utilization': dict(faculty_hours),
            'classroom_utilization': dict(classroom_hours),
            'daily_distribution': dict(daily_distribution)
        }

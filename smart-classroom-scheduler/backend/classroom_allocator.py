"""
Smart Classroom Allocation System
Handles dynamic classroom sharing between branches and sections
"""

from models import db, Classroom, Batch, Subject, TimetableEntry, ClassroomAllocation
from sqlalchemy import and_, or_
from datetime import datetime
import logging

class SmartClassroomAllocator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_priority_score(self, batch, classroom, time_slot, day_of_week, subject=None):
        """
        Calculate priority score for classroom allocation
        Higher score = Higher priority
        """
        score = 0
        
        # Base priority from batch
        if batch.priority_for_allocation == 1:  # High priority batch
            score += 100
        elif batch.priority_for_allocation == 2:  # Medium priority batch
            score += 50
        else:  # Low priority batch
            score += 25
        
        # Fixed allocation gets highest priority
        if classroom.is_fixed_allocation and classroom.fixed_batch_id == batch.id:
            score += 200
        
        # Classroom priority level
        if classroom.priority_level == 1:  # High priority classroom
            score += 75
        elif classroom.priority_level == 2:  # Medium priority classroom
            score += 40
        else:  # Low priority classroom
            score += 15
        
        # Subject type considerations
        if subject:
            if subject.requires_lab and classroom.type == 'lab':
                score += 150  # Lab subjects get high priority for lab rooms
            elif not subject.requires_lab and classroom.type == 'regular':
                score += 50   # Regular subjects prefer regular rooms
            elif subject.requires_lab and classroom.type == 'regular':
                score -= 50   # Lab subjects in regular rooms get penalty
        
        # Capacity matching (prefer rooms that match student count)
        if batch.student_count <= classroom.capacity:
            capacity_efficiency = (batch.student_count / classroom.capacity) * 100
            if capacity_efficiency >= 80:  # 80-100% utilization is ideal
                score += 30
            elif capacity_efficiency >= 60:  # 60-80% is good
                score += 20
            elif capacity_efficiency >= 40:  # 40-60% is acceptable
                score += 10
            # Below 40% gets no bonus (wasteful)
        else:
            score -= 100  # Room too small gets heavy penalty
        
        return score
    
    def find_available_classrooms(self, batch_id, day_of_week, time_slot, subject_id=None):
        """
        Find all available classrooms for a given time slot
        Returns list of (classroom, priority_score, allocation_type)
        """
        batch = Batch.query.get(batch_id)
        subject = Subject.query.get(subject_id) if subject_id else None
        
        # Get all classrooms
        all_classrooms = Classroom.query.all()
        available_classrooms = []
        
        for classroom in all_classrooms:
            allocation_info = self.check_classroom_availability(
                classroom, batch, day_of_week, time_slot, subject
            )
            
            if allocation_info['available']:
                priority_score = self.calculate_priority_score(
                    batch, classroom, time_slot, day_of_week, subject
                )
                
                available_classrooms.append({
                    'classroom': classroom,
                    'priority_score': priority_score,
                    'allocation_type': allocation_info['type'],
                    'can_borrow': allocation_info.get('can_borrow', False),
                    'original_owner': allocation_info.get('original_owner', None)
                })
        
        # Sort by priority score (highest first)
        available_classrooms.sort(key=lambda x: x['priority_score'], reverse=True)
        return available_classrooms
    
    def check_classroom_availability(self, classroom, requesting_batch, day_of_week, time_slot, subject=None):
        """
        Check if a classroom is available for allocation
        Returns availability info with allocation type
        """
        # Check if classroom is already occupied at this time
        existing_entry = TimetableEntry.query.filter_by(
            classroom_id=classroom.id,
            day_of_week=day_of_week,
            time_slot=time_slot
        ).first()
        
        if existing_entry:
            # Check if it's the same batch (updating existing schedule)
            if existing_entry.batch_id == requesting_batch.id:
                return {
                    'available': True,
                    'type': 'own_existing',
                    'reason': 'Already allocated to same batch'
                }
            else:
                return {
                    'available': False,
                    'type': 'occupied',
                    'reason': f'Occupied by batch {existing_entry.batch.name}'
                }
        
        # Check if this is a fixed allocation classroom
        if classroom.is_fixed_allocation:
            if classroom.fixed_batch_id == requesting_batch.id:
                return {
                    'available': True,
                    'type': 'fixed_own',
                    'reason': 'Own fixed classroom'
                }
            else:
                # Check if the fixed owner has a lab session at this time
                fixed_owner_lab_session = self.check_batch_has_lab_session(
                    classroom.fixed_batch_id, day_of_week, time_slot
                )
                
                if fixed_owner_lab_session and classroom.can_be_shared:
                    return {
                        'available': True,
                        'type': 'temporary_borrow',
                        'can_borrow': True,
                        'original_owner': classroom.fixed_batch_id,
                        'reason': 'Fixed owner has lab session - can borrow'
                    }
                else:
                    return {
                        'available': False,
                        'type': 'fixed_unavailable',
                        'reason': 'Fixed to another batch and not shareable'
                    }
        
        # Regular classroom - available for allocation
        return {
            'available': True,
            'type': 'regular_available',
            'reason': 'Regular classroom available'
        }
    
    def check_batch_has_lab_session(self, batch_id, day_of_week, time_slot):
        """
        Check if a batch has a lab session at the given time
        """
        lab_entry = db.session.query(TimetableEntry).join(Subject).filter(
            and_(
                TimetableEntry.batch_id == batch_id,
                TimetableEntry.day_of_week == day_of_week,
                TimetableEntry.time_slot == time_slot,
                Subject.requires_lab == True
            )
        ).first()
        
        return lab_entry is not None
    
    def allocate_classroom_smart(self, batch_id, subject_id, faculty_id, day_of_week, time_slot, timetable_id):
        """
        Smart classroom allocation with dynamic sharing
        Returns allocated classroom info or None if no suitable classroom found
        """
        available_classrooms = self.find_available_classrooms(
            batch_id, day_of_week, time_slot, subject_id
        )
        
        if not available_classrooms:
            self.logger.warning(f"No available classrooms for batch {batch_id} at {time_slot}")
            return None
        
        # Get the best classroom (highest priority score)
        best_allocation = available_classrooms[0]
        classroom = best_allocation['classroom']
        allocation_type = best_allocation['allocation_type']
        
        # Create timetable entry
        is_temporary = allocation_type == 'temporary_borrow'
        original_owner_id = best_allocation.get('original_owner') if is_temporary else None
        
        allocation_reason = None
        if is_temporary:
            allocation_reason = 'borrowed_during_lab_session'
        elif allocation_type == 'fixed_own':
            allocation_reason = 'fixed_classroom'
        
        timetable_entry = TimetableEntry(
            timetable_id=timetable_id,
            batch_id=batch_id,
            subject_id=subject_id,
            faculty_id=faculty_id,
            classroom_id=classroom.id,
            day_of_week=day_of_week,
            time_slot=time_slot,
            is_temporary_allocation=is_temporary,
            original_classroom_owner_id=original_owner_id,
            allocation_reason=allocation_reason
        )
        
        # Create classroom allocation record for tracking
        classroom_allocation = ClassroomAllocation(
            classroom_id=classroom.id,
            batch_id=batch_id,
            day_of_week=day_of_week,
            time_slot=time_slot,
            allocation_type=allocation_type,
            priority_score=best_allocation['priority_score']
        )
        
        try:
            db.session.add(timetable_entry)
            db.session.add(classroom_allocation)
            db.session.commit()
            
            self.logger.info(f"Successfully allocated classroom {classroom.name} to batch {batch_id}")
            return {
                'success': True,
                'classroom': classroom,
                'allocation_type': allocation_type,
                'is_temporary': is_temporary,
                'timetable_entry': timetable_entry
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to allocate classroom: {str(e)}")
            return None
    
    def get_classroom_utilization_report(self):
        """
        Generate classroom utilization report
        """
        classrooms = Classroom.query.all()
        report = []
        
        for classroom in classrooms:
            # Count total allocated slots
            total_slots = TimetableEntry.query.filter_by(classroom_id=classroom.id).count()
            
            # Count temporary allocations
            temp_slots = TimetableEntry.query.filter_by(
                classroom_id=classroom.id,
                is_temporary_allocation=True
            ).count()
            
            # Calculate utilization (assuming 5 days * 8 slots = 40 total possible slots)
            max_possible_slots = 40
            utilization_percentage = (total_slots / max_possible_slots) * 100
            
            report.append({
                'classroom': classroom,
                'total_slots_used': total_slots,
                'temporary_allocations': temp_slots,
                'fixed_allocations': total_slots - temp_slots,
                'utilization_percentage': round(utilization_percentage, 2),
                'sharing_efficiency': round((temp_slots / total_slots * 100), 2) if total_slots > 0 else 0
            })
        
        return report
    
    def optimize_classroom_assignments(self):
        """
        Optimize existing classroom assignments for better utilization
        """
        # Get all current timetable entries
        entries = TimetableEntry.query.all()
        optimization_suggestions = []
        
        for entry in entries:
            # Find better classroom options
            better_options = self.find_available_classrooms(
                entry.batch_id, entry.day_of_week, entry.time_slot, entry.subject_id
            )
            
            if better_options:
                current_classroom = entry.classroom
                best_option = better_options[0]
                
                # If we found a significantly better option
                current_score = self.calculate_priority_score(
                    entry.batch, current_classroom, entry.time_slot, entry.day_of_week, entry.subject
                )
                
                if best_option['priority_score'] > current_score + 50:  # Significant improvement threshold
                    optimization_suggestions.append({
                        'entry': entry,
                        'current_classroom': current_classroom,
                        'suggested_classroom': best_option['classroom'],
                        'improvement_score': best_option['priority_score'] - current_score,
                        'reason': f"Better match: {best_option['allocation_type']}"
                    })
        
        return optimization_suggestions

# Utility functions for batch and section management
def extract_branch_section_from_name(batch_name):
    """
    Extract branch and section from batch name
    Example: "CSE-A-2025" -> branch="CSE", section="A"
    """
    parts = batch_name.split('-')
    if len(parts) >= 2:
        return parts[0], parts[1]  # branch, section
    return batch_name, "A"  # default section

def generate_batch_name(branch, section, year):
    """
    Generate standardized batch name
    """
    return f"{branch}-{section}-{year}"

def get_batches_by_branch(branch):
    """
    Get all batches for a specific branch
    """
    return Batch.query.filter_by(branch=branch).all()

def get_sections_by_branch_semester(branch, semester):
    """
    Get all sections for a branch and semester
    """
    return Batch.query.filter_by(branch=branch, semester=semester).all()

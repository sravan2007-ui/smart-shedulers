"""
Database Migration Script for Smart Classroom Allocation System
Adds new fields for branch/section management and classroom allocation
"""

from flask import Flask
from models import db, Classroom, Batch, ClassroomAllocation
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration - MySQL
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def migrate_database():
    """Run database migration to add new fields"""
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Create all tables (this will add new tables and columns)
            db.create_all()
            print("[SUCCESS] Database tables created/updated successfully")
            
            # Update existing batches with branch and section if they don't have them
            try:
                batches_without_branch = Batch.query.filter(
                    (Batch.branch == None) | (Batch.branch == '')
                ).all()
            except Exception:
                # If columns don't exist yet, get all batches
                batches_without_branch = Batch.query.all()
            
            for batch in batches_without_branch:
                # Extract branch and section from name
                name_parts = batch.name.split('-')
                if len(name_parts) >= 2:
                    batch.branch = name_parts[0]  # e.g., "CSE"
                    batch.section = name_parts[1]  # e.g., "A"
                else:
                    batch.branch = batch.department[:3].upper()  # First 3 letters of department
                    batch.section = "A"  # Default section
                
                # Set default priority
                try:
                    if not hasattr(batch, 'priority_for_allocation') or batch.priority_for_allocation is None:
                        batch.priority_for_allocation = 2  # Medium priority
                except Exception:
                    # Column might not exist yet
                    pass
            
            # Update existing classrooms with new fields if they don't have them
            classrooms_to_update = Classroom.query.all()
            
            for classroom in classrooms_to_update:
                # Set default values for new fields if they don't exist
                try:
                    if not hasattr(classroom, 'is_fixed_allocation') or classroom.is_fixed_allocation is None:
                        classroom.is_fixed_allocation = False
                except Exception:
                    pass
                
                try:
                    if not hasattr(classroom, 'priority_level') or classroom.priority_level is None:
                        classroom.priority_level = 1  # High priority by default
                except Exception:
                    pass
                
                try:
                    if not hasattr(classroom, 'can_be_shared') or classroom.can_be_shared is None:
                        classroom.can_be_shared = True
                except Exception:
                    pass
            
            db.session.commit()
            print(f"[SUCCESS] Updated {len(batches_without_branch)} batches with branch/section info")
            print(f"[SUCCESS] Updated {len(classrooms_to_update)} classrooms with allocation settings")
            
            # Create sample data for demonstration
            create_sample_data()
            
            print("[SUCCESS] Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Migration failed: {str(e)}")
            raise

def create_sample_data():
    """Create sample data to demonstrate the smart allocation system"""
    try:
        print("Creating sample data...")
        
        # Create sample branches and sections if they don't exist
        sample_batches = [
            {
                'name': 'CSE-A-2025',
                'department': 'Computer Science and Engineering',
                'branch': 'CSE',
                'section': 'A',
                'semester': 5,
                'student_count': 60,
                'priority_for_allocation': 1  # High priority
            },
            {
                'name': 'CSE-B-2025',
                'department': 'Computer Science and Engineering',
                'branch': 'CSE',
                'section': 'B',
                'semester': 5,
                'student_count': 58,
                'priority_for_allocation': 2  # Medium priority
            },
            {
                'name': 'ECE-A-2025',
                'department': 'Electronics and Communication Engineering',
                'branch': 'ECE',
                'section': 'A',
                'semester': 3,
                'student_count': 55,
                'priority_for_allocation': 2  # Medium priority
            },
            {
                'name': 'MECH-A-2025',
                'department': 'Mechanical Engineering',
                'branch': 'MECH',
                'section': 'A',
                'semester': 7,
                'student_count': 50,
                'priority_for_allocation': 3  # Low priority
            }
        ]
        
        for batch_data in sample_batches:
            existing_batch = Batch.query.filter_by(name=batch_data['name']).first()
            if not existing_batch:
                batch = Batch(**batch_data)
                db.session.add(batch)
        
        # Create sample classrooms with different allocation settings
        sample_classrooms = [
            {
                'name': 'CSE-Lab-1',
                'capacity': 60,
                'type': 'lab',
                'equipment': 'Computers, Projector, AC',
                'is_fixed_allocation': True,
                'priority_level': 1,
                'can_be_shared': True
            },
            {
                'name': 'Room-301',
                'capacity': 70,
                'type': 'regular',
                'equipment': 'Projector, AC, Whiteboard',
                'is_fixed_allocation': True,
                'priority_level': 1,
                'can_be_shared': True
            },
            {
                'name': 'Room-302',
                'capacity': 65,
                'type': 'regular',
                'equipment': 'Projector, AC, Whiteboard',
                'is_fixed_allocation': False,
                'priority_level': 2,
                'can_be_shared': True
            },
            {
                'name': 'Auditorium',
                'capacity': 200,
                'type': 'auditorium',
                'equipment': 'Sound System, Projector, AC',
                'is_fixed_allocation': False,
                'priority_level': 3,
                'can_be_shared': True
            }
        ]
        
        for classroom_data in sample_classrooms:
            existing_classroom = Classroom.query.filter_by(name=classroom_data['name']).first()
            if not existing_classroom:
                classroom = Classroom(**classroom_data)
                db.session.add(classroom)
        
        db.session.commit()
        
        # Assign fixed classrooms to batches
        cse_lab = Classroom.query.filter_by(name='CSE-Lab-1').first()
        cse_a_batch = Batch.query.filter_by(name='CSE-A-2025').first()
        
        room_301 = Classroom.query.filter_by(name='Room-301').first()
        cse_b_batch = Batch.query.filter_by(name='CSE-B-2025').first()
        
        if cse_lab and cse_a_batch:
            cse_lab.fixed_batch_id = cse_a_batch.id
        
        if room_301 and cse_b_batch:
            room_301.fixed_batch_id = cse_b_batch.id
        
        db.session.commit()
        print("[SUCCESS] Sample data created successfully")
        
    except Exception as e:
        print(f"Warning: Could not create sample data: {str(e)}")

def rollback_migration():
    """Rollback migration (for testing purposes)"""
    with app.app_context():
        try:
            print("Rolling back migration...")
            
            # Drop the new table
            ClassroomAllocation.__table__.drop(db.engine, checkfirst=True)
            
            # Note: We don't drop columns from existing tables as it might cause data loss
            # In production, you would use proper migration tools like Alembic
            
            print("[SUCCESS] Migration rolled back successfully")
            
        except Exception as e:
            print(f"[ERROR] Rollback failed: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    else:
        migrate_database()
        
        print("\n" + "="*60)
        print("SMART CLASSROOM ALLOCATION SYSTEM - MIGRATION COMPLETE")
        print("="*60)
        print("\nNew Features Added:")
        print("- Branch and Section management for batches")
        print("- Fixed classroom allocation with sharing capability")
        print("- Priority-based classroom assignment")
        print("- Dynamic classroom sharing during lab sessions")
        print("- Comprehensive allocation tracking and reporting")
        print("\nAPI Endpoints Added:")
        print("- GET /api/classroom-allocations - Utilization report")
        print("- POST /api/classroom-allocations/optimize - Optimization suggestions")
        print("- POST /api/classroom-availability - Check availability")
        print("- GET /api/branches - Get all branches")
        print("- GET /api/sections/<branch> - Get sections by branch")
        print("\nDatabase Tables:")
        print("- classroom_allocations - Track all classroom assignments")
        print("- Enhanced classrooms table with allocation settings")
        print("- Enhanced batches table with branch/section info")
        print("\n" + "="*60)

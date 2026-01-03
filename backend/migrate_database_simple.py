"""
Simple Database Migration Script for Smart Classroom Allocation System
Uses raw SQL to add new columns safely
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = int(os.getenv('MYSQL_PORT', '3306'))
mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')

def migrate_database():
    """Run database migration using raw SQL"""
    connection = None
    try:
        print("Connecting to MySQL database...")
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        print("[SUCCESS] Connected to database")
        
        # Add new columns to batches table
        print("Adding new columns to batches table...")
        batch_columns = [
            ("branch", "ALTER TABLE batches ADD COLUMN branch VARCHAR(100) NOT NULL DEFAULT ''"),
            ("section", "ALTER TABLE batches ADD COLUMN section VARCHAR(10) NOT NULL DEFAULT 'A'"),
            ("priority_for_allocation", "ALTER TABLE batches ADD COLUMN priority_for_allocation INT DEFAULT 2")
        ]
        
        for column_name, sql in batch_columns:
            try:
                cursor.execute(sql)
                print(f"[SUCCESS] Added column {column_name} to batches table")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"[INFO] Column {column_name} already exists in batches table")
                else:
                    print(f"[WARNING] Failed to add column {column_name}: {e}")
        
        # Add new columns to classrooms table
        print("Adding new columns to classrooms table...")
        classroom_columns = [
            ("is_fixed_allocation", "ALTER TABLE classrooms ADD COLUMN is_fixed_allocation BOOLEAN DEFAULT FALSE"),
            ("fixed_batch_id", "ALTER TABLE classrooms ADD COLUMN fixed_batch_id INT DEFAULT NULL"),
            ("priority_level", "ALTER TABLE classrooms ADD COLUMN priority_level INT DEFAULT 1"),
            ("can_be_shared", "ALTER TABLE classrooms ADD COLUMN can_be_shared BOOLEAN DEFAULT TRUE")
        ]
        
        for column_name, sql in classroom_columns:
            try:
                cursor.execute(sql)
                print(f"[SUCCESS] Added column {column_name} to classrooms table")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"[INFO] Column {column_name} already exists in classrooms table")
                else:
                    print(f"[WARNING] Failed to add column {column_name}: {e}")
        
        # Add foreign key constraint for classrooms
        try:
            cursor.execute("""
                ALTER TABLE classrooms 
                ADD CONSTRAINT fk_classroom_fixed_batch 
                FOREIGN KEY (fixed_batch_id) REFERENCES batches(id) 
                ON DELETE SET NULL
            """)
            print("[SUCCESS] Added foreign key constraint for classrooms")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print("[INFO] Foreign key constraint already exists")
            else:
                print(f"[WARNING] Failed to add foreign key: {e}")
        
        # Create classroom_allocations table
        print("Creating classroom_allocations table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classroom_allocations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    classroom_id INT NOT NULL,
                    batch_id INT NOT NULL,
                    day_of_week INT NOT NULL,
                    time_slot VARCHAR(20) NOT NULL,
                    allocation_type VARCHAR(20) DEFAULT 'regular',
                    priority_score INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                    INDEX idx_classroom_time (classroom_id, day_of_week, time_slot),
                    INDEX idx_batch_time (batch_id, day_of_week, time_slot)
                )
            """)
            print("[SUCCESS] Created classroom_allocations table")
        except Exception as e:
            print(f"[INFO] classroom_allocations table might already exist: {e}")
        
        # Add new columns to timetable_entries table
        print("Adding new columns to timetable_entries table...")
        timetable_entry_columns = [
            ("is_temporary_allocation", "ALTER TABLE timetable_entries ADD COLUMN is_temporary_allocation BOOLEAN DEFAULT FALSE"),
            ("original_classroom_owner_id", "ALTER TABLE timetable_entries ADD COLUMN original_classroom_owner_id INT DEFAULT NULL"),
            ("allocation_reason", "ALTER TABLE timetable_entries ADD COLUMN allocation_reason VARCHAR(100) DEFAULT NULL")
        ]
        
        for column_name, sql in timetable_entry_columns:
            try:
                cursor.execute(sql)
                print(f"[SUCCESS] Added column {column_name} to timetable_entries table")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"[INFO] Column {column_name} already exists in timetable_entries table")
                else:
                    print(f"[WARNING] Failed to add column {column_name}: {e}")
        
        # Add foreign key for original_classroom_owner_id
        try:
            cursor.execute("""
                ALTER TABLE timetable_entries 
                ADD CONSTRAINT fk_timetable_original_owner 
                FOREIGN KEY (original_classroom_owner_id) REFERENCES batches(id) 
                ON DELETE SET NULL
            """)
            print("[SUCCESS] Added foreign key constraint for timetable_entries")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print("[INFO] Foreign key constraint already exists")
            else:
                print(f"[WARNING] Failed to add foreign key: {e}")
        
        # Add new columns to faculty_subjects table for better matching
        print("Adding new columns to faculty_subjects table...")
        faculty_subject_columns = [
            ("department", "ALTER TABLE faculty_subjects ADD COLUMN department VARCHAR(100) DEFAULT NULL"),
            ("branch", "ALTER TABLE faculty_subjects ADD COLUMN branch VARCHAR(100) DEFAULT NULL"),
            ("semester", "ALTER TABLE faculty_subjects ADD COLUMN semester INT DEFAULT NULL"),
            ("is_primary", "ALTER TABLE faculty_subjects ADD COLUMN is_primary BOOLEAN DEFAULT TRUE"),
            ("priority", "ALTER TABLE faculty_subjects ADD COLUMN priority INT DEFAULT 1")
        ]
        
        for column_name, sql in faculty_subject_columns:
            try:
                cursor.execute(sql)
                print(f"[SUCCESS] Added column {column_name} to faculty_subjects table")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"[INFO] Column {column_name} already exists in faculty_subjects table")
                else:
                    print(f"[WARNING] Failed to add column {column_name}: {e}")
        
        # Update existing batches with branch and section info
        print("Updating existing batches with branch/section info...")
        try:
            cursor.execute("SELECT id, name, department FROM batches WHERE branch = '' OR branch IS NULL")
        except:
            # If branch column doesn't exist yet, get all batches
            cursor.execute("SELECT id, name, department FROM batches")
        batches_to_update = cursor.fetchall()
        
        for batch_id, name, department in batches_to_update:
            # Extract branch and section from name
            name_parts = name.split('-')
            if len(name_parts) >= 2:
                branch = name_parts[0]  # e.g., "CSE"
                section = name_parts[1]  # e.g., "A"
            else:
                branch = department[:3].upper() if department else "GEN"  # First 3 letters of department
                section = "A"  # Default section
            
            cursor.execute("""
                UPDATE batches 
                SET branch = %s, section = %s, priority_for_allocation = 2 
                WHERE id = %s
            """, (branch, section, batch_id))
        
        print(f"[SUCCESS] Updated {len(batches_to_update)} batches with branch/section info")
        
        # Create sample data
        create_sample_data(cursor)
        
        connection.commit()
        print("[SUCCESS] Database migration completed successfully!")
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"[ERROR] Migration failed: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()

def create_sample_data(cursor):
    """Create sample data to demonstrate the smart allocation system"""
    try:
        print("Creating sample data...")
        
        # Create sample batches if they don't exist
        sample_batches = [
            ('CSE-A-2025', 'Computer Science and Engineering', 'CSE', 'A', 5, 60, 1),
            ('CSE-B-2025', 'Computer Science and Engineering', 'CSE', 'B', 5, 58, 2),
            ('ECE-A-2025', 'Electronics and Communication Engineering', 'ECE', 'A', 3, 55, 2),
            ('MECH-A-2025', 'Mechanical Engineering', 'MECH', 'A', 7, 50, 3)
        ]
        
        for name, department, branch, section, semester, student_count, priority in sample_batches:
            cursor.execute("""
                INSERT IGNORE INTO batches (name, department, branch, section, semester, student_count, priority_for_allocation, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (name, department, branch, section, semester, student_count, priority))
        
        # Create sample classrooms if they don't exist
        sample_classrooms = [
            ('CSE-Lab-1', 60, 'lab', 'Computers, Projector, AC', True, 1, True),
            ('Room-301', 70, 'regular', 'Projector, AC, Whiteboard', True, 1, True),
            ('Room-302', 65, 'regular', 'Projector, AC, Whiteboard', False, 2, True),
            ('Auditorium', 200, 'auditorium', 'Sound System, Projector, AC', False, 3, True)
        ]
        
        for name, capacity, room_type, equipment, is_fixed, priority, can_share in sample_classrooms:
            cursor.execute("""
                INSERT IGNORE INTO classrooms (name, capacity, type, equipment, is_fixed_allocation, priority_level, can_be_shared, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (name, capacity, room_type, equipment, is_fixed, priority, can_share))
        
        # Assign fixed classrooms to batches
        cursor.execute("SELECT id FROM batches WHERE name = 'CSE-A-2025'")
        cse_a_result = cursor.fetchone()
        if cse_a_result:
            cse_a_id = cse_a_result[0]
            cursor.execute("UPDATE classrooms SET fixed_batch_id = %s WHERE name = 'CSE-Lab-1'", (cse_a_id,))
        
        cursor.execute("SELECT id FROM batches WHERE name = 'CSE-B-2025'")
        cse_b_result = cursor.fetchone()
        if cse_b_result:
            cse_b_id = cse_b_result[0]
            cursor.execute("UPDATE classrooms SET fixed_batch_id = %s WHERE name = 'Room-301'", (cse_b_id,))
        cursor.execute("COMMIT")
        
        # Create sample faculty-subject assignments for better matching
        print("Creating sample faculty-subject assignments...")
        try:
            # Get sample data
            cursor.execute("SELECT id FROM faculty WHERE name LIKE '%Rami%' OR name LIKE '%naidu%'")
            rami_result = cursor.fetchone()
            
            cursor.execute("SELECT id FROM subjects WHERE name LIKE '%DBMS%' OR name LIKE '%Database%'")
            dbms_result = cursor.fetchone()
            
            cursor.execute("SELECT id, department, branch, semester FROM batches WHERE name = 'CSE-A-2025'")
            cse_a_result = cursor.fetchone()
            
            if rami_result and dbms_result and cse_a_result:
                rami_id = rami_result[0]
                dbms_id = dbms_result[0]
                batch_id, department, branch, semester = cse_a_result
                
                # Create specific assignment for DBMS to Rami Naidu for CSE-A
                cursor.execute("""
                    INSERT IGNORE INTO faculty_subjects 
                    (faculty_id, subject_id, department, branch, semester, is_primary, priority, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (rami_id, dbms_id, department, branch, semester, True, 1))
                
                print(f"[SUCCESS] Assigned DBMS to Rami Naidu for {department} {branch} semester {semester}")
            
            # Create more sample assignments
            sample_assignments = [
                # Format: (faculty_name_pattern, subject_name_pattern, department, branch, semester, is_primary, priority)
                ('%Computer%', '%Programming%', 'Computer Science and Engineering', 'CSE', 5, True, 1),
                ('%Electronics%', '%Circuits%', 'Electronics and Communication Engineering', 'ECE', 3, True, 1),
                ('%Mechanical%', '%Thermodynamics%', 'Mechanical Engineering', 'MECH', 7, True, 1),
            ]
            
            for faculty_pattern, subject_pattern, dept, branch, sem, is_primary, priority in sample_assignments:
                # Find matching faculty and subjects
                cursor.execute("SELECT id FROM faculty WHERE department LIKE %s LIMIT 1", (f'%{dept}%',))
                faculty_result = cursor.fetchone()
                
                cursor.execute("SELECT id FROM subjects WHERE department LIKE %s LIMIT 1", (f'%{dept}%',))
                subject_result = cursor.fetchone()
                
                if faculty_result and subject_result:
                    cursor.execute("""
                        INSERT IGNORE INTO faculty_subjects 
                        (faculty_id, subject_id, department, branch, semester, is_primary, priority, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (faculty_result[0], subject_result[0], dept, branch, sem, is_primary, priority))
            
            print("[SUCCESS] Created sample faculty-subject assignments")
            
        except Exception as e:
            print(f"Warning: Could not create faculty-subject assignments: {str(e)}")
        
        print("[SUCCESS] Sample data created successfully")
        
    except Exception as e:
        print(f"Warning: Could not create sample data: {str(e)}")

if __name__ == "__main__":
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

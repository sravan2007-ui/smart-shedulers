import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from models import db, User, Subject, Faculty, Classroom, Batch, FacultySubject, Timetable, TimetableEntry, ClassroomAllocation

# Load environment variables
load_dotenv()

# MySQL Configuration (Source)
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')
mysql_uri = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# PostgreSQL Configuration (Destination)
# Using the provided connection string from the user
postgres_uri = "postgresql://neondb_owner:npg_AZoRuwUWf3J0@ep-restless-moon-addj5ic9.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

print(f"Source (MySQL): {mysql_uri}")
print(f"Destination (Postgres): {postgres_uri}")

def create_postgres_tables(pg_engine):
    """Create all tables in Postgres"""
    print("Creating tables in PostgreSQL...")
    # Create tables using the metadata from models
    db.metadata.create_all(pg_engine)
    print("Tables created.")

def migrate_data():
    # 1. Setup Connections
    mysql_engine = create_engine(mysql_uri)
    postgres_engine = create_engine(postgres_uri)
    
    SessionMySQL = sessionmaker(bind=mysql_engine)
    SessionPostgres = sessionmaker(bind=postgres_engine)
    
    session_mysql = SessionMySQL()
    session_pg = SessionPostgres()
    
    try:
        # 2. Create Tables in Postgres
        create_postgres_tables(postgres_engine)
        
        # 3. Migrate Data in Order of Dependency
        
        # Helper to migrate a table
        def migrate_table(Model, model_name):
            print(f"Migrating {model_name}...")
            # Query all records from MySQL
            records = session_mysql.query(Model).all()
            count = 0
            for record in records:
                # Merge the record into the Postgres session
                # make_transient ensures it's treated as a new object, 
                # but merging with primary key preservation is what we want.
                # Actually, simplest way is to iterate columns and create new instance.
                # But merging might work if we detach first.
                session_mysql.expunge(record) # Remove from MySQL session
                session_pg.merge(record)      # Add to Postgres session
                count += 1
            
            session_pg.commit()
            print(f"Migrated {count} {model_name} records.")

        # Order matters due to Foreign Keys!
        # 1. Users (No FK)
        migrate_table(User, "Users")
        
        # 2. Faculties (No FK)
        migrate_table(Faculty, "Faculty")
        
        # 3. Subjects (No FK)
        migrate_table(Subject, "Subjects")
        
        # 4. Batches (No FK)
        migrate_table(Batch, "Batches")
        
        # 5. Classrooms (FK to Batches - fixed_batch_id)
        migrate_table(Classroom, "Classrooms")
        
        # 6. FacultySubjects (FK to Faculty, Subject)
        migrate_table(FacultySubject, "FacultySubjects")
        
        # 7. Timetables (FK to Batch, User)
        migrate_table(Timetable, "Timetables")
        
        # 8. TimetableEntries (FK to Timetable, Batch, Subject, Faculty, Classroom)
        migrate_table(TimetableEntry, "TimetableEntries")
        
        # 9. ClassroomAllocations (FK to Classroom, Batch)
        migrate_table(ClassroomAllocation, "ClassroomAllocations")
        
        print("\nSUCCESS: Database migration completed successfully!")
        
    except Exception as e:
        session_pg.rollback()
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session_mysql.close()
        session_pg.close()

if __name__ == "__main__":
    migrate_data()

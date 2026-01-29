from backend.app import app, db
from sqlalchemy import text

def migrate_postgres():
    print("Starting PostgreSQL migration...")
    with app.app_context():
        # Get engine
        engine = db.engine
        print(f"Connected to: {engine.url}")
        
        tables = ['classrooms', 'subjects', 'faculty', 'batches']
        
        with engine.connect() as conn:
            for table in tables:
                print(f"Checking table '{table}'...")
                try:
                    # Check if column exists
                    # Postgres specific query
                    check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='created_by';")
                    result = conn.execute(check_sql).fetchone()
                    
                    if not result:
                        print(f"Adding created_by to {table}...")
                        # Add column
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN created_by INTEGER;"))
                        # Add FK
                        conn.execute(text(f"ALTER TABLE {table} ADD CONSTRAINT fk_{table}_created_by FOREIGN KEY (created_by) REFERENCES users(id);"))
                        conn.commit()
                        print(f"[SUCCESS] Updated {table}")
                    else:
                        print(f"[INFO] Column created_by already exists in {table}")
                except Exception as e:
                    print(f"[ERROR] Failed on {table}: {e}")
                    conn.rollback()

if __name__ == "__main__":
    migrate_postgres()

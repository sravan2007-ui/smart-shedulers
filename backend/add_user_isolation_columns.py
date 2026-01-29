import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def add_columns():
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_port = int(os.getenv('MYSQL_PORT', '3306'))
    mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')

    print("Connecting to database...")
    try:
        connection = pymysql.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            port=mysql_port,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("[SUCCESS] Connected to database")
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        return

    tables = ['classrooms', 'subjects', 'faculty', 'batches']
    
    try:
        with connection.cursor() as cursor:
            for table in tables:
                print(f"Checking table '{table}'...")
                
                # Check if column exists
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'created_by'")
                result = cursor.fetchone()
                
                if not result:
                    print(f"Adding created_by column to {table}...")
                    # Add column and FK constraint
                    # Note: We make it nullable so existing rows are valid
                    sql = f"""
                    ALTER TABLE {table} 
                    ADD COLUMN created_by INT NULL,
                    ADD CONSTRAINT fk_{table}_created_by 
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
                    """
                    cursor.execute(sql)
                    print(f"[SUCCESS] Added created_by to {table}")
                else:
                    print(f"[INFO] Column created_by already exists in {table}")
            
            connection.commit()
            print("[SUCCESS] All tables updated successfully")

    except Exception as e:
        print(f"[ERROR] Failed to update tables: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    add_columns()

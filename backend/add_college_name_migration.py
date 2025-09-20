#!/usr/bin/env python3
"""
Migration script to add college_name column to timetables table
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'sravan167')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_database = os.getenv('MYSQL_DATABASE', 'smart_classroom_scheduler')

database_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

def run_migration():
    """Add college_name column to timetables table"""
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :schema 
                AND TABLE_NAME = 'timetables' 
                AND COLUMN_NAME = 'college_name'
            """), {"schema": mysql_database})
            
            column_exists = result.fetchone()[0] > 0
            
            if not column_exists:
                print("Adding college_name column to timetables table...")
                connection.execute(text("""
                    ALTER TABLE timetables 
                    ADD COLUMN college_name VARCHAR(200) NULL 
                    AFTER timing_config
                """))
                connection.commit()
                print("Successfully added college_name column!")
            else:
                print("college_name column already exists!")
                
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

# Database Migration Guide

## Overview
The Smart Classroom Scheduler has been migrated from SQLite to PostgreSQL for better performance, scalability, and production readiness.

## Prerequisites

### 1. Install PostgreSQL
- Download and install PostgreSQL from https://www.postgresql.org/downloads/
- During installation, remember the password for the `postgres` user
- Default port is 5432

### 2. Create Database
```sql
-- Connect to PostgreSQL as postgres user
psql -U postgres

-- Create database
CREATE DATABASE smart_classroom_scheduler;

-- Create user (optional)
CREATE USER scheduler_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE smart_classroom_scheduler TO scheduler_user;
```

### 3. Update Environment Variables
Edit the `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/smart_classroom_scheduler
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_classroom_scheduler
DB_USER=postgres
DB_PASSWORD=your_password

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
```

## Installation Steps

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python setup_database.py
```

This script will:
- Create all database tables
- Create default admin user (admin/admin123)
- Populate with sample data (classrooms, subjects, faculty, batches)
- Create faculty-subject mappings

### 3. Run Application
```bash
python app.py
```

## Database Schema

### Tables Created:
- **users**: Authentication and user management
- **classrooms**: Physical classroom information
- **subjects**: Course subjects with credits and hours
- **faculty**: Faculty member details
- **batches**: Student batch information
- **faculty_subjects**: Many-to-many mapping between faculty and subjects
- **timetables**: Generated timetable entries

## Key Changes from SQLite

### 1. Database Connection
- **Old**: Direct SQLite connection with `sqlite3`
- **New**: SQLAlchemy ORM with PostgreSQL

### 2. Models
- **Old**: Raw SQL queries
- **New**: SQLAlchemy models in `models.py`

### 3. Data Types
- **Old**: SQLite flexible typing
- **New**: PostgreSQL strict typing with proper constraints

### 4. Relationships
- **Old**: Manual foreign key handling
- **New**: SQLAlchemy relationships and backref

## Sample Data Included

### Classrooms:
- Room A101 (60 capacity, regular)
- Room A102 (50 capacity, regular)
- Lab B201 (30 capacity, lab)
- Lab B202 (25 capacity, lab)
- Hall C301 (100 capacity, auditorium)

### Subjects:
- Computer Science: Data Structures, Database Systems, Operating Systems, etc.
- Electrical Engineering: Circuit Analysis, Digital Electronics, Power Systems, etc.

### Faculty:
- Dr. John Smith (Computer Science)
- Prof. Sarah Johnson (Computer Science)
- Dr. Michael Brown (Computer Science)
- Prof. Emily Davis (Electrical Engineering)
- Dr. Robert Wilson (Electrical Engineering)

### Batches:
- CS-2022-A (Semester 3)
- CS-2021-A (Semester 5)
- CS-2020-A (Semester 7)
- EE-2022-A (Semester 3)
- EE-2021-A (Semester 5)
- EE-2020-A (Semester 7)

## Troubleshooting

### Connection Issues
1. Ensure PostgreSQL service is running
2. Check database credentials in `.env`
3. Verify database exists and user has permissions

### Migration Issues
1. Run `python setup_database.py` to recreate tables
2. Check PostgreSQL logs for detailed error messages
3. Ensure all dependencies are installed

### Performance
- PostgreSQL provides better performance for concurrent users
- Supports advanced indexing and query optimization
- Better suited for production environments

## Production Deployment

### Environment Variables
```env
DATABASE_URL=postgresql://username:password@hostname:port/database_name
SECRET_KEY=generate-a-strong-secret-key
FLASK_ENV=production
```

### Security Considerations
- Use strong database passwords
- Enable SSL connections in production
- Regularly backup the database
- Use environment-specific configuration files

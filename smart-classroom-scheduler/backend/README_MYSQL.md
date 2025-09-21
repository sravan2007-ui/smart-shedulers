# MySQL Database Setup Guide

## Overview
The Smart Classroom Scheduler has been configured to use MySQL database for better performance and production readiness.

## Prerequisites

### 1. Install MySQL Server
- Download and install MySQL Server from https://dev.mysql.com/downloads/mysql/
- During installation, set a root password (remember this password)
- Default port is 3306

### 2. Create Database
```sql
-- Connect to MySQL as root user
mysql -u root -p

-- Create database
CREATE DATABASE smart_classroom_scheduler;

-- Create user (optional)s
CREATE USER 'scheduler_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smart_classroom_scheduler.* TO 'scheduler_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Update Environment Variables
Edit the `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/smart_classroom_scheduler
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_classroom_scheduler
DB_USER=root
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

## Key Changes for MySQL

### 1. Database Driver
- **Old**: `psycopg2-binary` (PostgreSQL)
- **New**: `PyMySQL` (MySQL)

### 2. Connection String
- **Format**: `mysql+pymysql://username:password@host:port/database`
- **Example**: `mysql+pymysql://root:password@localhost:3306/smart_classroom_scheduler`

### 3. MySQL Specific Features
- Uses InnoDB engine for ACID compliance
- Supports foreign key constraints
- UTF-8 character encoding
- Auto-increment primary keys

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
1. Ensure MySQL service is running
2. Check database credentials in `.env`
3. Verify database exists and user has permissions
4. Test connection: `mysql -u root -p`

### Common MySQL Errors
1. **Access denied**: Check username/password
2. **Database doesn't exist**: Run `CREATE DATABASE smart_classroom_scheduler;`
3. **Connection refused**: Ensure MySQL server is running
4. **Port issues**: Default MySQL port is 3306

### Performance Optimization
- MySQL provides excellent performance for read-heavy workloads
- Supports indexing for faster queries
- Connection pooling available
- Better suited for production environments

## Production Deployment

### Environment Variables
```env
DATABASE_URL=mysql+pymysql://username:password@hostname:port/database_name
SECRET_KEY=generate-a-strong-secret-key
FLASK_ENV=production
```

### Security Considerations
- Use strong database passwords
- Enable SSL connections in production
- Regularly backup the database
- Use environment-specific configuration files
- Consider using MySQL user with limited privileges instead of root

## MySQL vs SQLite vs PostgreSQL

### MySQL Advantages:
- Excellent performance and scalability
- Wide industry adoption
- Great tooling and community support
- ACID compliance with InnoDB
- Replication and clustering support

### When to Use:
- Production web applications
- High-traffic websites
- Applications requiring high availability
- Multi-user environments
- When you need proven reliability

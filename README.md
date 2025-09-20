# Smart Classroom & Timetable Scheduler

A comprehensive web-based platform for automated timetable generation and classroom management in higher education institutions. This system addresses the challenges of manual timetable preparation by providing intelligent scheduling solutions that optimize resource utilization and minimize conflicts.

## 🎯 Features

### Core Functionality
- **Automated Timetable Generation**: AI-powered optimization algorithm that generates multiple timetable options
- **Multi-Parameter Optimization**: Considers classrooms, faculty workload, student batches, and subject requirements
- **Conflict Resolution**: Automatically detects and resolves scheduling conflicts
- **Resource Optimization**: Maximizes classroom utilization and balances faculty workload

### Management Modules
- **Classroom Management**: Add, edit, and manage classroom details including capacity and equipment
- **Subject Management**: Configure subjects with credits, weekly classes, and lab requirements
- **Faculty Management**: Manage faculty profiles with workload constraints and availability
- **Batch Management**: Organize student batches by department, semester, and shift
- **Timetable Management**: Create, review, and approve generated timetables

### Advanced Features
- **Multiple Optimization Options**: Generate 3+ optimized timetable variants to choose from
- **Fixed Slot Support**: Accommodate special classes with predetermined time slots
- **Multi-Department Support**: Handle scheduling across different departments
- **Multi-Shift Scheduling**: Support for morning, afternoon, and evening shifts
- **Review & Approval Workflow**: Built-in approval process for competent authorities

## 🏗️ Architecture

### Backend (Python Flask)
- **Framework**: Flask with SQLite database
- **Optimization Engine**: Custom algorithm considering multiple constraints
- **API Design**: RESTful APIs for all CRUD operations
- **Authentication**: Session-based user authentication

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Bootstrap 5 with custom CSS
- **Interactive UI**: jQuery-powered dynamic interactions
- **Modern Interface**: Clean, intuitive design with smooth animations
- **Real-time Updates**: AJAX-based operations without page refreshes

### Database Schema
- **Users**: Authentication and role management
- **Classrooms**: Room details, capacity, and equipment
- **Subjects**: Course information and requirements
- **Faculty**: Staff profiles and constraints
- **Batches**: Student group organization
- **Timetables**: Generated schedules and entries
- **Fixed Slots**: Predetermined time allocations

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd smart-classroom-scheduler
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Initialize Database**
   The database will be automatically created when you first run the application.

4. **Run the Application**
   ```bash
   # From the backend directory
   python app.py
   
   # Or from the root directory
   python backend/app.py
   ```

5. **Access the Application**
   Open your web browser and navigate to: `http://localhost:5000`

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

## 📁 Project Structure

```
smart-classroom-scheduler/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── timetable_optimizer.py # Optimization algorithm
│   ├── requirements.txt       # Python dependencies
│   └── scheduler.db          # SQLite database (auto-created)
├── frontend/
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── manage_*.html     # Management interfaces
│   │   └── timetable_generator.html
│   └── static/
│       ├── css/
│       │   └── style.css     # Custom styles
│       └── js/
│           └── main.js       # JavaScript functionality
└── README.md
```

## 🎮 Usage Guide

### 1. Initial Setup
1. Login with admin credentials
2. Add classrooms with capacity and equipment details
3. Create subjects with semester and credit information
4. Add faculty members with workload constraints
5. Set up student batches by department and semester

### 2. Generating Timetables
1. Navigate to "Generate Timetable"
2. Select batch, semester, and academic year
3. Click "Generate Timetable Options"
4. Review multiple optimized options
5. Preview and select the best option
6. Save the timetable with a descriptive name

### 3. Managing Data
- Use the "Manage" dropdown to access different modules
- Add, edit, or delete entries as needed
- View statistics on the dashboard
- Monitor recent timetable activities

## 🔧 Key Parameters for Optimization

The system considers the following parameters when generating timetables:

### Infrastructure Constraints
- Number of available classrooms
- Classroom capacity and type (regular/lab/auditorium)
- Equipment requirements for subjects

### Academic Requirements
- Number of student batches
- Subjects per semester with credit hours
- Classes per week for each subject
- Laboratory session requirements

### Faculty Constraints
- Maximum hours per day (default: 6)
- Maximum hours per week (default: 20)
- Average leaves per month
- Subject expertise mapping

### Scheduling Rules
- Maximum classes per day per batch (default: 6)
- Fixed time slots for special classes
- Multi-shift support (morning/afternoon/evening)
- Conflict avoidance between resources

## 🎯 Optimization Algorithm

The timetable generator uses a sophisticated algorithm that:

1. **Analyzes Constraints**: Evaluates all scheduling constraints and requirements
2. **Generates Options**: Creates multiple feasible timetable configurations
3. **Scores Solutions**: Rates each option based on optimization criteria:
   - Even distribution of classes across days
   - Faculty workload balance
   - Classroom utilization efficiency
   - Conflict minimization
4. **Ranks Results**: Presents options sorted by optimization score
5. **Allows Selection**: Enables users to choose the best-fit solution

## 🔒 Security Features

- Session-based authentication
- Input validation and sanitization
- SQL injection prevention
- XSS protection through template escaping
- Role-based access control ready

## 🌟 Benefits

### For Administrators
- **Time Saving**: Automated generation reduces manual effort by 90%
- **Conflict Reduction**: Intelligent algorithm minimizes scheduling conflicts
- **Resource Optimization**: Better utilization of classrooms and faculty
- **Flexibility**: Easy modifications and multiple options to choose from

### For Faculty
- **Balanced Workload**: Even distribution of teaching hours
- **Predictable Schedule**: Clear visibility of weekly commitments
- **Reduced Conflicts**: Minimal overlapping assignments

### For Students
- **Optimized Learning**: Well-distributed class schedules
- **Reduced Gaps**: Efficient use of daily time slots
- **Consistent Routine**: Predictable weekly patterns

## 🔄 Future Enhancements

- **Mobile Application**: Native mobile app for on-the-go access
- **Calendar Integration**: Sync with Google Calendar, Outlook
- **Notification System**: Email/SMS alerts for schedule changes
- **Advanced Analytics**: Detailed reports and insights
- **Multi-Language Support**: Localization for different regions
- **API Integration**: Connect with existing college management systems

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure the backend directory is writable
   - Check if SQLite is properly installed

2. **Module Import Error**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Port Already in Use**
   - Change the port in `app.py`: `app.run(port=5001)`
   - Or kill the process using the port

4. **Static Files Not Loading**
   - Ensure the frontend folder structure is correct
   - Check file permissions

### Getting Help
- Check the browser console for JavaScript errors
- Review the Flask application logs
- Ensure all file paths are correct

## 📄 License

This project is developed for educational and institutional use. Feel free to modify and adapt according to your institution's requirements.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve the system.

---

**Smart Classroom & Timetable Scheduler** - Revolutionizing academic scheduling through intelligent automation.

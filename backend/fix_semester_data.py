from app import app, db
from models import Subject

def fix_data():
    with app.app_context():
        print("Starting data fix...")
        
        # Update all CSE subjects that have missing semester to Semester 4
        subjects = Subject.query.filter_by(department="CSE", semester=None).all()
        for s in subjects:
            s.semester = 4
            print(f"Updated {s.name} ({s.code}) -> Sem 4")
        
        db.session.commit()
        print("Data fix completed!")

if __name__ == "__main__":
    fix_data()

from backend.app import app, db, Classroom
import traceback

def verify_column():
    print("Verifying created_by column exists...")
    with app.app_context():
        try:
            # Try to filter by created_by. If column is missing in DB or Model, this explodes.
            count = Classroom.query.filter_by(created_by=1).count()
            print(f"✅ Success! Query matched {count} classrooms for user 1.")
            
            # Check if model has the field
            if hasattr(Classroom, 'created_by'):
                 print("✅ Model has created_by field.")
            else:
                 print("❌ Model MISSING created_by field.")

        except Exception as e:
            print(f"❌ Verification Error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    verify_column()

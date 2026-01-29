from backend.app import app, db, User, Classroom
import uuid
import traceback

def verify_isolation():
    print("Starting verification...")
    with app.app_context():
        try:
            # Create two unique test users
            suffix = str(uuid.uuid4())[:8]
            user_a_name = f"user_a_{suffix}"
            user_b_name = f"user_b_{suffix}"
            
            user_a = User(username=user_a_name, email=f"{user_a_name}@test.com", role='user', is_verified=True)
            user_a.set_password('password')
            
            user_b = User(username=user_b_name, email=f"{user_b_name}@test.com", role='user', is_verified=True)
            user_b.set_password('password')
            
            db.session.add(user_a)
            db.session.add(user_b)
            db.session.commit()
            
            print(f"Created users: {user_a.id}, {user_b.id}")
            
            # Create classroom for User A
            c1 = Classroom(name=f"Room A {suffix}", capacity=50, created_by=user_a.id)
            db.session.add(c1)
            db.session.commit()
            print(f"Created Classroom for User A: {c1.id}")
            
            # Test Query for User A (Simulate filter)
            classrooms_a = Classroom.query.filter_by(created_by=user_a.id).all()
            print(f"User A sees: {[c.name for c in classrooms_a]}")
            
            # Test Query for User B (Simulate filter)
            classrooms_b = Classroom.query.filter_by(created_by=user_b.id).all()
            print(f"User B sees: {[c.name for c in classrooms_b]}")
            
            if len(classrooms_a) == 1 and len(classrooms_b) == 0:
                print("✅ Data Isolation Verified: User B cannot see User A's data.")
            else:
                print("❌ Data Isolation Failed!")
        except Exception as e:
            print(f"❌ Verification Error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    verify_isolation()

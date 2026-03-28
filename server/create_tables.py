from app import app, db
from models import User, InterviewSession, Question, Answer, InterviewFeedback

if __name__ == "__main__":
    with app.app_context():
        print("Creating tables...")
        try:
            db.create_all()
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

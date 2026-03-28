from app import app, db
from sqlalchemy import text

try:
    with app.app_context():
        print("Testing DB connection...")
        db.session.execute(text('SELECT 1'))
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")

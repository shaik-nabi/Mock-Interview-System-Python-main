import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

# Parse the URI slightly or just hardcode for creation
# URI: mysql+pymysql://root:password@localhost/mock_interview_db
# DB Name: mock_interview_db

DB_NAME = 'mock_interview_db'
DB_USER = 'root'
DB_PASSWORD = 'Nabi@168400'
DB_HOST = 'localhost'

try:
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database {DB_NAME} created (or already exists).")
    conn.close()
except Exception as e:
    print(f"Error creating database: {e}")


import pymysql

DB_NAME = 'mock_interview_db'
DB_USER = 'root'
DB_PASSWORD = 'Nabi@168400'
DB_HOST = 'localhost'

try:
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"Database {DB_NAME} reset successfully.")
    conn.close()
except Exception as e:
    print(f"Error resetting database: {e}")

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_signup():
    print("Testing Signup...")
    url = f"{BASE_URL}/auth/signup"
    data = {"name": "Test User", "email": "test@example.com", "password": "Password123!"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [201, 400] # 400 if already exists

def test_login():
    print("\nTesting Login...")
    url = f"{BASE_URL}/auth/login"
    data = {"email": "test@example.com", "password": "Password123!"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        return response.json().get('user', {}).get('id')
    return None

def test_start_interview(user_id):
    print("\nTesting Start Interview...")
    url = f"{BASE_URL}/api/start-interview"
    data = {"user_id": user_id, "job_role": "Python Developer", "experience_level": "Junior"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 201:
        return response.json().get('session', {}).get('id')
    return None

def test_get_questions(session_id):
    print("\nTesting Get Questions...")
    url = f"{BASE_URL}/api/get-questions"
    data = {"job_role": "Python Developer", "experience_lvl": "Junior", "session_id": session_id}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    # print(f"Response: {response.json()}") # Might be long
    return response.status_code == 200

def test_save_answer(session_id):
    print("\nTesting Save Answer...")
    url = f"{BASE_URL}/api/save-answer"
    data = {
        "session_id": session_id,
        "question_text": "What is Python?",
        "answer_text": "Python is a programming language."
    }
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 201

def test_history(user_id):
    print("\nTesting History...")
    url = f"{BASE_URL}/api/history"
    response = requests.get(url, params={"user_id": user_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    # Ensure server is running separately!
    print("Ensure the Flask server is running in another terminal!")
    
    signup_ok = test_signup()
    user_id = test_login()
    
    if user_id:
        session_id = test_start_interview(user_id)
        if session_id:
            test_get_questions(session_id)
            test_save_answer(session_id)
        test_history(user_id)
    else:
        print("Login failed, skipping authenticated tests.")

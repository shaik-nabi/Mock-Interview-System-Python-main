
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_signup_invalid_password():
    print("Testing signup with invalid password...")
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "password" # too short, no special char, etc.
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=data)
        if response.status_code == 400:
            print("PASS: Signup failed as expected.")
        else:
            print(f"FAIL: Signup unexpectedly succeeded or returned wrong status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAIL: Request failed: {e}")

def test_signup_valid():
    print("Testing signup with valid password...")
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "Password123!" # Valid
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=data)
        if response.status_code == 201:
            print("PASS: Signup succeeded.")
            return True
        elif response.status_code == 400 and "Email already exists" in response.text:
             print("PASS: Signup handled existing email.")
             return True
        else:
            print(f"FAIL: Signup failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Request failed - is the server running? {e}")
        return False

def test_login_valid():
    print("Testing login with valid credentials...")
    data = {
        "email": "test@example.com",
        "password": "Password123!"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        if response.status_code == 200:
            user = response.json().get('user')
            if user and user.get('first_name') == 'Test':
                print("PASS: Login succeeded and returned correct user.")
            else:
                 print(f"FAIL: Login succeeded but returned wrong user data: {response.text}")
        else:
            print(f"FAIL: Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAIL: Request failed: {e}")

if __name__ == "__main__":
    test_signup_invalid_password()
    if test_signup_valid():
        test_login_valid()

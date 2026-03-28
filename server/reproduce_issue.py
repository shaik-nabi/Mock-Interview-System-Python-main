import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def reproduce_frontend_request():
    print("Attempting to reproduce frontend request...")
    url = f"{BASE_URL}/api/get-questions"
    data = {"job_role": "python developer", "experience_lvl": "fresher"}
    
    try:
        response = requests.post(url, json=data)
        with open("error_log.txt", "w") as f:
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")
        print("Response written to error_log.txt")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    reproduce_frontend_request()

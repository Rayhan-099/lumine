import requests
import json
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("--- Starting API Tests ---")
    
    # 1. Register
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    print(f"Registering user {email}...")
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    
    if reg_res.status_code != 200:
        print("Registration failed:", reg_res.text)
        sys.exit(1)
    print("Registration passed")

    # 2. Login
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if login_res.status_code != 200:
        print("Login failed:", login_res.text)
        sys.exit(1)
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login passed")
    
    # 3. Analyze Endpoint (with text only first, to see graceful handling without image)
    print("Testing Analyze endpoint...")
    analyze_res = requests.post(
        f"{BASE_URL}/analyze/",
        headers=headers,
        data={"description": "I have some red acne on my face."}
    )
    
    if analyze_res.status_code != 200:
        print("Analyze failed:", analyze_res.text)
        sys.exit(1)
        
    analyze_data = analyze_res.json()
    print("Analyze response:", json.dumps(analyze_data, indent=2))
    print("Analyze passed")
    
    # 4. History Retrieval
    print("Testing History endpoint...")
    history_res = requests.get(f"{BASE_URL}/history", headers=headers)
    
    if history_res.status_code != 200:
        print("History failed:", history_res.text)
        sys.exit(1)
        
    history_data = history_res.json()
    if len(history_data) == 0:
        print("History passed but is empty!")
        sys.exit(1)
        
    print(f"History passed. Found {len(history_data)} records.")
    
    print("--- All API Tests Passed ---")

if __name__ == "__main__":
    run_tests()

#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_company_profile():
    # First login to get a token
    login_data = {
        "username_or_email": "acme_hr",  # Company user from seed
        "password": "pass1234"
    }
    
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Login successful, token: {token[:20]}...")
    
    # Test company profile endpoint
    company_user_id = 1  # First company from our debug
    print(f"\nTesting company profile endpoint for user {company_user_id}...")
    response = requests.get(f"{BASE_URL}/profiles/companies/{company_user_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        print("Company profile data:")
        print(json.dumps(profile_data, indent=2))
        
        # Check if required fields are present
        required_fields = ["username", "bio", "companyBio", "profileImageUrl"]
        missing_fields = [field for field in required_fields if field not in profile_data or profile_data[field] is None]
        
        if missing_fields:
            print(f"\n❌ Missing fields: {missing_fields}")
        else:
            print(f"\n✅ All required fields are present!")
            
    else:
        print(f"Error: {response.text}")
    
    # Test student profile for comparison
    print(f"\n--- Comparison with student profile ---")
    student_user_id = 11  # Student user from seed
    response = requests.get(f"{BASE_URL}/profiles/students/{student_user_id}", headers=headers)
    print(f"Student profile status: {response.status_code}")
    if response.status_code == 200:
        student_data = response.json()
        print("Student profile keys:", list(student_data.keys()))

if __name__ == "__main__":
    test_company_profile()
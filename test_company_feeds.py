#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_company_data_in_feeds():
    # Login as student to test the student feed (which shows company posts)
    login_data = {
        "username_or_email": "eleni",  # Student user from seed
        "password": "pass1234"
    }
    
    print("Logging in as student...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Login successful!")
    
    # Test student feed (shows company posts)
    print(f"\nTesting student feed (company posts)...")
    response = requests.get(f"{BASE_URL}/feed/student", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        feed_data = response.json()
        print(f"Found {len(feed_data)} posts in student feed")
        
        if feed_data:
            first_post = feed_data[0]
            print("\nFirst post company data:")
            company_fields = {
                "companyUserId": first_post.get("companyUserId"),
                "companyName": first_post.get("companyName"), 
                "username": first_post.get("username"),
                "bio": first_post.get("bio"),
                "companyBio": first_post.get("companyBio"),
                "profileImageUrl": first_post.get("profileImageUrl"),
                "companyProfileImageUrl": first_post.get("companyProfileImageUrl")
            }
            print(json.dumps(company_fields, indent=2))
            
            # Check if required fields are present
            required_fields = ["username", "bio", "companyBio", "profileImageUrl"]
            missing_fields = [field for field in required_fields if field not in first_post or first_post[field] is None]
            
            if missing_fields:
                print(f"\n❌ Missing fields in posts: {missing_fields}")
            else:
                print(f"\n✅ All required fields are present in posts!")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_company_data_in_feeds()
#!/usr/bin/env python3

from app.db import SessionLocal
from app.models import User, UserRole
from app.auth import create_access_token
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def direct_feed_test():
    # Get a student user ID from database
    db = SessionLocal()
    try:
        student = db.query(User).filter(User.role == UserRole.STUDENT).first()
        if not student:
            print("No student found!")
            return
            
        print(f"Found student: {student.username} (ID: {student.id})")
        
        # Create a token for this student
        token = create_access_token(student.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Testing student feed...")
        response = requests.get(f"{BASE_URL}/feed/student", headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} posts")
            if data:
                post = data[0]
                print("First post company fields:")
                company_fields = ["companyUserId", "companyName", "username", "bio", "companyBio", "profileImageUrl", "companyProfileImageUrl"]
                for field in company_fields:
                    print(f"  {field}: {post.get(field, 'MISSING')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    direct_feed_test()
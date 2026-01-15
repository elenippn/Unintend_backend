#!/usr/bin/env python3

from app.db import SessionLocal
from app.models import User, UserRole
from app.auth import create_access_token
import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_chat_with_profile_images():
    db = SessionLocal()
    try:
        # Get a student user
        student = db.query(User).filter(User.role == UserRole.STUDENT).first()
        if not student:
            print("No student found!")
            return
            
        print(f"Testing with student: {student.username} (ID: {student.id})")
        
        # Create a token for this student
        token = create_access_token(student.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\nTesting applications list (conversations list)...")
        response = requests.get(f"{BASE_URL}/applications", headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} applications")
            if data:
                app = data[0]
                print("\nFirst application:")
                print(f"  Application ID: {app.get('applicationId')}")
                print(f"  Other party name: {app.get('otherPartyName')}")
                print(f"  Other party profile image: {app.get('otherPartyProfileImageUrl', 'MISSING')}")
                print(f"  Last message: {app.get('lastMessage', 'No messages')}")
                
                # Test messages for this conversation
                conversation_id = app.get('conversationId')
                if conversation_id:
                    print(f"\nTesting messages for conversation {conversation_id}...")
                    response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages", headers=headers)
                    if response.status_code == 200:
                        messages = response.json()
                        print(f"Found {len(messages)} messages")
                        if messages:
                            msg = messages[0]
                            print("\nFirst message:")
                            print(f"  Text: {msg.get('text', '')}")
                            print(f"  From company: {msg.get('fromCompany', False)}")
                            print(f"  Is system: {msg.get('isSystem', False)}")
                            print(f"  Sender name: {msg.get('senderName', 'MISSING')}")
                            print(f"  Sender profile image: {msg.get('senderProfileImageUrl', 'MISSING')}")
                    else:
                        print(f"Messages error: {response.status_code}")
        else:
            print(f"Applications error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_chat_with_profile_images()
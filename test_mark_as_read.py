"""
Test script για mark as read functionality.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionLocal
from app.models import User, UserRole, Application, Conversation, Message, MessageType
from datetime import datetime


def test_mark_as_read():
    """Test the mark as read logic."""
    print("=" * 60)
    print("Testing Mark as Read Functionality")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Get a conversation
        conv = db.query(Conversation).first()
        if not conv:
            print("[FAIL] No conversations found. Run seed or test_matching_flow first.")
            return
        
        app = db.get(Application, conv.application_id)
        if not app:
            print("[FAIL] No application found for conversation")
            return
        
        print(f"Conversation ID: {conv.id}")
        print(f"Application ID: {app.id}")
        print(f"Student: {app.student_user_id}")
        print(f"Company: {app.company_user_id}")
        print()
        
        # Get messages
        messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
        print(f"Messages in conversation: {len(messages)}")
        for i, msg in enumerate(messages):
            sender = 'SYSTEM' if msg.type == MessageType.SYSTEM else f'User {msg.sender_user_id}'
            print(f"  {i+1}. [{sender}] {msg.text[:50]}...")
        print()
        
        # Simulate: Check unread count for student BEFORE mark as read
        from app.routers.chat_routes import _unread_count, _ensure_participant
        
        # Ensure participant exists
        part = _ensure_participant(
            db,
            conversation_id=conv.id,
            user_id=app.student_user_id,
            seed_last_read_to_last_message=False  # Don't auto-mark
        )
        
        # Count unread (assuming student hasn't read any)
        part.last_read_message_id = None  # Reset to simulate fresh user
        db.flush()
        
        unread_before = _unread_count(
            db,
            conversation_id=conv.id,
            user_id=app.student_user_id,
            last_read_message_id=part.last_read_message_id
        )
        
        print(f"[BEFORE] Student unread count: {unread_before}")
        print()
        
        # Simulate: Mark as read
        from sqlalchemy import func
        last_msg_id = (
            db.query(func.max(Message.id))
            .filter(Message.conversation_id == conv.id)
            .scalar()
        )
        
        part.last_read_message_id = last_msg_id
        part.updated_at = datetime.utcnow()
        db.commit()
        
        # Check unread count AFTER
        unread_after = _unread_count(
            db,
            conversation_id=conv.id,
            user_id=app.student_user_id,
            last_read_message_id=part.last_read_message_id
        )
        
        print(f"[AFTER] Student unread count: {unread_after}")
        print()
        
        # Verify
        if unread_after == 0:
            print("[OK] Mark as read works correctly!")
            print("[OK] Unread count went from {} to 0".format(unread_before))
        else:
            print("[FAIL] Unread count should be 0, got {}".format(unread_after))
        
        print()
        print("=" * 60)
        print("Test Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_mark_as_read()

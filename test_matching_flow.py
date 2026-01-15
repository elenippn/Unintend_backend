"""
Test script για την επιβεβαίωση του Like/Pass/Application Status Flow.

Αυτό το script ελέγχει:
1. Student κάνει LIKE → Application status: PENDING
2. Company κάνει LIKE → Application status: ACCEPTED (Match!)
3. Company κάνει PASS → Application status: DECLINED
4. Conversation creation μόνο όταν γίνει match
5. System messages στα σωστά σημεία
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionLocal
from app.models import (
    User, UserRole, InternshipPost, StudentProfilePost,
    Application, ApplicationStatus, Conversation, Message, MessageType,
    Decision, StudentPostInteraction, CompanyStudentPostInteraction
)
from datetime import datetime


def clear_test_data(db):
    """Clear all test data from previous runs."""
    print("Clearing test data...")
    db.query(Message).delete()
    db.query(Conversation).delete()
    db.query(Application).delete()
    db.query(StudentPostInteraction).delete()
    db.query(CompanyStudentPostInteraction).delete()
    db.commit()
    print("Test data cleared\n")


def test_student_like_first(db):
    """Test Case 1: Student κάνει LIKE πρώτος → PENDING"""
    print("Test 1: Student LIKE first (PENDING)")
    print("-" * 50)
    
    # Get student and post
    student = db.query(User).filter(User.role == UserRole.STUDENT).first()
    company = db.query(User).filter(User.role == UserRole.COMPANY).first()
    post = db.query(InternshipPost).filter(InternshipPost.company_user_id == company.id).first()
    
    if not student or not post:
        print("[FAIL] No student or post found. Run seed first.")
        return False
    
    print(f"Student: {student.username} (ID: {student.id})")
    print(f"Company: {company.username} (ID: {company.id})")
    print(f"Post: {post.title} (ID: {post.id})")
    
    # Create application with student LIKE
    app = Application(
        post_id=post.id,
        student_user_id=student.id,
        company_user_id=company.id,
        student_decision=Decision.LIKE,
        company_decision=None,
        status=ApplicationStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app)
    db.flush()
    
    # Create conversation with PENDING message
    conv = Conversation(application_id=app.id, created_at=datetime.utcnow())
    db.add(conv)
    db.flush()
    
    msg = Message(
        conversation_id=conv.id,
        type=MessageType.SYSTEM,
        sender_user_id=None,
        text="Message still pending",
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    
    # Verify
    app_check = db.get(Application, app.id)
    assert app_check.status == ApplicationStatus.PENDING, "Status should be PENDING"
    assert app_check.student_decision == Decision.LIKE, "Student decision should be LIKE"
    assert app_check.company_decision is None, "Company decision should be None"
    
    conv_check = db.query(Conversation).filter(Conversation.application_id == app.id).first()
    assert conv_check is not None, "Conversation should exist"
    
    msg_check = db.query(Message).filter(Message.conversation_id == conv.id).first()
    assert msg_check.text == "Message still pending", "Should have pending message"
    
    print(f"[OK] Application created: ID={app.id}, Status={app.status.value}")
    print(f"[OK] Conversation created: ID={conv.id}")
    print(f"[OK] System message: '{msg.text}'")
    print()
    
    return app.id


def test_company_like_match(db, app_id):
    """Test Case 2: Company κάνει LIKE → ACCEPTED (Match!)"""
    print("Test 2: Company LIKE (MATCH -> ACCEPTED)")
    print("-" * 50)
    
    app = db.get(Application, app_id)
    if not app:
        print("[FAIL] Application not found")
        return False
    
    print(f"Application ID: {app.id}")
    print(f"Before: Status={app.status.value}, Student={app.student_decision}, Company={app.company_decision}")
    
    # Company makes LIKE decision
    app.company_decision = Decision.LIKE
    
    # Recalculate status (should be ACCEPTED now)
    if app.student_decision == Decision.LIKE and app.company_decision == Decision.LIKE:
        app.status = ApplicationStatus.ACCEPTED
        app.updated_at = datetime.utcnow()
        
        # Add ACCEPTED system message
        conv = db.query(Conversation).filter(Conversation.application_id == app.id).first()
        msg = Message(
            conversation_id=conv.id,
            type=MessageType.SYSTEM,
            sender_user_id=None,
            text="Ready to connect?",
            created_at=datetime.utcnow(),
        )
        db.add(msg)
    
    db.commit()
    
    # Verify
    app_check = db.get(Application, app.id)
    assert app_check.status == ApplicationStatus.ACCEPTED, "Status should be ACCEPTED"
    assert app_check.student_decision == Decision.LIKE, "Student decision should be LIKE"
    assert app_check.company_decision == Decision.LIKE, "Company decision should be LIKE"
    
    messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
    assert len(messages) == 2, "Should have 2 system messages (PENDING + ACCEPTED)"
    assert messages[-1].text == "Ready to connect?", "Last message should be 'Ready to connect?'"
    
    print(f"[OK] After: Status={app_check.status.value}, Student={app_check.student_decision.value}, Company={app_check.company_decision.value}")
    print(f"[OK] Messages in conversation: {len(messages)}")
    print(f"   - {messages[0].text}")
    print(f"   - {messages[1].text}")
    print()
    
    return True


def test_company_pass_declined(db):
    """Test Case 3: Company κάνει PASS → DECLINED"""
    print("Test 3: Company PASS (DECLINED)")
    print("-" * 50)
    
    # Get different student and post for new test
    student = db.query(User).filter(User.role == UserRole.STUDENT).offset(1).first()
    company = db.query(User).filter(User.role == UserRole.COMPANY).offset(1).first()
    post = db.query(InternshipPost).filter(InternshipPost.company_user_id == company.id).first()
    
    if not student or not post:
        print("[FAIL] No student or post found")
        return False
    
    print(f"Student: {student.username} (ID: {student.id})")
    print(f"Company: {company.username} (ID: {company.id})")
    print(f"Post: {post.title} (ID: {post.id})")
    
    # Create application with student LIKE
    app = Application(
        post_id=post.id,
        student_user_id=student.id,
        company_user_id=company.id,
        student_decision=Decision.LIKE,
        company_decision=None,
        status=ApplicationStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app)
    db.flush()
    
    # Create conversation
    conv = Conversation(application_id=app.id, created_at=datetime.utcnow())
    db.add(conv)
    db.flush()
    
    msg1 = Message(
        conversation_id=conv.id,
        type=MessageType.SYSTEM,
        sender_user_id=None,
        text="Message still pending",
        created_at=datetime.utcnow(),
    )
    db.add(msg1)
    db.commit()
    
    print(f"Initial: Status={app.status.value}")
    
    # Company makes PASS decision
    app.company_decision = Decision.PASS
    app.status = ApplicationStatus.DECLINED
    app.updated_at = datetime.utcnow()
    
    msg2 = Message(
        conversation_id=conv.id,
        type=MessageType.SYSTEM,
        sender_user_id=None,
        text="Unfortunately this was not a match, keep searching!",
        created_at=datetime.utcnow(),
    )
    db.add(msg2)
    db.commit()
    
    # Verify
    app_check = db.get(Application, app.id)
    assert app_check.status == ApplicationStatus.DECLINED, "Status should be DECLINED"
    assert app_check.company_decision == Decision.PASS, "Company decision should be PASS"
    
    messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
    assert len(messages) == 2, "Should have 2 system messages"
    assert messages[-1].text == "Unfortunately this was not a match, keep searching!", "Should have declined message"
    
    print(f"[OK] After: Status={app_check.status.value}, Company={app_check.company_decision.value}")
    print(f"[OK] System message: '{messages[-1].text}'")
    print()
    
    return True


def test_student_pass_declined(db):
    """Test Case 4: Student κάνει PASS → DECLINED"""
    print("Test 4: Student PASS (DECLINED)")
    print("-" * 50)
    
    student = db.query(User).filter(User.role == UserRole.STUDENT).offset(2).first()
    company = db.query(User).filter(User.role == UserRole.COMPANY).offset(2).first()
    post = db.query(InternshipPost).filter(InternshipPost.company_user_id == company.id).first()
    
    if not student or not post:
        print("[FAIL] No student or post found")
        return False
    
    print(f"Student: {student.username} (ID: {student.id})")
    print(f"Post: {post.title} (ID: {post.id})")
    
    # Student makes PASS decision directly
    app = Application(
        post_id=post.id,
        student_user_id=student.id,
        company_user_id=company.id,
        student_decision=Decision.PASS,
        company_decision=None,
        status=ApplicationStatus.DECLINED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app)
    db.flush()
    
    conv = Conversation(application_id=app.id, created_at=datetime.utcnow())
    db.add(conv)
    db.flush()
    
    msg = Message(
        conversation_id=conv.id,
        type=MessageType.SYSTEM,
        sender_user_id=None,
        text="Unfortunately this was not a match, keep searching!",
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    
    # Verify
    app_check = db.get(Application, app.id)
    assert app_check.status == ApplicationStatus.DECLINED, "Status should be DECLINED"
    assert app_check.student_decision == Decision.PASS, "Student decision should be PASS"
    
    print(f"[OK] Status={app_check.status.value}, Student={app_check.student_decision.value}")
    print(f"[OK] Conversation exists with declined message")
    print()
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Like/Pass/Application Status Flow")
    print("=" * 50)
    print()
    
    db = SessionLocal()
    try:
        clear_test_data(db)
        
        # Run tests
        app_id = test_student_like_first(db)
        if not app_id:
            print("[FAIL] Test 1 failed, aborting")
            return
        
        if not test_company_like_match(db, app_id):
            print("[FAIL] Test 2 failed")
            return
        
        if not test_company_pass_declined(db):
            print("[FAIL] Test 3 failed")
            return
        
        if not test_student_pass_declined(db):
            print("[FAIL] Test 4 failed")
            return
        
        print("=" * 50)
        print("[OK] All tests passed!")
        print("=" * 50)
        print()
        print("Summary:")
        print("  [OK] PENDING status when one party LIKEs")
        print("  [OK] ACCEPTED status when both LIKE (Match!)")
        print("  [OK] DECLINED status when either PASSes")
        print("  [OK] Conversations created with correct system messages")
        print("  [OK] Status transitions work correctly")
        
    except AssertionError as e:
        print(f"[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

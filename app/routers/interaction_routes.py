from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models import (
    UserRole, Decision,
    StudentPostInteraction,
    InternshipPost, Application, ApplicationStatus,
    Conversation, Message, MessageType,
    StudentProfilePost,
    CompanyStudentPostInteraction,
    ConversationParticipant,
)
from ..schemas import StudentDecisionRequest, CompanyDecisionStudentPostRequest, CompanyDecisionStudentRequest

router = APIRouter(prefix="", tags=["interactions"])


PENDING_TEXT = "Message still pending"
ACCEPTED_TEXT = "Ready to connect?"
DECLINED_TEXT = "Unfortunately this was not a match, keep searching!"


def calculate_application_status(student_decision: Decision | None, company_decision: Decision | None) -> ApplicationStatus:
    """
    Calculate the application status based on both parties' decisions.
    
    Logic:
    - Both LIKE → ACCEPTED (Match!)
    - Either PASS → DECLINED (No match)
    - One LIKE, other None → PENDING (Waiting for response)
    - Both None → PENDING (Initial state)
    """
    if student_decision == Decision.LIKE and company_decision == Decision.LIKE:
        return ApplicationStatus.ACCEPTED
    
    if student_decision == Decision.PASS or company_decision == Decision.PASS:
        return ApplicationStatus.DECLINED
    
    if (student_decision == Decision.LIKE and company_decision is None) or \
       (company_decision == Decision.LIKE and student_decision is None):
        return ApplicationStatus.PENDING
    
    return ApplicationStatus.PENDING


def get_or_create_application(
    db: Session,
    student_id: int,
    company_id: int,
    post_id: int,
) -> Application:
    """Get existing application or create new one."""
    app = (
        db.query(Application)
        .filter(
            Application.post_id == post_id,
            Application.student_user_id == student_id
        )
        .first()
    )
    
    if not app:
        app = Application(
            post_id=post_id,
            student_user_id=student_id,
            company_user_id=company_id,
            student_decision=None,
            company_decision=None,
            status=ApplicationStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(app)
        db.flush()
    
    return app


def update_application_and_conversation(
    db: Session,
    app: Application,
    student_decision: Decision | None = None,
    company_decision: Decision | None = None,
) -> None:
    """
    Update application decisions and create/update conversation based on status.
    
    Conversation is created ONLY when status becomes ACCEPTED (both LIKE).
    """
    # Update decisions if provided
    if student_decision is not None:
        app.student_decision = student_decision
    if company_decision is not None:
        app.company_decision = company_decision
    
    # Calculate new status
    old_status = app.status
    new_status = calculate_application_status(app.student_decision, app.company_decision)
    app.status = new_status
    app.updated_at = datetime.utcnow()
    
    # Get or create conversation if it doesn't exist
    conv = db.query(Conversation).filter(Conversation.application_id == app.id).first()
    
    # Only create conversation when status changes or if it's the first action
    if old_status != new_status or not conv:
        if not conv:
            # Create conversation on first action
            conv = Conversation(application_id=app.id, created_at=datetime.utcnow())
            db.add(conv)
            db.flush()
            
            # Initialize participants with first system message
            system_text = PENDING_TEXT if new_status == ApplicationStatus.PENDING else \
                         ACCEPTED_TEXT if new_status == ApplicationStatus.ACCEPTED else \
                         DECLINED_TEXT
            
            msg = Message(
                conversation_id=conv.id,
                type=MessageType.SYSTEM,
                sender_user_id=None,
                text=system_text,
                created_at=datetime.utcnow(),
            )
            db.add(msg)
            db.flush()
            
            # Create participant entries
            for user_id in [app.student_user_id, app.company_user_id]:
                db.add(ConversationParticipant(
                    conversation_id=conv.id,
                    user_id=user_id,
                    last_read_message_id=msg.id,
                    updated_at=datetime.utcnow(),
                ))
        else:
            # Status changed - add system message
            if old_status != new_status:
                system_text = ACCEPTED_TEXT if new_status == ApplicationStatus.ACCEPTED else \
                             DECLINED_TEXT if new_status == ApplicationStatus.DECLINED else \
                             PENDING_TEXT
                
                msg = Message(
                    conversation_id=conv.id,
                    type=MessageType.SYSTEM,
                    sender_user_id=None,
                    text=system_text,
                    created_at=datetime.utcnow(),
                )
                db.add(msg)
    
    db.flush()


def ensure_student_interaction_row(db: Session, student_user_id: int, post_id: int) -> StudentPostInteraction:
    """Get or create student-post interaction row."""
    row = (
        db.query(StudentPostInteraction)
        .filter(
            StudentPostInteraction.student_user_id == student_user_id,
            StudentPostInteraction.post_id == post_id
        )
        .first()
    )
    if not row:
        row = StudentPostInteraction(
            student_user_id=student_user_id,
            post_id=post_id,
            decision=Decision.NONE,
        )
        db.add(row)
        db.flush()
    return row


def ensure_company_studentpost_interaction(
    db: Session,
    company_user_id: int,
    student_post_id: int
) -> CompanyStudentPostInteraction:
    """Get or create company-student post interaction row."""
    row = (
        db.query(CompanyStudentPostInteraction)
        .filter(
            CompanyStudentPostInteraction.company_user_id == company_user_id,
            CompanyStudentPostInteraction.student_post_id == student_post_id,
        )
        .first()
    )
    if not row:
        row = CompanyStudentPostInteraction(
            company_user_id=company_user_id,
            student_post_id=student_post_id,
            decision=Decision.NONE,
        )
        db.add(row)
        db.flush()
    return row


@router.post("/decisions/student/post")
def student_decision_post(
    req: StudentDecisionRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    """
    Student makes a LIKE or PASS decision on an internship post.
    
    Creates or updates Application with student_decision.
    Status becomes PENDING if LIKE (waiting for company).
    Status becomes DECLINED if PASS.
    """
    if current.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can decide on posts")

    post = db.get(InternshipPost, req.postId)
    if not post or not post.is_active:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update interaction tracking
    interaction = ensure_student_interaction_row(db, current.id, post.id)
    decision = Decision(req.decision)
    interaction.decision = decision
    interaction.decided_at = datetime.utcnow()
    
    # Get or create application
    app = get_or_create_application(db, current.id, post.company_user_id, post.id)
    
    # Update application with student's decision
    update_application_and_conversation(
        db,
        app,
        student_decision=decision,
        company_decision=app.company_decision,
    )

    db.commit()
    return {"ok": True}


@router.post("/decisions/company/student-post")
def company_decision_student_post(
    req: CompanyDecisionStudentPostRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    """
    Company makes a LIKE or PASS decision on a student profile post.
    
    If student has already LIKEd one of company's posts:
    - Company LIKE → Match! (ACCEPTED)
    - Company PASS → DECLINED
    
    If student hasn't acted yet:
    - Creates/updates Application with company_decision = LIKE/PASS
    - Status becomes PENDING (waiting for student) or DECLINED (if PASS)
    """
    if current.role != UserRole.COMPANY:
        raise HTTPException(status_code=403, detail="Only companies can decide on student posts")

    spost = db.get(StudentProfilePost, req.studentPostId)
    if not spost or not spost.is_active:
        raise HTTPException(status_code=404, detail="Student post not found")

    # Update interaction tracking
    interaction = ensure_company_studentpost_interaction(db, current.id, spost.id)
    decision = Decision(req.decision)
    interaction.decision = decision
    interaction.decided_at = datetime.utcnow()
    
    # Find if there's an existing application (student liked one of our posts)
    app = (
        db.query(Application)
        .filter(
            Application.company_user_id == current.id,
            Application.student_user_id == spost.student_user_id,
        )
        .order_by(Application.updated_at.desc())
        .first()
    )
    
    if app:
        # Update existing application with company decision
        update_application_and_conversation(
            db,
            app,
            student_decision=app.student_decision,
            company_decision=decision,
        )
    else:
        # No existing application - company acted first
        # Create application with company decision (waiting for student to like a post)
        # We need a post to link to - use the most recent active post from this company
        company_post = (
            db.query(InternshipPost)
            .filter(
                InternshipPost.company_user_id == current.id,
                InternshipPost.is_active == True
            )
            .order_by(InternshipPost.created_at.desc())
            .first()
        )
        
        if company_post:
            app = get_or_create_application(db, spost.student_user_id, current.id, company_post.id)
            update_application_and_conversation(
                db,
                app,
                student_decision=app.student_decision,
                company_decision=decision,
            )

    db.commit()
    return {"ok": True}


@router.post("/decisions/company/student")
def company_decision_student(
    req: CompanyDecisionStudentRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    """
    Company decides LIKE/PASS given a studentUserId; resolves the student's profile post.
    Convenience endpoint that finds the student's profile post automatically.
    """
    if current.role != UserRole.COMPANY:
        raise HTTPException(status_code=403, detail="Only companies can decide on students")

    spost = (
        db.query(StudentProfilePost)
        .filter(StudentProfilePost.student_user_id == req.studentUserId)
        .first()
    )
    if not spost or not spost.is_active:
        raise HTTPException(status_code=404, detail="Student post not found")

    # Reuse the student-post endpoint logic
    return company_decision_student_post(
        CompanyDecisionStudentPostRequest(
            studentPostId=spost.id,
            decision=req.decision
        ),
        db,
        current,
    )

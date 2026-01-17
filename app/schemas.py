from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.aliases import AliasChoices
from typing import Optional, List, Literal

from .models import UserRole, Decision, ApplicationStatus, MessageType


class RegisterRequest(BaseModel):
    name: str
    surname: str
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=6)
    role: UserRole


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str]
    surname: Optional[str]
    role: UserRole
    profileImageUrl: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    studies: Optional[str] = None
    experience: Optional[str] = None
    companyName: Optional[str] = None
    companyBio: Optional[str] = None


class UpdateMeRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    studies: Optional[str] = None
    experience: Optional[str] = None
    companyName: Optional[str] = None
    companyBio: Optional[str] = None


class StudentPublicProfileResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    profileImageUrl: Optional[str] = None

    university: Optional[str] = None
    department: Optional[str] = None

    bio: Optional[str] = None
    skills: Optional[str] = None
    studies: Optional[str] = None
    experience: Optional[str] = None


class CompanyPublicProfileResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    profileImageUrl: Optional[str] = None

    companyName: Optional[str] = None
    industry: Optional[str] = None
    bio: Optional[str] = None
    companyBio: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class PostCreateRequest(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    department: Optional[str] = None


class PostUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    companyUserId: int
    companyName: Optional[str]
    companyProfileImageUrl: Optional[str] = None
    # NEW fields for company map data
    username: Optional[str] = None
    bio: Optional[str] = None
    companyBio: Optional[str] = None
    profileImageUrl: Optional[str] = None
    title: str
    description: str
    location: Optional[str]
    department: Optional[str] = None
    imageUrl: Optional[str] = None
    saved: bool = False
    createdAt: datetime

    class Config:
        from_attributes = True


class StudentDecisionRequest(BaseModel):
    postId: int
    decision: Literal["LIKE", "PASS"]


class StudentSaveRequest(BaseModel):
    postId: int
    saved: bool


class StudentExperiencePostCreateRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = None


class StudentExperiencePostUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class StudentExperiencePostResponse(BaseModel):
    id: int
    studentUserId: int
    title: str
    description: str
    category: Optional[str]
    imageUrl: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True


# ✅ NEW: Company αποφασίζει σε student-profile post
class CompanyDecisionStudentPostRequest(BaseModel):
    studentPostId: int
    decision: Literal["LIKE", "PASS"]


# Convenience: decision by student user id (will resolve to the student's profile post)
class CompanyDecisionStudentRequest(BaseModel):
    studentUserId: int
    decision: Literal["LIKE", "PASS"]


# ✅ NEW: Αυτό που γυρνάει το /feed/company (student profiles σαν posts)
class StudentProfilePostResponse(BaseModel):
    id: int
    studentUserId: int

    studentUsername: Optional[str] = None
    studentName: Optional[str] = None
    studentSurname: Optional[str] = None

    studentProfileImageUrl: Optional[str] = None

    university: Optional[str] = None
    department: Optional[str] = None

    title: Optional[str] = None
    description: str
    location: Optional[str] = None
    imageUrl: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True


class ApplicationListItem(BaseModel):
    applicationId: int
    status: ApplicationStatus
    conversationId: Optional[int] = None  # null if no match yet

    # useful for UI
    postId: int
    postTitle: str
    studentUserId: int
    companyUserId: int

    # Track decisions
    studentDecision: Optional[Literal["LIKE", "PASS"]] = None
    companyDecision: Optional[Literal["LIKE", "PASS"]] = None

    otherPartyName: str  # companyName for student, or student username for company
    otherPartyProfileImageUrl: Optional[str] = None  # NEW: Profile image of the other party

    # requested
    lastMessage: Optional[str] = None

    # unread state (for Messages list dot)
    unreadCount: int = 0
    lastMessageId: Optional[int] = None
    lastMessageAt: Optional[datetime] = None
    
    internshipTitle: Optional[str] = None  # Alias for postTitle
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SetApplicationStatusRequest(BaseModel):
    # Backwards-compatible: some clients send LIKE/PASS instead of ACCEPTED/DECLINED.
    status: Literal["ACCEPTED", "DECLINED", "LIKE", "PASS"]


class MessageSender(BaseModel):
    id: int
    role: Optional[UserRole] = None
    name: Optional[str] = None
    avatarUrl: Optional[str] = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    type: MessageType
    # Canonical sender identity (stable across endpoints/roles)
    senderId: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("senderId", "senderUserId"),
        serialization_alias="senderId",
    )

    # Backwards-compatible mirror (deprecated)
    senderUserId: Optional[int] = None

    senderRole: Optional[UserRole] = None
    text: str
    createdAt: datetime

    # Optional richer identity
    senderName: Optional[str] = None
    senderProfileImageUrl: Optional[str] = None

    sender: Optional[MessageSender] = None

    # Optional: computed server-side for the current requester
    isMine: Optional[bool] = None

    # derived flags (kept for existing UI)
    fromCompany: bool
    isSystem: bool


class SendMessageRequest(BaseModel):
    text: str


class MarkConversationReadRequest(BaseModel):
    # Option A: best
    lastReadMessageId: Optional[int] = None

    # Option B
    readAt: Optional[datetime] = None


class MarkConversationReadResponse(BaseModel):
    conversationId: int
    unreadCount: int
    lastReadMessageId: Optional[int] = None

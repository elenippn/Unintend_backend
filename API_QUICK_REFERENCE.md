# API Quick Reference - Like/Pass Flow

## Decision Endpoints

### Student Likes/Passes Internship Post
```http
POST /decisions/student/post
Authorization: Bearer {student_token}
Content-Type: application/json

{
  "postId": 123,
  "decision": "LIKE"  // or "PASS"
}
```

**Response:**
```json
{
  "ok": true
}
```

### Company Likes/Passes Student Profile
```http
POST /decisions/company/student-post
Authorization: Bearer {company_token}
Content-Type: application/json

{
  "studentPostId": 456,
  "decision": "LIKE"  // or "PASS"
}
```

**Alternative (by user ID):**
```http
POST /decisions/company/student
Authorization: Bearer {company_token}
Content-Type: application/json

{
  "studentUserId": 789,
  "decision": "LIKE"  // or "PASS"
}
```

## Applications List

### Get All Applications/Messages
```http
GET /applications
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "applicationId": 1,
    "conversationId": 42,
    "status": "ACCEPTED",
    "studentUserId": 10,
    "companyUserId": 20,
    "postId": 123,
    "studentDecision": "LIKE",
    "companyDecision": "LIKE",
    "otherPartyName": "Acme Corp",
    "otherPartyProfileImageUrl": "/uploads/profiles/acme.jpg",
    "lastMessage": "Hello!",
    "unreadCount": 2,
    "internshipTitle": "Software Engineer Intern",
    "postTitle": "Software Engineer Intern",
    "lastMessageId": 5,
    "lastMessageAt": "2026-01-15T11:30:00Z",
    "createdAt": "2026-01-15T10:00:00Z",
    "updatedAt": "2026-01-15T11:30:00Z"
  }
]
```

## Status Values

| Status | Meaning | When |
|--------|---------|------|
| `PENDING` | Waiting for response | One party LIKEd, other hasn't responded |
| `ACCEPTED` | Match! | Both parties LIKEd |
| `DECLINED` | No match | At least one party PASSed |

## Decision Flow Examples

### Example 1: Successful Match
```
1. Student LIKEs post #123
   → Application: studentDecision=LIKE, companyDecision=null, status=PENDING
   → Message: "Message still pending"

2. Company LIKEs student
   → Application: companyDecision=LIKE, status=ACCEPTED
   → Message: "Ready to connect?"
   → Result: MATCH! Can now chat
```

### Example 2: Company Passes
```
1. Student LIKEs post #123
   → status=PENDING

2. Company PASSes student
   → Application: companyDecision=PASS, status=DECLINED
   → Message: "Unfortunately this was not a match, keep searching!"
```

### Example 3: Student Passes
```
1. Student PASSes post #123
   → Application: studentDecision=PASS, status=DECLINED
   → Message: "Unfortunately this was not a match, keep searching!"
   → Frontend: Filter out from Messages list
```

## Frontend Tips

### Show Pending Applications
```javascript
const pendingApps = applications.filter(app => 
  app.status === 'PENDING'
);

// Show "Waiting for response" UI
```

### Show Matches Only
```javascript
const matches = applications.filter(app => 
  app.status === 'ACCEPTED'
);

// Show conversation UI with chat
```

### Filter Out Declined
```javascript
const activeApps = applications.filter(app => 
  app.status !== 'DECLINED'
);
```

### Check Who Liked First
```javascript
function getLikeStatus(app, currentRole) {
  if (currentRole === 'STUDENT') {
    if (app.studentDecision === 'LIKE' && !app.companyDecision) {
      return 'You liked, waiting for company';
    }
    if (app.companyDecision === 'LIKE' && !app.studentDecision) {
      return 'Company liked you! Like back to match';
    }
  } else {
    if (app.companyDecision === 'LIKE' && !app.studentDecision) {
      return 'You liked, waiting for student';
    }
    if (app.studentDecision === 'LIKE' && !app.companyDecision) {
      return 'Student liked you! Like back to match';
    }
  }
  
  if (app.status === 'ACCEPTED') {
    return "It's a match!";
  }
  
  return '';
}
```

## Chat

### Get Conversation Messages
```http
GET /conversations/{conversationId}/messages
Authorization: Bearer {token}
```

**Response (always stable sender identity):**
```json
[
  {
    "id": 123,
    "text": "Καλημέρα...",
    "createdAt": "2026-01-16T12:34:56Z",
    "senderId": 45,
    "senderRole": "COMPANY",
    "sender": {
      "id": 45,
      "role": "COMPANY",
      "name": "Acme Corp",
      "avatarUrl": "/uploads/profiles/acme.jpg"
    },
    "type": "USER",
    "isSystem": false,
    "isMine": false
  }
]
```

**System message rules:**
- `type="SYSTEM"`
- `senderId=null` and `sender=null` (if there is no human sender)

**Naming consistency:**
- Use `senderId` everywhere (canonical)
- `senderUserId` may still appear for backwards compatibility, but should be treated as deprecated

### Send Message
```http
POST /conversations/{conversationId}/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "text": "Hello!"
}
```

**Notes:**
- Sender is derived from the JWT/session (not from client payload)
- Response includes the same message shape as GET (`senderId` always present)

## Testing with curl

### Student Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"eleni","password":"pass1234"}'
```

### Student Likes Post
```bash
curl -X POST http://127.0.0.1:8000/decisions/student/post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"postId":1,"decision":"LIKE"}'
```

### Company Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"acme_hr","password":"pass1234"}'
```

### Company Likes Student
```bash
curl -X POST http://127.0.0.1:8000/decisions/company/student \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"studentUserId":11,"decision":"LIKE"}'
```

### Get Applications
```bash
curl -X GET http://127.0.0.1:8000/applications \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Issues & Solutions

### Issue: Applications showing duplicates
**Solution:** Deduplication is automatic. If you still see duplicates, make sure you're using the latest version.

### Issue: conversationId is null
**Explanation:** Conversation exists but might not be loaded. Check if Application has a valid ID.

### Issue: Status not updating
**Solution:** Make sure both decisions are being set correctly. Check the database:
```sql
SELECT id, student_decision, company_decision, status FROM applications;
```

### Issue: System messages not appearing
**Solution:** System messages are added automatically on status changes. If missing, check the Messages table:
```sql
SELECT * FROM messages WHERE type = 'SYSTEM';
```

## Database Queries for Debugging

### Check Application Status
```sql
SELECT 
  a.id,
  a.student_decision,
  a.company_decision,
  a.status,
  u1.username as student,
  u2.username as company,
  p.title as post
FROM applications a
JOIN users u1 ON a.student_user_id = u1.id
JOIN users u2 ON a.company_user_id = u2.id
JOIN internship_posts p ON a.post_id = p.id;
```

### Check Conversations
```sql
SELECT 
  c.id as conv_id,
  a.id as app_id,
  a.status,
  COUNT(m.id) as message_count
FROM conversations c
JOIN applications a ON c.application_id = a.id
LEFT JOIN messages m ON m.conversation_id = c.id
GROUP BY c.id;
```

### Check System Messages
```sql
SELECT 
  m.id,
  m.conversation_id,
  m.text,
  m.created_at,
  a.status
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
JOIN applications a ON c.application_id = a.id
WHERE m.type = 'SYSTEM'
ORDER BY m.created_at DESC;
```

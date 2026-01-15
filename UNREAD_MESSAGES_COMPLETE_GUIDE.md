# Unread Messages Implementation - Complete Guide

## 🎯 Τι έχεις ήδη στο Backend (Ready to Use!)

### Endpoint: Mark Conversation as Read
```http
POST /conversations/{conversation_id}/read
Authorization: Bearer {token}
Content-Type: application/json

Body (Optional):
{
  "lastReadMessageId": 123  // Αν παραλείψεις = mark ALL as read
}

Response:
{
  "conversationId": 42,
  "unreadCount": 0,
  "lastReadMessageId": 123
}
```

### Endpoint: Get Applications (with unread count)
```http
GET /applications
Authorization: Bearer {token}

Response:
[
  {
    "applicationId": 1,
    "conversationId": 42,
    "unreadCount": 3,  ← Αυτό είναι το magic field!
    "lastMessage": "Hello!",
    "otherPartyName": "Acme Corp",
    ...
  }
]
```

---

## 📱 Flutter Implementation (Copy-Paste Ready)

### Step 1: Service Method

Πρόσθεσε αυτή τη μέθοδο στο `ChatService` ή `ApiService`:

```dart
Future<void> markConversationAsRead(int conversationId) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/conversations/$conversationId/read'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_token',
      },
      body: json.encode({}),  // Empty = mark all as read
    );
    
    if (response.statusCode != 200) {
      print('Failed to mark as read: ${response.statusCode}');
    }
  } catch (e) {
    print('Error marking as read: $e');
    // Don't throw - not critical
  }
}
```

### Step 2: Chat Screen Widget

Κάλεσε το `markConversationAsRead` όταν ανοίγει το chat:

```dart
class _ChatScreenState extends State<ChatScreen> {
  List<Message> messages = [];
  bool isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadMessagesAndMarkRead();
  }
  
  Future<void> _loadMessagesAndMarkRead() async {
    setState(() => isLoading = true);
    
    try {
      // 1. Load messages
      final msgs = await _chatService.getMessages(widget.conversationId);
      setState(() {
        messages = msgs;
        isLoading = false;
      });
      
      // 2. ✅ Mark as read (ΚΥΡΙΟ ΣΗΜΕΙΟ!)
      await _chatService.markConversationAsRead(widget.conversationId);
      
      // 3. Refresh applications list to update badges
      if (mounted) {
        context.read<ApplicationsProvider>().refreshApplications();
      }
    } catch (e) {
      setState(() => isLoading = false);
      // Handle error
    }
  }
  
  // ... rest of widget
}
```

### Step 3: Applications List - Show Unread Badge

```dart
class ApplicationListItem extends StatelessWidget {
  final Application app;
  final VoidCallback onTap;
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundImage: app.otherPartyProfileImageUrl != null
              ? NetworkImage(app.otherPartyProfileImageUrl!)
              : null,
          child: app.otherPartyProfileImageUrl == null 
              ? Text(app.otherPartyName[0].toUpperCase())
              : null,
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                app.otherPartyName,
                style: TextStyle(
                  fontWeight: app.unreadCount > 0 
                      ? FontWeight.bold 
                      : FontWeight.normal,
                ),
              ),
            ),
            
            // ✅ UNREAD BADGE (Κουκίδα)
            if (app.unreadCount > 0)
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${app.unreadCount}',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
        subtitle: Text(
          app.lastMessage ?? 'No messages yet',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: app.unreadCount > 0 ? Colors.black87 : Colors.grey,
            fontWeight: app.unreadCount > 0 ? FontWeight.w500 : FontWeight.normal,
          ),
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (app.lastMessageAt != null)
              Text(
                _formatTime(app.lastMessageAt!),
                style: TextStyle(
                  fontSize: 12,
                  color: app.unreadCount > 0 ? Colors.blue : Colors.grey,
                ),
              ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
  
  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m';
    } else {
      return 'now';
    }
  }
}
```

### Step 4: Model Class

Βεβαιώσου ότι το `Application` model έχει το `unreadCount`:

```dart
class Application {
  final int applicationId;
  final int? conversationId;
  final String status;
  final String otherPartyName;
  final String? otherPartyProfileImageUrl;
  final String? lastMessage;
  final int unreadCount;  // ✅ ΑΠΑΡΑΙΤΗΤΟ!
  final DateTime? lastMessageAt;
  
  Application({
    required this.applicationId,
    this.conversationId,
    required this.status,
    required this.otherPartyName,
    this.otherPartyProfileImageUrl,
    this.lastMessage,
    this.unreadCount = 0,
    this.lastMessageAt,
  });
  
  factory Application.fromJson(Map<String, dynamic> json) {
    return Application(
      applicationId: json['applicationId'],
      conversationId: json['conversationId'],
      status: json['status'],
      otherPartyName: json['otherPartyName'],
      otherPartyProfileImageUrl: json['otherPartyProfileImageUrl'],
      lastMessage: json['lastMessage'],
      unreadCount: json['unreadCount'] ?? 0,  // ✅ Parse from API
      lastMessageAt: json['lastMessageAt'] != null 
          ? DateTime.parse(json['lastMessageAt'])
          : null,
    );
  }
}
```

---

## 🎨 UI Examples

### Option 1: Κόκκινη κουκίδα με αριθμό (Recommended)
```dart
if (app.unreadCount > 0)
  Container(
    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(
      color: Colors.red,
      borderRadius: BorderRadius.circular(12),
    ),
    child: Text(
      '${app.unreadCount}',
      style: TextStyle(
        color: Colors.white,
        fontSize: 12,
        fontWeight: FontWeight.bold,
      ),
    ),
  )
```

### Option 2: Απλή κόκκινη κουκίδα (dot)
```dart
if (app.unreadCount > 0)
  Container(
    width: 10,
    height: 10,
    decoration: BoxDecoration(
      color: Colors.red,
      shape: BoxShape.circle,
    ),
  )
```

### Option 3: Badge με Material 3
```dart
if (app.unreadCount > 0)
  Badge(
    label: Text('${app.unreadCount}'),
    backgroundColor: Colors.red,
  )
```

### Option 4: Bold text για unread
```dart
Text(
  app.otherPartyName,
  style: TextStyle(
    fontWeight: app.unreadCount > 0 
        ? FontWeight.bold 
        : FontWeight.normal,
  ),
)
```

---

## 🔄 Complete Flow

```
┌──────────────────────────────────────────────────┐
│ User opens Messages List                        │
│                                                  │
│ GET /applications                                │
│ Response includes:                               │
│   - applicationId: 1                            │
│   - conversationId: 42                          │
│   - unreadCount: 3 🔴                          │
│   - lastMessage: "Hello!"                       │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ UI shows red badge with "3"                     │
│                                                  │
│ [Acme Corp]               [3] ← Red badge       │
│ Hello!                                           │
└──────────────────────────────────────────────────┘
                    │
                    ▼ User taps
┌──────────────────────────────────────────────────┐
│ ChatScreen opens                                 │
│                                                  │
│ 1. GET /conversations/42/messages                │
│    → Load messages                               │
│                                                  │
│ 2. POST /conversations/42/read                   │
│    → Mark as read                                │
│    Response: unreadCount = 0                     │
│                                                  │
│ 3. refreshApplications()                         │
│    → Reload list with updated counts             │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ User returns to Messages List                    │
│                                                  │
│ [Acme Corp]               ✅ No badge!          │
│ Hello!                                           │
│                                                  │
│ Badge disappeared because unreadCount = 0       │
└──────────────────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

### Backend Testing
```bash
# 1. Login as student
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"eleni","password":"pass1234"}'

# Save token
TOKEN="your_token_here"

# 2. Get applications (check unread count)
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/applications

# 3. Mark conversation as read
curl -X POST http://127.0.0.1:8000/conversations/1/read \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# 4. Verify unreadCount = 0
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/applications
```

### Flutter Testing
1. ✅ Open messages list → See unread badges
2. ✅ Tap conversation → Chat opens
3. ✅ Network tab → See POST /conversations/{id}/read
4. ✅ Return to list → Badge should be gone
5. ✅ Send new message from other user → Badge reappears

---

## 🐛 Troubleshooting

### Badge doesn't disappear
**Problem:** Unread count stays > 0 after opening chat

**Solutions:**
1. Check if `markConversationAsRead()` is being called
2. Verify the POST request returns 200 OK
3. Ensure `refreshApplications()` is called after marking
4. Check network logs for the API calls

```dart
// Add debug prints
Future<void> _loadMessagesAndMarkRead() async {
  print('Loading messages for conversation ${widget.conversationId}');
  final msgs = await _chatService.getMessages(widget.conversationId);
  
  print('Marking as read...');
  await _chatService.markConversationAsRead(widget.conversationId);
  
  print('Refreshing applications...');
  await context.read<ApplicationsProvider>().refreshApplications();
  
  print('Done!');
}
```

### Badge shows wrong count
**Problem:** unreadCount shows incorrect number

**Solutions:**
1. Backend calculates based on `last_read_message_id`
2. Make sure you're not counting SYSTEM messages
3. Only count messages where `sender_user_id != current_user.id`

### Multiple badges appear
**Problem:** Badge shows on multiple conversations

**Solution:** This is correct! Each conversation tracks its own unread count independently.

---

## 🎁 Bonus: Total Unread Badge

Show total unread count in BottomNavigationBar:

```dart
class MainScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<ApplicationsProvider>(
      builder: (context, provider, _) {
        final totalUnread = provider.applications
            .fold(0, (sum, app) => sum + app.unreadCount);
        
        return Scaffold(
          bottomNavigationBar: BottomNavigationBar(
            items: [
              BottomNavigationBarItem(
                icon: Icon(Icons.home),
                label: 'Home',
              ),
              BottomNavigationBarItem(
                icon: Badge(
                  isLabelVisible: totalUnread > 0,
                  label: Text('$totalUnread'),
                  child: Icon(Icons.chat),
                ),
                label: 'Messages',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.person),
                label: 'Profile',
              ),
            ],
          ),
        );
      },
    );
  }
}
```

---

## 📝 Summary

### Backend (Already Done ✅)
- ✅ `POST /conversations/{id}/read` - Mark as read
- ✅ `GET /applications` - Returns `unreadCount` for each conversation
- ✅ Automatic calculation based on `last_read_message_id`
- ✅ Only counts messages from other party (not your own)

### Flutter (3 Simple Steps)
1. ✅ Add `markConversationAsRead()` method to service
2. ✅ Call it in `ChatScreen.initState()` after loading messages
3. ✅ Show badge in list if `app.unreadCount > 0`

### Result
- Unread badge appears automatically
- Badge disappears when user opens chat
- Updates in real-time
- Works for both students and companies
- No extra setup needed! 🎉

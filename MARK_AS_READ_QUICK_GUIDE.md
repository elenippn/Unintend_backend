# Mark as Read - Quick Implementation Guide

## Backend Endpoint (Ήδη Έτοιμο ✅)

```http
POST /conversations/{conversation_id}/read
Authorization: Bearer {token}
Content-Type: application/json

{
  "lastReadMessageId": 123  // Optional - αν παραλείψεις, mark όλα ως read
}
```

**Response:**
```json
{
  "conversationId": 42,
  "unreadCount": 0,
  "lastReadMessageId": 123
}
```

---

## Flutter Implementation (3 Βήματα)

### 1️⃣ Service Method

```dart
Future<void> markConversationAsRead(int conversationId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/conversations/$conversationId/read'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
    body: json.encode({}),  // Άδειο body = mark όλα ως read
  );
  
  if (response.statusCode != 200) {
    throw Exception('Failed to mark as read');
  }
}
```

### 2️⃣ Chat Screen - Κάλεσε όταν ανοίγει

```dart
class _ChatScreenState extends State<ChatScreen> {
  @override
  void initState() {
    super.initState();
    _loadMessages();
  }
  
  Future<void> _loadMessages() async {
    // Load messages first
    final msgs = await chatService.getMessages(widget.conversationId);
    setState(() => messages = msgs);
    
    // ✅ ΚΥΡΙΟ ΣΗΜΕΙΟ: Mark as read
    await chatService.markConversationAsRead(widget.conversationId);
    
    // Refresh applications list to update unread badges
    context.read<ApplicationsProvider>().refreshApplications();
  }
}
```

### 3️⃣ Applications List - Εμφάνισε Badge

```dart
class ApplicationListItem extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Row(
        children: [
          Expanded(child: Text(app.otherPartyName)),
          
          // ✅ Unread Badge (Κουκίδα)
          if (app.unreadCount > 0)
            Container(
              padding: EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.red,
                shape: BoxShape.circle,
              ),
              child: Text(
                '${app.unreadCount}',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
        ],
      ),
      // ... rest of ListTile
    );
  }
}
```

---

## Πότε να καλείς το mark_as_read:

1. ✅ **Όταν ανοίγει το chat** (μόλις φορτώσουν τα messages)
2. ✅ **Όταν η app επιστρέφει από background** (optional)
3. ✅ **Όταν στέλνεις μήνυμα** (optional - για safety)

---

## Application Model - Απαραίτητο Field

```dart
class Application {
  final int unreadCount;  // ✅ Αυτό το field ελέγχει την κουκίδα!
  
  Application.fromJson(Map<String, dynamic> json)
      : unreadCount = json['unreadCount'] ?? 0,
        // ... other fields
}
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. User opens Applications List                        │
│    GET /applications                                    │
│    Response: unreadCount = 3 🔴                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. User taps on conversation                           │
│    → Opens ChatScreen                                   │
│    → GET /conversations/42/messages                     │
│    → Loads messages                                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Auto mark as read                                   │
│    POST /conversations/42/read                         │
│    Response: unreadCount = 0 ✅                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Refresh applications list                           │
│    provider.refreshApplications()                       │
│    → Fetches updated list                              │
│    → unreadCount = 0 (badge disappears!)               │
└─────────────────────────────────────────────────────────┘
```

---

## Testing με curl

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"eleni","password":"pass1234"}' \
  | jq -r '.access_token')

# 2. Get applications (check unreadCount)
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/applications

# 3. Mark as read
curl -X POST http://127.0.0.1:8000/conversations/1/read \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# 4. Verify unreadCount = 0
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/applications
```

---

## Troubleshooting

### Η κουκίδα δεν φεύγει
1. Ελέγξε ότι καλείς `markConversationAsRead()` μετά το load των messages
2. Βεβαιώσου ότι καλείς `refreshApplications()` μετά
3. Check network tab: Το POST request να επιστρέφει 200 OK

### unreadCount παραμένει > 0
1. Σιγουρέψου ότι το `conversationId` είναι σωστό
2. Check αν έχεις νέα messages που ήρθαν μετά το mark as read
3. Δοκίμασε χωρίς `lastReadMessageId` (mark all)

### Badge δεν εμφανίζεται καθόλου
1. Ελέγξε ότι το model έχει το `unreadCount` field
2. Βεβαιώσου ότι το backend στέλνει το field στο response
3. Check: `print('Unread: ${app.unreadCount}');`

---

## Bonus: Total Unread Count για Badge

```dart
class ApplicationsProvider extends ChangeNotifier {
  int get totalUnreadCount {
    return applications.fold(0, (sum, app) => sum + app.unreadCount);
  }
}

// Use in BottomNavigationBar
BottomNavigationBarItem(
  icon: Badge(
    isLabelVisible: provider.totalUnreadCount > 0,
    label: Text('${provider.totalUnreadCount}'),
    child: Icon(Icons.chat),
  ),
  label: 'Messages',
)
```

---

## Summary

✅ Backend endpoint: `POST /conversations/{id}/read`  
✅ Call στο ChatScreen.initState()  
✅ Refresh applications μετά το mark  
✅ Show badge αν `unreadCount > 0`  
✅ Η κουκίδα φεύγει αυτόματα! 🎉

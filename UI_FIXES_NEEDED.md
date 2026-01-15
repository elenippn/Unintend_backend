# ΤΙ ΠΡΕΠΕΙ ΝΑ ΦΤΙΑΞΕΙ Ο UI AGENT

## 🔴 ΠΡΟΒΛΗΜΑΤΑ ΣΤΟ SCREENSHOT

1. **Όλα τα μηνύματα είναι αριστερά** (με πράσινο background)
2. **Τα δικά σου πρέπει να είναι ΔΕΞΙΑ** (με μπλε background)

---

## ✅ Η ΛΥΣΗ (4 Βήματα)

### Βήμα 1: Πάρε το Current User ID

```dart
// Στο initState του ChatScreen
Future<void> _loadData() async {
  // ✅ Κάλεσε το /auth/me
  final meResponse = await http.get(
    Uri.parse('http://YOUR_IP:8000/auth/me'),
    headers: {'Authorization': 'Bearer YOUR_TOKEN'},
  );
  
  final meData = json.decode(meResponse.body);
  final currentUserId = meData['id'];  // ✅ π.χ. 11
  
  // Αποθήκευσε το σε state variable
  setState(() => this.currentUserId = currentUserId);
}
```

### Βήμα 2: Σύγκρινε το senderUserId

```dart
Widget _buildMessageBubble(Message message, int currentUserId) {
  // ✅ ΚΥΡΙΟ ΣΗΜΕΙΟ!
  final bool isMe = message.senderUserId == currentUserId;
  
  // Παράδειγμα:
  // currentUserId = 11 (εσύ)
  // message.senderUserId = 11 → isMe = true → ΔΕΞΙΑ
  // message.senderUserId = 1 → isMe = false → ΑΡΙΣΤΕΡΑ
}
```

### Βήμα 3: Alignment βάσει isMe

```dart
// ❌ ΛΑΘΟΣ (Αυτό που έχεις):
return Align(
  alignment: Alignment.centerLeft,  // Όλα αριστερά!
  child: ...
);

// ✅ ΣΩΣΤΟ (Αυτό που πρέπει):
return Align(
  alignment: isMe 
      ? Alignment.centerRight   // Δικά μου ΔΕΞΙΑ
      : Alignment.centerLeft,   // Άλλου ΑΡΙΣΤΕΡΑ
  child: ...
);
```

### Βήμα 4: Colors βάσει isMe

```dart
decoration: BoxDecoration(
  color: isMe 
      ? Colors.blue[700]      // Δικά μου = μπλε
      : Colors.green[100],    // Άλλου = πράσινο
  borderRadius: BorderRadius.circular(16),
)

// Text color
Text(
  message.text,
  style: TextStyle(
    color: isMe ? Colors.white : Colors.black87,
  ),
)
```

---

## 📋 ΠΛΗΡΗΣ ΚΩΔΙΚΑΣ

```dart
class _ChatScreenState extends State<ChatScreen> {
  List<Message> messages = [];
  int? currentUserId;  // ✅ Αποθήκευσε το current user ID
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    // 1. Πάρε το current user ID
    final meResponse = await http.get(
      Uri.parse('http://YOUR_IP:8000/auth/me'),
      headers: {'Authorization': 'Bearer YOUR_TOKEN'},
    );
    
    final meData = json.decode(meResponse.body);
    currentUserId = meData['id'];  // ✅ Αποθήκευσε
    
    // 2. Φόρτωσε messages
    final msgResponse = await http.get(
      Uri.parse('http://YOUR_IP:8000/conversations/${widget.conversationId}/messages'),
      headers: {'Authorization': 'Bearer YOUR_TOKEN'},
    );
    
    final List data = json.decode(msgResponse.body);
    setState(() {
      messages = data.map((json) => Message.fromJson(json)).toList();
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView.builder(
        itemCount: messages.length,
        itemBuilder: (context, index) {
          // ✅ Πέρνα το currentUserId
          return _buildMessageBubble(messages[index], currentUserId ?? 0);
        },
      ),
    );
  }
  
  Widget _buildMessageBubble(Message message, int currentUserId) {
    // System messages στο κέντρο
    if (message.isSystem) {
      return Center(
        child: Container(
          padding: EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            message.text,
            style: TextStyle(
              color: Colors.grey[600],
              fontStyle: FontStyle.italic,
            ),
          ),
        ),
      );
    }
    
    // ✅ Σύγκριση
    final bool isMe = message.senderUserId == currentUserId;
    
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4, horizontal: 12),
        padding: EdgeInsets.all(12),
        constraints: BoxConstraints(maxWidth: 250),
        decoration: BoxDecoration(
          color: isMe ? Colors.blue[700] : Colors.green[100],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: isMe ? Colors.white : Colors.black87,
          ),
        ),
      ),
    );
  }
}
```

---

## 🎯 ΤΙ ΣΤΕΛΝΕΙ ΤΟ BACKEND

```json
GET /auth/me Response:
{
  "id": 11,          ← Αυτό χρειάζεσαι!
  "username": "eleni",
  "role": "STUDENT"
}

GET /conversations/1/messages Response:
[
  {
    "id": 13,
    "senderUserId": 11,   ← Δικό σου (eleni)
    "text": "Γεια σας!",
    "isSystem": false
  },
  {
    "id": 15,
    "senderUserId": 1,    ← Άλλου (company)
    "text": "Hello!",
    "isSystem": false
  }
]
```

**Λογική:**
- `senderUserId: 11` == `currentUserId: 11` → ΔΕΞΙΑ (μπλε)
- `senderUserId: 1` != `currentUserId: 11` → ΑΡΙΣΤΕΡΑ (πράσινο)

---

## 🐛 BONUS: Fix για 422 Error στο Mark as Read

```dart
// ❌ ΛΑΘΟΣ (snake_case):
body: json.encode({
  'last_read_message_id': messageId,
})

// ✅ ΣΩΣΤΟ (camelCase):
body: json.encode({
  'lastReadMessageId': messageId,
})
```

---

## 📝 ΣΥΝΟΨΗ

**Το backend είναι 100% σωστό!** ✅

Το UI πρέπει:
1. ✅ Να πάρει το `currentUserId` από `/auth/me`
2. ✅ Να συγκρίνει `message.senderUserId == currentUserId`
3. ✅ Να βάλει `isMe ? right : left` alignment
4. ✅ Να βάλει `isMe ? blue : green` colors

**Αυτά τα 4 fixes λύνουν ΟΛΑ τα προβλήματα!** 🎉

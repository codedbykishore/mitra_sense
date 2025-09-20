
# MITRA Sense — Feature 1: Chat Persistence

## Goal
Persist all chat messages (user and AI) in Firestore so they can be retrieved later for context, analysis, and dashboards.  

---

## Requirements

### Backend
1. **Modify Chat Route** (`app/routes/input.py`):
   - After processing each message, save both **user input** and **AI response** to Firestore.  
   - Use `FirestoreService` for DB operations.  

2. **Message Schema** (Firestore `conversations/{conversation_id}/messages/{message_id}`):
```json
{
  "conversation_id": "string",
  "message_id": "string",
  "sender_id": "string",             // user_id or "ai"
  "text": "string",
  "timestamp": "timestamp",
  "metadata": {
    "source": "user|ai",
    "language": "en|hi|...",
    "embedding_id": "string|null",
    "emotion_score": {"anxious":0.5,"sad":0.2}
  },
  "mood_score": {"label":"calm","score":0.3}
}
```

3. **Conversation Document** (`conversations/{conversation_id}`):
```json
{
  "conversation_id": "string",
  "participants": ["user_id"],
  "created_at": "timestamp",
  "last_active_at": "timestamp"
}
```

4. **FirestoreService** (`app/services/firestore.py`):
   - `save_message(conversation_id, message_data)`  
   - `create_or_update_conversation(user_id)` → returns `conversation_id`  

5. Ensure all DB calls are **async**.

---

## Testing
- Unit test: `test_chat_persistence.py`  
  - Simulate sending a chat message  
  - Verify message + AI response are saved in Firestore with proper schema  

---
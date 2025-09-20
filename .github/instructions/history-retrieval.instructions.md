

# MITRA Sense — Feature 2.5: Chat History Retrieval

## Goal
Allow users to see their past conversations after logging out/logging in again or when accessing the app from another device.  

---

## Requirements

### Backend

1. **FirestoreService (`app/services/firestore.py`)**
   - Add:
     ```python
     async def get_messages(conversation_id: str, limit: int = 50) -> List[Dict]
     ```
     - Query `conversations/{conversation_id}/messages`.
     - Order by `timestamp` ascending (oldest → newest).
     - Apply `limit` for pagination.

   - Add:
     ```python
     async def get_user_conversations(user_id: str) -> List[Dict]
     ```
     - Returns conversation documents where user_id is a participant.
     - Sort by `last_active_at` descending.

2. **New API Endpoints**
   - `GET /api/v1/conversations`
     - Returns list of conversation_ids + metadata for current_user.
   - `GET /api/v1/conversations/{conversation_id}/messages?limit=50`
     - Returns messages for a conversation.
     - Verify current_user is in participants list.

3. **Access Control**
   - Only participants can fetch conversation messages.
   - Validate via `get_current_user`.

---

### Frontend

1. **Chat UI Initialization**
   - On login, call `/api/v1/conversations` to fetch latest conversation_id(s).
   - Then call `/api/v1/conversations/{conversation_id}/messages` to load chat messages.
   - Hydrate chat state with response.

2. **Pagination**
   - Implement "Load More" or infinite scroll to fetch older messages.

---

### Testing

- Unit test: `tests/test_chat_history.py`
  - Insert fake messages into Firestore.
  - Verify `get_messages()` returns correct order + limit.
  - Verify only participants can fetch conversations.

- Integration test: `tests/test_chat_history_real.py`
  - Run with real Firestore credentials.
  - Confirm endpoint returns actual saved chat.

---

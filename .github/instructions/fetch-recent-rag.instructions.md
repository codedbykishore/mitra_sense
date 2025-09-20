---
applyTo: '**'
---

# Feature 2 – Fetch Recent Chat Context for RAG

## Objective
Enable the AI to access **recent conversation history** so RAG-enhanced responses are contextually aware. Fetch the last N messages from a conversation for use in AI prompts.

## Instructions for Implementation

### Backend
1. **Firestore Query**
   - Fetch messages for a given `conversation_id`.
   - Order by `created_at` descending.
   - Limit to the last N messages (configurable, e.g., 10).

2. **Service Layer**
   - Create `ConversationService.get_recent_context(conversation_id, limit=10)`:
     - Calls Firestore query.
     - Returns messages sorted ascending (oldest → newest) to preserve conversation flow.
   - Include message content, sender info, timestamp.

3. **Optional API Endpoint**
   - `GET /api/v1/conversations/{conversation_id}/context?limit=N`
   - Returns `{ context: [...messages] }`

### Frontend
1. Before sending a chat message to `/api/v1/input/chat`:
   - Fetch recent messages for the conversation.
   - Include the fetched context in the request payload for RAG.

2. Ensure proper sorting and structure so AI can interpret the conversation in order.

### Testing
- Unit test Firestore query for correct ordering and limit.
- Integration test: fetch context, send to AI, verify AI response incorporates context correctly.

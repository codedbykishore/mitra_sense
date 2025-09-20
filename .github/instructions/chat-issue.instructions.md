---
applyTo: '**'
---

### Conversation History (Frontend)

- Use `useConversations.ts` hook to manage chat CRUD operations.
- Always sync with backend Firestore service:
  - `/api/v1/input/chat` → append message
  - `/api/v1/conversations/*` → manage CRUD
- Conversation structure:
  ```typescript
  interface Conversation {
    id: string;
    createdAt: string;
    updatedAt: string;
    messages: ChatMessage[];
  }

  interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    text: string;
    timestamp: string;
  }
  ```
- Store conversations in React Query or SWR cache for persistence.
- UI must support:
  - listing past conversations
  - resuming a selected conversation
  - editing/deleting messages
  - deleting an entire conversation

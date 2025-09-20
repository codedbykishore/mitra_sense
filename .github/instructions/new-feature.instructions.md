---
applyTo: '**'
---

# MITRA Sense — Institution Admin Dashboard Implementation Guide

## Feature Overview
Build a **dashboard for institution/admin users** to monitor student wellbeing, persist chat history, and provide role-based access while respecting privacy and consent.  

---

## High-Level Tasks

### **Priority A — Core Behavior**

**1. Chat Persistence**
- Save all user and AI messages in Firestore:
  - Collection: `conversations`
  - Subcollection: `messages`
- Message schema:
```json
{
  "conversation_id": "string",
  "message_id": "string",
  "sender_id": "string",
  "text": "string",
  "timestamp": "timestamp",
  "metadata": {
    "source": "user|ai",
    "embedding_id": "string",
    "emotion_score": {"anxious":0.5,"sad":0.2,...},
    "language": "en|hi|..."
  },
  "mood_score": {"label":"calm","score":0.3}
}
```

**2. Context Fetch for RAG**
- Add `FirestoreService.get_recent_context(user_id, limit=20, summarise=True)`:
  - Returns top-K messages or summary for Gemini RAG calls.
- Update `GeminiService.process_cultural_conversation(past_context=...)`.

**3. Student Listing & Mood Endpoints**
- `GET /api/v1/institutions/{institution_id}/students`:
  - Returns: profile, latest_mood, last_active_at, consent flags.
- `GET /api/v1/institutions/{institution_id}/students/{student_id}/mood`:
  - Returns detailed mood timeline.

**4. Frontend Dashboard**
- Page: `frontend/app/institution/dashboard/page.tsx`
- Components: `StudentList.tsx`, `StudentCard.tsx`, `StudentDetail.tsx`
- Features:
  - Role check: admin only
  - Displays student list, mood badges, last message snippet
  - Click-through to student detail/chat view
- Backend permission checks:
  - Verify `current_user.institution_id === requested_institution_id` and role = `institution_admin`

---

### **Priority B — Enhancements & Realtime**

**Realtime Mood Updates**
- Firestore real-time listeners or polling to update dashboard dynamically.

**Mood Computation**
- Add `MoodService`:
  - Aggregates voice STT emotion analysis + last N text messages
  - Computes score & label: calm, anxious, sad, angry, neutral
  - Optionally aggregate over last 24/72 hours
- Store latest_mood:  
```json
{"score":0.7,"label":"anxious","detail":{"anger":0.1,"sadness":0.6,...}}
```

**Student-Level Chat View**
- Optional page for admins
- Shows aggregated chat context & mood timeline
- Full transcript only if student consented

---

### **Priority C — Safety, Privacy & RAG Quality**

**Privacy & Consent**
- Add `user.profile.visibility` or `institution_visibility` (default false)
- Only show full transcripts with explicit consent
- Log all access events in `institution_access_logs`

**RAG Context Selection**
- Use embeddings to fetch semantically relevant messages
- Fallback: top-N messages by recency
- Limit context to avoid huge histories (3–5 messages + summary)

**Testing**
- Unit tests: `test_institution_dashboard.py`, `test_chat_persistence.py`
- Integration tests: `_real.py` files using actual Firestore credentials

---

## Assumptions
1. Users have `institution_id` and roles (`student`, `institution_admin`) in Firestore.
2. Onboarding already sets roles and institution IDs.
3. Google OAuth + sessions are functioning; `useUser.ts` provides role + institution_id.
4. RAG/Gemini pipeline can accept additional context.
5. Firestore collections exist: `users`, `institutions`, `conversations`.
6. Default privacy: show mood only unless student opts in for transcript sharing.

---
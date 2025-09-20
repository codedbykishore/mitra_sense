
# Feature 6 - Realtime Mood Updates + MoodService Implementation Guide

You are implementing **realtime mood updates** for MITRA Sense.

## 1. Backend Implementation

### MoodService (`app/services/mood_service.py`)
- Manage CRUD operations for student moods.
- Store moods in Firestore.
- Include timestamps and optional mood metadata (intensity, notes).
- Broadcast changes to authorized viewers using Firestore listeners or WebSockets.

### API Endpoints (`app/routes/mood.py`)
1. `POST /api/v1/students/{id}/mood` → Update mood
   - Validates student identity.
   - Checks privacy flags before saving.
   - Logs update in AccessLog.
2. `GET /api/v1/students/{id}/mood` → Get current mood
   - Returns latest mood entry.
   - Respects privacy flags.
   - Logs access in AccessLog.
3. `GET /api/v1/students/mood/stream` (optional) → Real-time mood feed
   - Streams mood updates for authorized viewers.
   - Ensure authentication and privacy enforcement.

### Security & Privacy
- Only the student can update their mood.
- Viewers can see moods based on privacy flags.
- Log all updates and reads.

### Firestore Integration
- Moods collection: `moods/{user_id}/entries`
- Fields: `timestamp`, `mood`, `intensity`, `notes` (optional)
- Real-time listeners for frontend updates.

---

## 2. Frontend Implementation

### Components
1. `MoodSelector.tsx`  
   - Dropdown or slider to select current mood.
   - Updates backend using `POST /api/v1/students/{id}/mood`.
2. `MoodDisplay.tsx`  
   - Shows the current mood.
   - Updates in real-time via listener or WebSocket.
3. `MoodStream.tsx` (optional)  
   - Listens for mood updates from multiple students (admins or peer groups).
   - Updates UI immediately on change.

### Hooks
- `useMood.ts`  
  - Encapsulate API calls, listener subscription, and privacy handling.

### UI/UX Considerations
- Display intensity visually (emoji, color, or bar).
- Handle errors gracefully.
- Respect privacy flags in UI (hide mood if `share_moods` is false).

---

## 3. Testing & Validation

- Unit tests for MoodService.
- API integration tests for mood endpoints.
- Frontend tests for components and real-time updates.
- Privacy enforcement validation.

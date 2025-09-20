---
applyTo: '**'
---

# Feature 5 – Privacy Flags + Access Logging

## Objective
Enhance user privacy and system accountability by adding:
1. **Privacy Flags** – Let users control visibility of their conversations/mood logs.  
2. **Access Logging** – Record when facilitators or admins access sensitive data.

## Instructions for Implementation

### Backend
1. **Firestore Schema Updates**
   - Add `privacy_flags` field in user/student profiles:
     - `share_moods` (bool, default `true`)
     - `share_conversations` (bool, default `true`)
   - Add `access_logs` collection:
     - Fields: `user_id`, `action`, `resource`, `timestamp`, `performed_by`.

2. **Service Layer**
   - `PrivacyService.check_flags(user_id, resource_type)` → returns whether access is allowed.  
   - `LoggingService.log_access(user_id, resource, action, performed_by)` → creates log entry.

3. **API Middleware**
   - Before returning moods or conversations, check privacy flags.  
   - If access denied → return 403 with safe error message.  
   - On every access → log event into `access_logs`.

4. **Endpoints**
   - `PATCH /api/v1/students/{id}/privacy` → update privacy flags.  
   - `GET /api/v1/students/{id}/access-logs` → facilitator/admin only.

### Frontend
1. **Privacy Settings UI**
   - Add a **Privacy Settings tab** in `/dashboard/students/{id}`.  
   - Toggles for:
     - Share moods
     - Share conversations
   - Save changes → call backend `PATCH` endpoint.

2. **Access Logs UI**
   - In dashboard, show list of access logs for a selected student.  
   - Display: who accessed, what resource, when.

### Testing
- Unit test privacy flag checks.  
- Integration test logs creation on data access.  
- Frontend test: toggle privacy and confirm restrictions take effect.


# Feature 3 – Student Listing + Mood API Endpoints

## Objective
Provide backend + frontend support for:
1. **Student Listing** – Retrieve all registered students for admin/facilitator dashboards.  
2. **Mood Tracking** – Store and fetch student mood updates.

## Instructions for Implementation

### Backend
1. **Firestore Data Models**
   - Add `students` collection with fields:
     - `id`, `name`, `email`, `created_at`
   - Add `moods` subcollection under each student:
     - Fields: `mood`, `notes`, `created_at`

2. **Service Layer**
   - `StudentService.list_students()`: fetch all student profiles.
   - `StudentService.add_mood(student_id, mood, notes)`: store mood entry.
   - `StudentService.get_moods(student_id, limit=10)`: fetch recent mood entries.

3. **API Endpoints**
   - `GET /api/v1/students` → return list of students.
   - `POST /api/v1/students/{student_id}/moods` → add new mood entry.
   - `GET /api/v1/students/{student_id}/moods?limit=N` → fetch recent moods.

### Frontend
1. **Student Listing**
   - Create a page `/dashboard/students`.
   - Fetch `/api/v1/students` and display list.
   - Show basic student info (name, email, joined date).

2. **Mood Tracking**
   - Add UI component for logging mood (dropdown + notes).
   - Display recent mood history for each student.

### Testing
- Unit test `StudentService` methods with Firestore mocks.
- Integration test API endpoints with sample student + mood data.

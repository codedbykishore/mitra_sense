

# Feature 4 – Frontend Dashboard Page + Components

## Objective
Build a **dashboard page** for facilitators/admins that integrates student listing, mood tracking, and conversation monitoring into a single UI hub.

## Instructions for Implementation

### Frontend (Next.js + React TypeScript)
1. **Dashboard Route**
   - Create page at `/dashboard`.
   - Protect route with authentication (redirect to login if not authenticated).
   - Use layout with sidebar navigation.

2. **Core Components**
   - **StudentListPanel.tsx**  
     - Shows list of students (from `/api/v1/students`).  
     - Click student → show details and mood history.  
   - **MoodSummaryPanel.tsx**  
     - Fetches aggregated mood data for all students.  
     - Display quick stats (happy, sad, stressed counts).  
   - **ConversationListPanel.tsx** *(read-only preview)*  
     - Show recent conversation snippets for each student.  
     - Integrate with existing `/api/v1/conversations` endpoint.  

3. **UI/UX Patterns**
   - Use Tailwind + shadcn/ui components (Cards, Tabs, Dropdowns).
   - Grid-based layout:
     - Left: Student list
     - Right: Tabbed content → Mood summary | Conversations
   - Loading spinners & error messages for API calls.

4. **Integration**
   - Reuse `StudentList`, `MoodTracker`, and `MoodHistory` from Feature 3.
   - Add a new `ConversationPreview` component.

### Backend (Optional Support)
- If not already available, implement `GET /api/v1/conversations` (list all conversations for admin).
- Ensure proper authentication/authorization for facilitator role.

### Testing
- Verify `/dashboard` loads with correct authentication.  
- Mock API calls for students, moods, and conversations in frontend tests.  
- Ensure all panels render properly with sample data.



# Copilot Task Prompt (Frontend - Next.js)

We already have Google Authentication working in our MITRA Sense project.  
Right now, after Google login, the user is redirected straight into the app.  
We want to **insert an onboarding step** where the user must fill out their details before entering the app.  

### Requirements

1. **Onboarding Page**
   - Create a new page in `frontend/app/onboarding/page.tsx`.
   - After successful Google OAuth login, redirect the user here **if they have no role/details in Firestore**.
   - UI should include:
     - Role selection: **Student** / **Institution** (radio or dropdown).
     - Additional fields:
       - Student → name, age, region, language preference
       - Institution → institution name, contact person, region
     - Submit button → calls backend to save details.

2. **User Context Update**
   - Extend the `useUser.jsx` (or equivalent user context hook) to track:
     - role
     - profile details (from Firestore).
   - If onboarding not completed, always redirect to `/onboarding`.

3. **API Integration**
   - Call a new endpoint (e.g. `/api/v1/users/onboarding`) to save the details.
   - Handle errors gracefully (retry, validation messages).

4. **Routing Rules**
   - If user logs in and **has onboarding completed**, go to main dashboard/chat.
   - If user logs in and **has NOT completed onboarding**, go to `/onboarding`.
   - Protect routes: disallow accessing chat/voice features until onboarding done.

5. **UI/UX Considerations**
   - Use Tailwind CSS for styling (consistent with project).
   - Simple, friendly tone for students.
   - Accessible (keyboard + screen reader support).
   - Show a loading spinner while checking onboarding status.

6. **Constraints**
   - DO NOT remove Google login flow.
   - DO NOT bypass onboarding for new users.
   - Keep code modular: Onboarding page separate from main app.
   - Follow Next.js App Router patterns (server components + client components where needed).

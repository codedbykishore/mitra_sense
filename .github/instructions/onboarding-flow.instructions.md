

# Copilot Task Prompt (Frontend - Next.js)

We already have Google Authentication working in our MITRA Sense project.  
Right now, after Google login, the user is redirected straight into the app.  
We want to **insert an onboarding step** where the user must fill out their details before entering the app.  

Most of this flow is already implemented — now we need to **add Institution-specific rules and logic**.  

---

### Requirements

1. **Onboarding Page Enhancements**
   - Role options: **Student** / **Institution**.
   - **Institution role form fields**:
     - Institution Name (text input)
     - Full Name (contact person)
     - Region
   - **Student role form fields**:
     - Name, Age, Region, Language preference
     - Institution dropdown:
       - Pre-populated with all existing institution names from Firestore
       - Include `"No Institution"` option  

2. **Institution Persistence**
   - When a new Institution signs up:
     - Save institution details in a global `institutions` collection in Firestore.
     - Ensure the `institutionName` is unique (no duplicates).
   - Students should only be able to pick institutions from this global list.  

3. **User Context Update**
   - Extend the user context (`useUser.jsx` or equivalent) to also track:
     - `institutionId` (or `null` if "No Institution")
     - Distinguish between Student and Institution roles.  

4. **API Integration**
   - Update `/api/v1/users/onboarding` endpoint:
     - For role = Institution → save to both `users` and `institutions` collection.
     - For role = Student → validate chosen institution exists (unless "No Institution").  

5. **Constraints**
   - DO NOT remove the Google login flow.
   - DO NOT bypass onboarding for new users.
   - Keep Onboarding page modular and separate from main app.
   - Maintain App Router conventions (server/client components).  

---

### UI/UX Notes
- Tailwind CSS styling, simple + friendly tone.  
- Student side should be lightweight and easy.  
- Institution side more formal but consistent design.  
- Accessible (keyboard navigation + screen readers).  
- Show spinner/loading while checking onboarding status.  


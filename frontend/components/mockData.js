import { makeId } from "./utils"

// Empty initial state - users start with no conversations
// Real conversations will be loaded from Firestore when authentication is implemented
export const INITIAL_CONVERSATIONS = []

export const INITIAL_TEMPLATES = [
  {
    id: "t1",
    name: "Daily Check-in",
    content: `🌅 **Daily Mental Health Check-in**

**How are you feeling today?**
Rate your mood from 1-10:

**What's on your mind?**
Share any thoughts or concerns you have today.

**Energy Level:**
- High / Medium / Low

**Sleep Quality:**
How did you sleep last night?

**Gratitude:**
One thing you're grateful for today:

**Support Needed:**
Is there anything specific you'd like to talk about or need help with?`,
    snippet: "Daily mood and mental health check-in template...",
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t2",
    name: "Stress Management",
    content: `😰 **Stress & Anxiety Management**

**What's causing stress right now?**
Identify the main sources of your stress:

**Physical Symptoms:**
- Tension, headaches, fatigue, etc.

**Emotional Impact:**
How is this affecting your mood and thoughts?

**Coping Strategies Used:**
What have you tried so far?

**Support System:**
Who can you reach out to?

**Self-Care Plan:**
What activities help you feel calmer?

**Professional Help:**
Would you like information about counseling or crisis support?

*Remember: You're not alone. Help is always available.*`,
    snippet: "Stress and anxiety management framework with coping strategies...",
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t3",
    name: "Family Communication",
    content: `👨‍👩‍👧‍👦 **Family & Cultural Understanding**

**Situation:**
What's happening with your family or cultural expectations?

**Your Perspective:**
How do you see the situation?

**Family's Perspective:**
Try to understand their point of view:

**Cultural Context:**
How do cultural values play a role?

**Communication Goals:**
What would you like to achieve?

**Respectful Approach:**
How can you honor both your needs and family values?

**Compromise Ideas:**
What middle ground might work?

**Support Needed:**
Would you like help preparing for this conversation?

*MITRA understands the importance of family harmony while supporting your individual well-being.*`,
    snippet: "Navigate family conversations with cultural sensitivity...",
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "t4",
    name: "Crisis Support",
    content: `🚨 **Immediate Support & Crisis Resources**

**If you're having thoughts of self-harm or suicide:**
- **Tele MANAS**: 14416 (24/7 mental health helpline)
- **Emergency**: 112 or go to nearest hospital
- **Crisis Text**: Text HOME to 741741

**Current Safety:**
Are you in immediate danger? Y/N

**Support Person:**
Is there someone you can call right now?

**Immediate Needs:**
What do you need most urgently?

**Professional Help:**
Would you like help connecting with a counselor?

**Follow-up:**
Can we check in with you later?

**Remember:** 
- Your life has value
- This feeling is temporary  
- Help is available
- You are not alone

*MITRA is here to support you, but for immediate crisis situations, please contact emergency services or Tele MANAS.*`,
    snippet: "Crisis support resources and immediate safety planning...",
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

export const INITIAL_FOLDERS = [
  { id: "f1", name: "Mental Health" },
  { id: "f2", name: "Family & Relationships" },
  { id: "f3", name: "Personal Growth" },
  { id: "f4", name: "Crisis Support" },
]

# 🎨 MITRA Sense UI Features Guide

## 🚀 How to Access All Implemented Features

### **📱 Application URLs**
- **Main App**: `http://localhost:3000` (Next.js Frontend)
- **API Documentation**: `http://localhost:8000/docs` (FastAPI Swagger UI)
- **API Base**: `http://localhost:8000` (Backend API)

---

## 🏠 **Main UI Features** (http://localhost:3000)

### **1. 🔐 Authentication System**
**Location**: Landing page when not logged in
- **Google OAuth Login**: Click "Login with Google" button
- **Session Management**: Automatic login persistence
- **Logout**: Available in user menu

**How to Access**:
1. Visit `http://localhost:3000`
2. If not logged in, you'll see the login screen
3. Click "Login with Google" to authenticate

### **2. 📋 User Onboarding Flow**
**Location**: `http://localhost:3000/onboarding` (auto-redirects)
- **Student Role**: Name, Age, Region, Language, Institution selection
- **Institution Role**: Institution creation and management
- **Dynamic Institution Dropdown**: Real-time institution list from Firestore

**How to Access**:
1. After first login, automatic redirect to onboarding
2. Complete profile information
3. Select or create institution
4. Choose privacy preferences

### **3. 💬 Main Chat Interface**
**Location**: Main dashboard after login
- **AI-Powered Conversations**: RAG-enhanced responses
- **Cultural Context**: Hindi/English code-switching support
- **Voice Integration**: Push-to-talk functionality
- **Real-time Responses**: Streaming AI responses
- **Conversation History**: Persistent chat history

**Features Available**:
- **Text Chat**: Type messages and get AI responses
- **Voice Chat**: Click microphone icon for voice input
- **Conversation Management**: Multiple conversation threads
- **Crisis Detection**: Automatic risk assessment
- **Mood Inference**: Automatic mood detection from messages ✨ **NEW**

### **4. 🎤 Voice Companion System**
**Location**: Integrated into chat interface
- **Push-to-Talk**: Hold to record voice messages
- **Speech-to-Text**: Converts voice to text
- **Text-to-Speech**: AI responses read aloud
- **Emotion Analysis**: Voice emotion detection
- **Multi-language**: Hindi and English support

**How to Use**:
1. Click the microphone icon in chat
2. Hold to record your message
3. Release to process and send
4. Receive both text and audio response

### **5. 😊 Mood Management System** ✨ **NEWLY IMPLEMENTED**
**Location**: Integrated throughout the app
- **Manual Mood Selection**: `MoodSelector` component
- **Current Mood Display**: `MoodDisplay` component
- **Real-time Mood Stream**: `MoodStream` component for admins
- **Automatic Mood Inference**: From chat messages
- **Privacy Controls**: User-controlled sharing

**How to Access**:
1. **Manual Mood Update**: Look for mood selector in UI
2. **View Current Mood**: Mood display shows current state
3. **Automatic Detection**: Chat messages automatically analyzed
4. **Privacy Settings**: Control who sees your mood

### **6. 👥 Student Management** (Institution View)
**Location**: Available for institution users
- **Student List**: View enrolled students
- **Mood Analytics**: Aggregate mood data
- **Privacy-Aware**: Only shared data visible
- **Real-time Updates**: Live mood and conversation updates

### **7. 📊 Dashboard & Analytics**
**Location**: Main dashboard area
- **Mood Analytics**: Mood trends and distributions
- **Conversation Statistics**: Usage metrics
- **Institution Overview**: Student engagement data
- **Privacy-Compliant**: Only authorized data shown

---

## 🛠️ **Developer/Testing Features**

### **8. 📚 API Documentation**
**Location**: `http://localhost:8000/docs`
- **Interactive API Docs**: Test all endpoints
- **Schema Documentation**: Request/response formats
- **Authentication Testing**: Try authenticated endpoints

**Key Endpoints to Test**:
- `POST /api/v1/input/chat` - Main chat endpoint
- `POST /api/v1/students/mood/infer` - Mood inference testing ✨ **NEW**
- `GET /api/v1/students/mood/stream` - Real-time mood stream
- `GET /api/v1/students/mood/analytics` - Mood analytics

### **9. 🧪 Testing Interface**
You can test features directly:

```bash
# Test chat with mood inference
curl -X POST "http://localhost:8000/api/v1/input/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "I am feeling really excited about my project!"}'

# Test mood inference directly  
curl -X POST "http://localhost:8000/api/v1/students/mood/infer" \
  -H "Content-Type: application/json" \
  -d '{"message": "I feel amazing today!", "language": "en", "auto_update_enabled": true}'
```

---

## 🎯 **How to Experience Each Feature**

### **Complete User Journey**:

1. **🔐 Login Process**:
   - Visit `http://localhost:3000`
   - Click "Login with Google"
   - Complete Google OAuth flow

2. **📋 Onboarding**:
   - Fill out profile information
   - Select your institution
   - Set privacy preferences
   - Choose language preferences

3. **💬 Chat Experience**:
   - Start typing in the chat interface
   - Send messages about your feelings/mood
   - **Watch automatic mood inference work** ✨
   - Try voice input with microphone
   - See culturally-aware responses

4. **😊 Mood Features**:
   - **Automatic**: Chat "I'm feeling happy!" and see mood auto-detected
   - **Manual**: Use mood selector to set mood manually
   - **Analytics**: View mood trends (if authorized)
   - **Privacy**: Control who can see your mood

5. **🎤 Voice Features**:
   - Click microphone in chat
   - Record voice message
   - Get voice response back
   - See emotion analysis from voice

6. **👥 Institution Features** (if institution user):
   - View student dashboard
   - See aggregated mood analytics
   - Monitor real-time mood updates
   - Access privacy-compliant data

---

## 🎨 **UI Component Locations**

### **Main Components**:
- **`AIAssistantUI.jsx`**: Main application container
- **`ChatPane.jsx`**: Chat interface with voice integration
- **`Sidebar.jsx`**: Navigation and conversation history
- **`Header.jsx`**: Top navigation bar
- **`Login.jsx`**: Authentication interface

### **Mood Components** ✨ **NEW**:
- **`MoodSelector.tsx`**: Manual mood selection
- **`MoodDisplay.tsx`**: Current mood display
- **`MoodStream.tsx`**: Real-time mood updates

### **Voice Components**:
- **`VoiceCompanion.tsx`**: Voice interaction system
- **`voice/`**: Complete voice processing pipeline

### **Student Management**:
- **`students/`**: Student-related components
- **`dashboard/`**: Analytics and overview

---

## 🚨 **Quick Feature Test Checklist**

To quickly verify all features are working:

### ✅ **Authentication**:
- [ ] Can login with Google OAuth
- [ ] Session persists on refresh
- [ ] Can logout successfully

### ✅ **Onboarding**:
- [ ] New user redirected to onboarding
- [ ] Can complete profile setup
- [ ] Institution selection works
- [ ] Privacy settings saved

### ✅ **Chat System**:
- [ ] Can send text messages
- [ ] Receives AI responses
- [ ] Conversation history persists
- [ ] Cultural context works (try Hindi)

### ✅ **Voice Features**:
- [ ] Microphone activation works
- [ ] Voice-to-text conversion
- [ ] Text-to-speech playback
- [ ] Voice emotion analysis

### ✅ **Mood System** ✨ **NEW**:
- [ ] Manual mood selection
- [ ] Automatic mood inference from chat
- [ ] Mood display updates
- [ ] Privacy controls work
- [ ] Analytics available (if authorized)

### ✅ **Institution Features**:
- [ ] Student list displays
- [ ] Mood analytics accessible
- [ ] Real-time updates work
- [ ] Privacy enforcement active

---

## 🎉 **Experience the Full MITRA Sense System**

**Visit `http://localhost:3000` now to see all these features in action!**

The application includes:
- ✅ Complete authentication flow
- ✅ User onboarding experience  
- ✅ AI-powered chat with cultural awareness
- ✅ Voice interaction system
- ✅ **Automatic mood inference from messages** ✨
- ✅ Real-time mood management
- ✅ Student/institution management
- ✅ Privacy-first design
- ✅ Mobile-responsive interface
- ✅ Dark/light theme support

**All features are live and fully functional!** 🚀

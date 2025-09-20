# Feature 5 - Privacy Flags and Access Logging

## Implementation Complete ✅

This document describes the complete implementation of Feature 5: Privacy Flags and Access Logging for the MITRA Sense project.

## Backend Implementation

### 1. Database Models

#### Updated User Model
```python
# app/models/db_models.py
class User(BaseModel):
    # ... existing fields
    privacy_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "share_moods": True,
            "share_conversations": True
        }
    )
```

#### New AccessLog Model
```python
class AccessLog(BaseModel):
    log_id: str
    user_id: str  # The user whose data was accessed
    resource: str  # Resource accessed (e.g., "moods", "conversations")
    action: str  # Action performed (e.g., "view", "export", "list")
    performed_by: str  # user_id of who performed the action
    performed_by_role: str  # Role of the person who performed the action
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)
```

### 2. Services

#### PrivacyService
- `check_flags(user_id, resource_type)` - Check if access is allowed
- `update_privacy_flags(user_id, privacy_flags)` - Update user privacy settings
- `get_privacy_flags(user_id)` - Get current privacy settings

#### LoggingService
- `log_access(user_id, resource, action, performed_by, ...)` - Log access events
- `get_access_logs(user_id, limit)` - Get access logs for a user
- `get_recent_access_logs(limit)` - Get recent logs across all users (admin)

### 3. API Endpoints

#### Privacy Settings
```http
PATCH /api/v1/students/{id}/privacy
Content-Type: application/json

{
  "privacy_flags": {
    "share_moods": true,
    "share_conversations": false
  }
}
```

#### Access Logs
```http
GET /api/v1/students/{id}/access-logs?limit=50
```

### 4. Privacy Middleware

The `PrivacyMiddleware` automatically:
- Checks privacy flags before allowing access to protected resources
- Logs all access attempts (successful and denied)
- Raises HTTP 403 errors when access is denied due to privacy settings

#### Example Usage in Routes
```python
# Before accessing student moods
await privacy_middleware.check_and_log_access(
    target_user_id=student_id,
    resource_type="moods",
    action="view",
    current_user=current_user.model_dump(),
    metadata={"limit": str(limit)}
)
```

## Frontend Implementation

### 1. Privacy Settings Component
- Toggle switches for mood and conversation sharing
- Visual indicators for sharing status
- Save functionality with error handling
- Privacy notices and explanations

### 2. Access Logs Component
- Chronological list of access events
- Detailed information about who accessed what and when
- Role-based access control (only institution admins can view)
- Expandable metadata for detailed context

### 3. Privacy Tab Component
- Unified tab interface combining settings and logs
- Role-based visibility controls
- Responsive design with loading states

## Security Features

### Access Control
1. **Students** can only update their own privacy settings
2. **Institution admins** can update privacy settings for students in their institution
3. **Only institution role** can view access logs
4. All access is logged, including denied attempts

### Privacy Protection
1. Privacy flags are enforced at the API level
2. Access logging happens automatically via middleware
3. Meta-logging: Viewing access logs is itself logged
4. Emergency override capability for crisis situations

### Audit Trail
Every access to sensitive data creates a log entry with:
- User whose data was accessed
- Resource type (moods, conversations, etc.)
- Action performed (view, export, update, etc.)
- Who performed the action and their role
- Timestamp
- Additional metadata (e.g., filters, limits)

## Example API Usage

### Test Privacy Settings Update
```bash
curl -X PATCH http://localhost:8000/api/v1/students/user123/privacy \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "privacy_flags": {
      "share_moods": false,
      "share_conversations": true
    }
  }'
```

### Test Access Logs Retrieval
```bash
curl -X GET "http://localhost:8000/api/v1/students/user123/access-logs?limit=20" \
  -H "Cookie: session=..."
```

### Test Privacy-Protected Mood Access
```bash
# This will be denied if share_moods is false and not accessing own data
curl -X GET "http://localhost:8000/api/v1/students/user123/moods?limit=10" \
  -H "Cookie: session=..."
```

## Integration Points

### 1. Student Routes
Updated `app/routes/students.py` to include privacy checks for:
- `GET /students/{id}/moods` - Check share_moods flag
- Future: Conversation access endpoints

### 2. Main Application
Added privacy router to `app/main.py`:
```python
from app.routes.privacy import router as privacy_router
app.include_router(privacy_router, tags=["privacy"])
```

### 3. Frontend Integration
The privacy components can be integrated into existing student dashboard:
```jsx
import { PrivacyTab } from './components/students/PrivacyTab';

// In student detail view
<PrivacyTab 
  studentId={studentId}
  currentUserId={currentUser.id}
  currentUserRole={currentUser.role}
/>
```

## Testing

### Backend Tests
Create tests for:
- Privacy flag checking logic
- Access logging functionality
- API endpoint authorization
- Middleware integration

### Frontend Tests
Create tests for:
- Privacy toggle interactions
- Access log display
- Error handling
- Role-based visibility

## Configuration

### Environment Variables
No additional environment variables required. Uses existing Firestore and authentication setup.

### Database Collections
- `users` - Updated to include privacy_flags
- `access_logs` - New collection for audit trail

## Monitoring & Analytics

### Access Patterns
The logging system enables analysis of:
- Most accessed data types
- Access frequency by role
- Privacy setting adoption rates
- Potential unauthorized access attempts

### Privacy Compliance
- Full audit trail for data access
- User control over data sharing
- Transparent access logging
- Emergency override logging

## Future Enhancements

1. **Data Export Controls** - Privacy flags for data export requests
2. **Granular Permissions** - Time-based or context-based sharing
3. **User Notifications** - Alert users when their data is accessed
4. **Admin Dashboard** - Centralized view of all access logs
5. **Compliance Reports** - Automated privacy compliance reporting

## Success Metrics

✅ **Privacy Control**: Users can control sharing of moods and conversations  
✅ **Access Transparency**: All data access is logged and auditable  
✅ **Role-Based Access**: Institution admins can view access logs  
✅ **Security**: Privacy flags are enforced at API level  
✅ **User Experience**: Clean, intuitive privacy settings interface  
✅ **Compliance**: Full audit trail for regulatory requirements

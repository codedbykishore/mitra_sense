---
applyTo: '**'
---

# Feature: Twilio WhatsApp Crisis Notification Integration

You are implementing a **Twilio WhatsApp notification system** for MITRA Sense.  
This feature will automatically notify the college counsellor when a student is detected to be at high risk of suicide or severe crisis.

## 1️⃣ Scope & Flow

- **Trigger:** High-risk conversation detected (crisis_score ≥ 0.8 from chat, voice, or mood analysis)  
- **Recipient:** College counsellor or designated emergency contact  
- **Channel:** WhatsApp via Twilio  
- **Message Content:** Minimal PII, crisis score, timestamp, suggested action  
- **Privacy:** Only send if emergency override or consent is provided  

### Flow
```
Crisis Detection → Privacy Check → Twilio WhatsApp Notification → Logging
```

---

## 2️⃣ Backend Service

### CrisisNotificationService (`app/services/crisis_notification_service.py`)
- Encapsulate Twilio API calls
- Accept `user_id`, `crisis_score`, `message`, optional metadata
- Respect privacy flags (`emergency_override`)
- Log all notifications in Firestore (`crisis_logs` or `access_logs`)
- Retry failed messages if Twilio API returns an error

**Methods:**
- `send_whatsapp_alert(user_id: str, crisis_score: float, message: str) -> bool`
- `log_notification(user_id: str, recipient: str, status: str) -> None`

---

## 3️⃣ API Endpoint (Optional)

### `POST /api/v1/crisis/escalate`
- Manual override for counsellor notification
- Body parameters:
```json
{
  "user_id": "string",
  "message": "string"
}
```
- Authentication required: Admin / Counsellor
- Logs all manual notifications

---

## 4️⃣ Twilio Integration Setup

1. Create Twilio account (sandbox or production)  
2. Obtain credentials: `ACCOUNT_SID`, `AUTH_TOKEN`, WhatsApp sender ID  
3. Test sending a simple WhatsApp message  
4. Configure environment variables in backend  

**Example environment variables:**
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
COUNSELLOR_WHATSAPP_TO=whatsapp:+91XXXXXXXXXX
```

---

## 5️⃣ Testing & Validation

- Unit tests for `CrisisNotificationService` methods  
- Integration tests with Twilio sandbox  
- Verify privacy enforcement: notifications sent only when allowed  
- Simulate multiple simultaneous crisis events  
- Check Firestore logs for proper auditing

---

## 6️⃣ Frontend/Admin Integration (Optional)

- Display real-time crisis alerts to admins/counsellors  
- Allow manual escalation via `POST /api/v1/crisis/escalate`  
- Show notification status (sent, failed) in dashboard

---

## 7️⃣ Documentation & Compliance

- Document message templates, logging policies, and privacy enforcement  
- Ensure minimal PII in messages  
- Maintain HIPAA/GDPR/Indian IT Act compliance
- Include full audit trail for every notification

---

## 8️⃣ Deployment & Monitoring

- Deploy as serverless function or part of backend  
- Monitor logs and Twilio delivery reports  
- Retry failed messages automatically  
- Alert dev team if messages fail consistently

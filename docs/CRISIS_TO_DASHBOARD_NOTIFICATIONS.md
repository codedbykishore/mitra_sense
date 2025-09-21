# Crisis Escalation → Institution Notifications

This document describes how high-risk crisis detections generate privacy-preserving notifications visible to institution users in the MITRA dashboard.

## Flow

1. Detection: `/api/v1/crisis/detect` computes risk score and level using keyword + Gemini.
2. Auto-escalate: For `risk_level == high`, `CrisisService.escalate()` runs.
3. Notification: If the student belongs to an institution, an `InstitutionNotification` is created in Firestore under `institution_notifications`.
4. Viewing: Institution users open the dashboard and see notifications via `/api/v1/notifications/institution`.
5. Acknowledge: Users can mark notifications read via `/api/v1/notifications/{id}/read`.

## Data Model

- `InstitutionNotification` (Pydantic): `notification_id`, `institution_id`, `user_id`, `type`, `severity`, `risk_score`, `risk_level`, `reason`, `status`, `metadata`, `created_at`.
- Minimal PII: we only include the student `user_id`.

## Backend

- Model: `app/models/db_models.py`
- Firestore helpers: `create_institution_notification`, `list_institution_notifications`, `mark_notification_read`, and `get_institution_id_for_user` in `app/services/firestore.py`.
- Router: `app/routes/notifications.py` mounted at `/api/v1`.
- Crisis integration: `app/services/crisis.py` creates a notification during escalation for high risk.

## Frontend

- Types: `frontend/types/notifications.ts`
- Component: `frontend/components/dashboard/NotificationsPanel.tsx`
- Usage: wired into `frontend/app/dashboard/page.tsx` (tab + sidebar widget).

## Notes

- Authorization: Only `institution` and `admin` roles can list notifications. Admin must specify `?institution_id=...`.
- Polling: Frontend refreshes every 15s.
- Cooldown: Escalation-level dedupe is handled by `CrisisService.is_under_cooldown()`. You can add additional dedupe logic if needed.

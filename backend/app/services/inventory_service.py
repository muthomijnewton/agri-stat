from datetime import timedelta, timezone
from app.models.foundation import utcnow


def batch_status(batch, now=None):
    if batch.quantity_on_hand == 0:
        return "DEPLETED"
    if batch.expires_at is None:
        return "ACTIVE"
    now = now or utcnow()
    expires = batch.expires_at
    if expires.tzinfo is None:  # SQLite does not retain timezone metadata.
        expires = expires.replace(tzinfo=timezone.utc)
    if expires <= now:
        return "EXPIRED"
    return "EXPIRING_SOON" if expires <= now + timedelta(days=3) else "ACTIVE"

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Notification, User
from app.core.security import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return {
        "count": db.query(Notification).filter(Notification.read == False).count()  # noqa: E712
    }


# NOTE: /read-all MUST be registered before /{notification_id}/read.
# FastAPI matches routes top-to-bottom; if the parameterised route came first,
# "read-all" would be captured as an integer notification_id and raise a 422.
@router.patch("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    db.query(Notification).update({Notification.read: True})
    db.commit()
    return {"status": "all marked as read"}


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read = True
    db.commit()
    return {"status": "updated"}

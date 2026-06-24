from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db)):
    return {
        "count": db.query(Notification).filter(Notification.read == False).count()
    }


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.read = True
        db.commit()
    return {"status": "updated"}


@router.patch("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).update({Notification.read: True})
    db.commit()
    return {"status": "all marked as read"}
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import TrackedItem, PriceHistory
from schemas import ItemResponse, PriceHistoryResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(user_id: int, db: Session = Depends(get_session)):
    items = db.exec(
        select(TrackedItem).where(TrackedItem.user_id == user_id)
    ).all()

    total_items = len(items)
    active_items = len([i for i in items if i.is_active])

    return {
        "total_items": total_items,
        "active_items": active_items,
        "items": [
            {
                "id": i.id,
                "name": i.name,
                "current_price": float(i.current_price),
                "is_active": i.is_active,
            }
            for i in items
        ],
    }

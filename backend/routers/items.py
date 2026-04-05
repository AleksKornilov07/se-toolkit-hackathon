from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from decimal import Decimal
from database import get_session
from models import User, TrackedItem, PriceHistory
from schemas import ItemCreate, ItemResponse, PriceHistoryResponse
from services.price_checker import fetch_price
import asyncio

router = APIRouter(prefix="/api/items", tags=["items"])


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        user = User(id=user_id, username=f"user_{user_id}")
        db.add(user)

    # Fetch current price immediately on creation
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        current_price = loop.run_until_complete(fetch_price(item.url, item.store))
        loop.close()
        if current_price is None:
            current_price = Decimal("0")
    except Exception:
        current_price = Decimal("0")

    new_item = TrackedItem(
        user_id=user_id,
        name=item.name,
        url=item.url,
        store=item.store,
        current_price=current_price,
        target_price=item.target_price,
        is_active=True,
    )
    db.add(new_item)

    # Record initial price in history
    if current_price > 0:
        history = PriceHistory(
            item_id=new_item.id,
            price=current_price,
            currency="USD",
            in_stock=True,
        )
        db.add(history)

    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/", response_model=list[ItemResponse])
def get_items(user_id: int, db: Session = Depends(get_session)):
    return db.exec(select(TrackedItem).where(TrackedItem.user_id == user_id)).all()


@router.get("/{item_id}/history", response_model=list[PriceHistoryResponse])
def get_price_history(item_id: int, db: Session = Depends(get_session)):
    return db.exec(
        select(PriceHistory)
        .where(PriceHistory.item_id == item_id)
        .order_by(PriceHistory.checked_at.desc())
        .limit(100)
    ).all()


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_session)):
    item = db.get(TrackedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}

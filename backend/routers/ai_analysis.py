from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import TrackedItem, PriceHistory
from decimal import Decimal
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/analyze/{item_id}")
def analyze_price(item_id: int, db: Session = Depends(get_session)):
    """AI-powered price analysis with recommendation"""
    item = db.get(TrackedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    history = db.exec(
        select(PriceHistory)
        .where(PriceHistory.item_id == item_id)
        .order_by(PriceHistory.checked_at)
    ).all()

    # If not enough history, generate mock data for demo
    if len(history) < 3:
        history = _generate_mock_history(item.current_price)

    prices = [float(h.price) for h in history]
    current_price = prices[-1] if prices else float(item.current_price)
    avg_price = sum(prices) / len(prices) if prices else current_price
    min_price = min(prices) if prices else current_price
    max_price = max(prices) if prices else current_price

    # Determine trend
    if len(prices) >= 2:
        if prices[-1] < prices[0]:
            trend = "falling"
        elif prices[-1] > prices[0]:
            trend = "rising"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Generate recommendation
    if trend == "falling" and current_price > avg_price * 0.9:
        recommendation = "WAIT"
        reason = f"Price is falling. Average is ${avg_price:.2f}, current is ${current_price:.2f}. Wait for a better deal."
    elif trend == "rising":
        recommendation = "BUY NOW"
        reason = f"Price is rising. Current ${current_price:.2f} may be the lowest you'll see soon."
    elif current_price <= min_price * 1.05:
        recommendation = "BUY NOW"
        reason = f"Price is near historic low (${min_price:.2f}). Good time to buy!"
    else:
        recommendation = "WAIT"
        reason = f"Price is stable at ${current_price:.2f}. Monitor for drops."

    return {
        "item_id": item_id,
        "item_name": item.name,
        "current_price": current_price,
        "avg_price": round(avg_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "trend": trend,
        "recommendation": recommendation,
        "reason": reason,
        "data_points": len(prices),
    }


@router.post("/seed/{item_id}")
def seed_mock_data(item_id: int, db: Session = Depends(get_session)):
    """Generate mock price history for demo purposes"""
    item = db.get(TrackedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Clear existing history
    existing = db.exec(
        select(PriceHistory).where(PriceHistory.item_id == item_id)
    ).all()
    for h in existing:
        db.delete(h)

    # Generate 10 data points over 10 days
    base_price = random.uniform(50, 200)
    now = datetime.utcnow()

    for i in range(10):
        price = base_price + random.uniform(-20, 20)
        if price < 10:
            price = 10
        history = PriceHistory(
            item_id=item_id,
            price=Decimal(str(round(price, 2))),
            currency="USD",
            in_stock=True,
            checked_at=now - timedelta(days=10 - i),
        )
        db.add(history)

    # Update current price
    item.current_price = Decimal(str(round(base_price + random.uniform(-5, 5), 2)))

    db.commit()
    return {"status": "seeded", "data_points": 10}


def _generate_mock_history(current_price: Decimal) -> list:
    """Generate mock history for analysis"""
    prices = []
    base = float(current_price) if current_price > 0 else 100
    now = datetime.utcnow()

    for i in range(10):
        price = base + random.uniform(-30, 30)
        if price < 10:
            price = 10
        prices.append(
            PriceHistory(
                price=Decimal(str(round(price, 2))),
                checked_at=now - timedelta(days=10 - i),
            )
        )

    return prices

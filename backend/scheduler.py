from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session, select
from database import engine
from models import TrackedItem, PriceHistory
from services.price_checker import fetch_price
import asyncio


async def check_all_prices():
    """Check prices for all active items"""
    with Session(engine) as db:
        statement = select(TrackedItem).where(TrackedItem.is_active == True)
        items = db.exec(statement).all()

        for item in items:
            new_price = await fetch_price(item.url, item.store)

            if new_price:
                old_price = item.current_price
                item.current_price = new_price

                history = PriceHistory(
                    item_id=item.id,
                    price=new_price,
                    currency="USD",
                    in_stock=True,
                )
                db.add(history)

                if old_price > 0 and new_price < old_price:
                    print(f"Price dropped for {item.name}: ${old_price} -> ${new_price}")

                db.commit()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_all_prices,
        trigger=IntervalTrigger(minutes=15),
        id="price_check",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler

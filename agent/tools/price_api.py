import httpx
from config import settings


async def get_price_history(item_id: int) -> list:
    """Fetch price history for an item from backend"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BACKEND_URL}/api/items/{item_id}/history"
        )
        response.raise_for_status()
        return response.json()


async def get_item_info(item_id: int) -> dict:
    """Fetch item info from backend"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BACKEND_URL}/api/items/",
            params={"user_id": 1},
        )
        response.raise_for_status()
        items = response.json()
        for item in items:
            if item["id"] == item_id:
                return item
        return {}

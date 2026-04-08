import httpx


class PriceTrackerAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_items(self, user_id: int) -> list:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.base_url}/api/items/", params={"user_id": user_id}
            )
            res.raise_for_status()
            return res.json()

    async def create_item(self, user_id: int, item_data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.base_url}/api/items/?user_id={user_id}", json=item_data
            )
            res.raise_for_status()
            return res.json()

    async def delete_item(self, item_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.delete(f"{self.base_url}/api/items/{item_id}")
            res.raise_for_status()
            return res.json()

    async def update_target_price(self, item_id: int, target_price: float) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.patch(
                f"{self.base_url}/api/items/{item_id}/target",
                params={"target_price": target_price}
            )
            res.raise_for_status()
            return res.json()

    async def get_all_items(self) -> list:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/api/items/all")
            res.raise_for_status()
            return res.json()

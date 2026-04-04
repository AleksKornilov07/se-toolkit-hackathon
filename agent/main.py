from openai import OpenAI
from config import settings
from tools.price_api import get_price_history, get_item_info

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


def analyze_price_trend(item_id: int) -> str:
    """Analyze price history and give buy/wait recommendation"""
    import asyncio

    async def _analyze():
        history = await get_price_history(item_id)
        item = await get_item_info(item_id)

        if len(history) < 2:
            return "Not enough price history to analyze. Check back later!"

        prices = [h["price"] for h in history]
        current_price = prices[-1]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        trend = "falling" if prices[-1] < prices[0] else "rising"

        prompt = f"""
You are a price analysis assistant. Analyze this product price history:

Product: {item.get('name', 'Unknown')}
Current price: ${current_price}
Average price: ${avg_price:.2f}
Lowest price: ${min_price}
Highest price: ${max_price}
Trend: {trend}
Price history (oldest to newest): {prices}

Give a clear recommendation:
1. BUY NOW or WAIT
2. Brief explanation why
3. If waiting, what price would be a good deal

Be concise and helpful.
"""

        response = client.chat.completions.create(
            model="qwen-2.5-72b-instruct",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    return asyncio.run(_analyze())

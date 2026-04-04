import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import settings
from services.api_client import PriceTrackerAPI

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
api = PriceTrackerAPI(settings.BACKEND_URL)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Welcome to PriceTracker Bot!\n\n"
        "I help you track product prices and notify you when they drop.\n\n"
        "Commands:\n"
        "/add — Add item to track\n"
        "/myitems — View your tracked items\n"
        "/help — Help"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📦 PriceTracker Help\n\n"
        "1. Use /add to start tracking a product\n"
        "2. Send me a product URL\n"
        "3. I'll notify you when the price drops!\n\n"
        "Commands:\n"
        "/add — Add new item\n"
        "/myitems — Your tracked items\n"
        "/stop <id> — Stop tracking an item"
    )


@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    await message.answer("📎 Send me the product URL you want to track:")


@dp.message(Command("myitems"))
async def cmd_myitems(message: types.Message):
    try:
        items = await api.get_items(message.from_user.id)
        if not items:
            await message.answer(
                "You have no tracked items. Use /add to start tracking."
            )
            return

        text = "📦 Your tracked items:\n\n"
        for item in items:
            status = "✅" if item["is_active"] else "⏸️"
            text += f"{status} **{item['name']}**\n"
            text += f"   Price: ${item['current_price']}\n"
            text += f"   ID: {item['id']}\n\n"

        await message.answer(text)
    except Exception as e:
        await message.answer(f"Error fetching items: {e}")


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /stop <item_id>\nExample: /stop 5")
        return

    try:
        item_id = int(args[1])
        await api.delete_item(item_id)
        await message.answer(f"✅ Item {item_id} removed from tracking.")
    except ValueError:
        await message.answer("Invalid item ID. Use a number.")
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message()
async def handle_url(message: types.Message):
    if not message.text or not message.text.startswith("http"):
        await message.answer(
            "Please send a valid product URL starting with http:// or https://"
        )
        return

    try:
        item_data = {
            "name": "Product",
            "url": message.text,
            "store": "generic",
        }
        await api.create_item(message.from_user.id, item_data)
        await message.answer(
            "✅ Item added! I'll track the price.\n"
            "Use /myitems to see your tracked items."
        )
    except Exception as e:
        await message.answer(f"Error adding item: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

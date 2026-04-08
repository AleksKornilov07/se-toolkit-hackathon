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

# Кэш: user_id -> {item_id: last_price}
user_price_cache = {}
# Множество уведомлённых: user_id -> set(item_id)
notified_items = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    # Инициализируем кэш для пользователя
    if user_id not in user_price_cache:
        user_price_cache[user_id] = {}
    await message.answer(
        f"👋 Welcome to PriceTracker Bot!\n\n"
        f"🔑 Your User ID: `{user_id}`\n"
        f"Use this ID to log in on the website.\n\n"
        f"I help you track product prices and notify you when they drop.\n\n"
        f"Commands:\n"
        f"/add — Add item to track\n"
        f"/myitems — View your tracked items\n"
        f"/id — Show your User ID\n"
        f"/help — Help",
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📦 PriceTracker Help\n\n"
        "1. Use /add to start tracking a product\n"
        "2. Send me a product URL\n"
        "3. Set a target price with /setnewprice\n"
        "4. I'll notify you when the price drops below your target!\n\n"
        "Commands:\n"
        "/start — Start bot and get your ID\n"
        "/id — Show your User ID\n"
        "/add — Add new item\n"
        "/myitems — Your tracked items\n"
        "/setnewprice <id> <price> — Set target price alert\n"
        "/stop <id> — Stop tracking an item"
    )


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(
        f"🔑 Your Telegram User ID: `{message.from_user.id}`\n\n"
        f"Use this ID to log in on the website.",
        parse_mode="Markdown"
    )


pending_items = {}

@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    pending_items[message.from_user.id] = {}
    await message.answer("📎 Send me the product URL you want to track:")


@dp.message(Command("myitems"))
async def cmd_myitems(message: types.Message):
    try:
        user_id = message.from_user.id
        items = await api.get_items(user_id)
        if not items:
            await message.answer(
                "You have no tracked items. Use /add to start tracking."
            )
            return

        text = "📦 Your tracked items:\n\n"
        for item in items:
            status = "✅" if item["is_active"] else "⏸️"
            target = item.get("target_price")
            target_str = f" | Target: ${target:.2f}" if target else ""
            text += f"{status} **{item['name']}**\n"
            text += f"   Price: ${item['current_price']}{target_str}\n"
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


@dp.message(Command("setnewprice"))
async def cmd_setprice(message: types.Message):
    """Set target price: /setnewprice <item_id> <price>"""
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "Usage: `/setnewprice <item_id> <target_price>`\n\n"
            "Example: `/setnewprice 5 40.00`\n"
            "I'll notify you when the price falls below $40.00",
            parse_mode="Markdown"
        )
        return

    try:
        item_id = int(args[1])
        target = float(args[2])
        user_id = message.from_user.id

        # Обновляем в БД
        await api.update_target_price(item_id, target)

        # Сбрасываем уведомление — пусть снова пришлёт при падении
        if user_id in notified_items:
            notified_items[user_id].discard(item_id)

        await message.answer(
            f"🎯 Target price updated!\n\n"
            f"Item ID: {item_id}\n"
            f"New target: ${target:.2f}"
        )
    except ValueError:
        await message.answer("Invalid format. Use: /setnewprice <item_id> <price>\nExample: /setnewprice 5 40.00")
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message()
async def handle_user_input(message: types.Message):
    if not message.text:
        return
    if message.text.startswith("/"):
        return
    
    user_id = message.from_user.id
    
    # Если пользователь в процессе добавления (отправил URL)
    if user_id in pending_items and 'url' in pending_items[user_id]:
        # Это целевая цена
        try:
            target = float(message.text)
            item_info = pending_items[user_id]
            
            item = await api.create_item(user_id, {
                "name": item_info.get("name", "Product"),
                "url": item_info["url"],
                "store": "generic",
                "target_price": target,
            })
            
            # Запоминаем цену
            if user_id not in user_price_cache:
                user_price_cache[user_id] = {}
            user_price_cache[user_id][item['id']] = float(item['current_price'])
            
            # Инициализируем notified set
            if user_id not in notified_items:
                notified_items[user_id] = set()
            
            del pending_items[user_id]
            
            await message.answer(
                f"✅ Item added with target price!\n\n"
                f"Name: {item['name']}\n"
                f"Current: ${item['current_price']}\n"
                f"Target: ${target:.2f}\n"
                f"I'll notify you when price drops below ${target:.2f}."
            )
        except ValueError:
            await message.answer("Invalid price. Please enter a number (e.g., 40.00):")
        except Exception as e:
            await message.answer(f"Error: {e}")
            del pending_items[user_id]
    elif message.text.startswith("http"):
        # Начало добавления — запомнить URL
        pending_items[user_id] = {
            "url": message.text,
            "name": "Product",
        }
        await message.answer("💰 Now enter your target price (e.g., 40.00):")
    else:
        await message.answer(
            "Please send a product URL (http://...).\n"
            "Use /add to start tracking."
        )


async def price_monitor():
    """Проверяет цены каждые 2 мин. Уведомляет ОДИН РАЗ при падении ниже целевой."""
    print("Price monitor started")
    while True:
        await asyncio.sleep(120)
        try:
            all_items = await api.get_all_items()

            for item in all_items:
                uid = item['user_id']
                item_id = item['id']
                current = float(item['current_price'])
                target = item.get('target_price')

                if current <= 0:
                    continue

                if uid not in user_price_cache:
                    user_price_cache[uid] = {}
                if uid not in notified_items:
                    notified_items[uid] = set()

                old = user_price_cache[uid].get(item_id)

                # Уведомляем только если цена упала ниже целевой И ещё не уведосли
                if target and current < target and item_id not in notified_items[uid]:
                    try:
                        await bot.send_message(
                            chat_id=uid,
                            text=f"🎯 Target reached!\n\n📦 {item['name']}\nTarget: ${target:.2f}\nNow: ${current:.2f}"
                        )
                        print(f"[NOTIFIED] user {uid} {item['name']}: ${current} < ${target}")
                        notified_items[uid].add(item_id)
                    except Exception as send_err:
                        print(f"Failed to notify user {uid}: {send_err}")

                user_price_cache[uid][item_id] = current

        except Exception as e:
            print(f"Monitor error: {e}")


async def main():
    # Сначала заполняем кэш текущими ценами
    try:
        all_items = await api.get_all_items()
        for item in all_items:
            uid = item['user_id']
            if uid not in user_price_cache:
                user_price_cache[uid] = {}
            user_price_cache[uid][item['id']] = float(item['current_price'])
            if uid not in notified_items:
                notified_items[uid] = set()
        print(f"Cache filled: {len(all_items)} items")
    except Exception as e:
        print(f"Cache fill error: {e}")
    
    asyncio.create_task(price_monitor())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

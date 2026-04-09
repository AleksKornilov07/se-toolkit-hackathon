# PriceTracker

AI-powered price tracker that monitors product prices and notifies users when prices drop below their target.

## Demo

![PriceTracker Dashboard](https://via.placeholder.com/800x400/3b82f6/ffffff?text=PriceTracker+Dashboard)

*Screenshot: Main dashboard with price history chart and AI-powered buy/wait recommendation.*

![Telegram Bot Notifications](https://via.placeholder.com/400x300/10b981/ffffff?text=Telegram+Bot+Notifications)

*Screenshot: Telegram bot showing price drop notification.*

## Context

### End Users
Online shoppers who want to save money by tracking product prices and buying at the best moment.

### Problem
Product prices fluctuate constantly across online stores. Shoppers waste time manually checking prices and miss the best moments to buy.

### Solution
PriceTracker automatically monitors prices 24/7 and sends Telegram notifications when prices drop below the user's target. An AI agent analyzes price trends and recommends the best time to buy.

## Features

### Implemented ✅
- **Product Tracking** — Add products by URL, automatic price parsing
- **Price History** — Interactive charts showing price changes over time
- **Target Price Alerts** — Set your desired price, get notified when it's reached (one-time notification)
- **AI Price Advisor** — Analyzes price trends, recommends BUY NOW or WAIT
- **Telegram Bot** — Add items, view tracked items, receive notifications via Telegram
- **Web Dashboard** — View items, charts, AI analysis, manage target prices
- **Multi-Currency Support** — Automatically detects $, £, € symbols
- **User Authentication** — Login via Telegram User ID
- **Scheduled Monitoring** — Prices checked every 5 minutes
- **Demo Data Generation** — Simulate price history for demonstration

### Not Yet Implemented 🚧
- Email notifications
- Browser extension for 1-click item addition
- Mobile app (React Native)
- Multi-store price comparison
- Historical savings statistics

## Usage

### Web App
1. Open `http://your-vm-ip:3000`
2. Enter your Telegram User ID (get it from `/start` in the bot)
3. Add a product URL and your target price
4. View price charts and AI recommendations

### Telegram Bot
1. Send `/start` to the bot — get your User ID
2. Send `/add` — bot asks for product URL
3. Send the URL — bot asks for target price
4. Enter target price — bot confirms tracking
5. Bot notifies you when price drops below target

**Bot Commands:**
| Command | Description |
|---|---|
| `/start` | Start bot, get your User ID |
| `/id` | Show your User ID |
| `/add` | Add a product to track |
| `/myitems` | View your tracked items |
| `/setnewprice <id> <price>` | Update target price |
| `/stop <id>` | Stop tracking an item |
| `/help` | Show all commands |

## Deployment

### VM Requirements
- **OS:** Ubuntu 24.04 LTS
- **Pre-installed:** Docker, Docker Compose Plugin

### Step-by-Step Deployment

#### 1. Install Docker on VM
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and log back in for group changes to take effect.

#### 2. Clone the Repository
```bash
cd ~
git clone https://github.com/AleksKornilov07/se-toolkit-hackathon.git price-tracker
cd price-tracker
```

#### 3. Create Environment File
```bash
nano .env
```

Add the following:
```env
POSTGRES_USER=pricetracker
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=pricetracker
DATABASE_URL=postgresql://pricetracker:your_secure_password@db:5432/pricetracker
SECRET_KEY=your_secret_key
OPENROUTER_API_KEY=your_openrouter_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

#### 4. Start All Services
```bash
docker compose up -d --build
```

#### 5. Verify Deployment
```bash
docker compose ps
curl http://localhost:8000/health
```

Expected output: `{"status":"ok"}`

#### 6. Configure Reverse Proxy (Optional)
For HTTPS access, configure Caddy:
```bash
# Edit Caddyfile
nano Caddyfile
# Add your domain:
# your-domain.com {
#     reverse_proxy /api/* backend:8000
#     reverse_proxy /* frontend:3000
# }
docker compose restart caddy
```

#### 7. Start Telegram Bot (Local Machine)
The bot runs on your local machine (Telegram is blocked on university VMs).

```bash
cd bot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env
echo "TELEGRAM_BOT_LINK=https://t.me/PriceTracker240783_bot" > .env
echo "BACKEND_URL=http://10.93.25.235:8000" >> .env
echo "FRONTEND_URL=http://10.93.25.235:3000/" >> .

python main.py
```

### Service Architecture
```
University VM:
  ├── Backend (FastAPI) :8000
  ├── Frontend (React) :3000
  ├── PostgreSQL (Database) :5432
  ├── AI Agent (nanobot)
  ├── Scheduler (APScheduler) — checks prices every 5 min
  └── Caddy (Reverse Proxy) — HTTPS

Local Machine:
  └── Telegram Bot (aiogram) — connects to VM via HTTP
```

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python + FastAPI + SQLModel |
| Database | PostgreSQL |
| Frontend | React + TypeScript + Chart.js |
| Bot | aiogram (Telegram) |
| AI Agent | nanobot + LLM API (OpenRouter) |
| Scheduler | APScheduler |
| Deployment | Docker Compose + Caddy |

## License
MIT — see [LICENSE](LICENSE) for details.

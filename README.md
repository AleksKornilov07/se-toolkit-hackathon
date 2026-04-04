# PriceTracker

AI-powered price tracking system that monitors product prices and notifies users when prices drop.

## One-Sentence Description

Tracks product prices across online stores and notifies you when they drop, with AI-powered recommendations on the best time to buy.

## Features

- **Web Dashboard** — Add products, view current prices, see interactive price history charts
- **Telegram Bot** — Track items via chat, receive price-drop notifications
- **AI Agent** — Get buy/wait recommendations based on price trend analysis
- **Automated Monitoring** — Scheduler checks prices every 5 minutes
- **Multi-Store Support** — Parse prices from Amazon, BestBuy, and other stores

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL 17 |
| Frontend | React + TypeScript + Chart.js |
| Telegram Bot | aiogram 3.x |
| AI Agent | OpenAI SDK + LLM |
| Scheduler | APScheduler |
| Deployment | Docker Compose + Caddy |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local bot)
- Telegram Bot Token (from @BotFather)

### Run Backend + Frontend (VM or Local)

```bash
docker compose up -d --build
```

- Web App: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Run Telegram Bot (Local)

```bash
cd bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
echo "BACKEND_URL=http://localhost:8000" >> .env

python main.py
```

### Run AI Agent (Local or VM)

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
echo "OPENROUTER_API_KEY=your_key_here" > .env
echo "BACKEND_URL=http://localhost:8000" >> .env

python main.py
```

## Project Structure

```
price-tracker/
├── backend/           # FastAPI application
│   ├── main.py        # Entry point
│   ├── models.py      # SQLModel database models
│   ├── schemas.py     # Pydantic schemas
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic (price checker)
│   └── scheduler.py   # APScheduler for price checks
├── frontend/          # React web application
│   └── src/
│       ├── App.tsx    # Main component
│       └── main.tsx   # Entry point
├── bot/               # Telegram bot (runs locally)
│   ├── main.py        # Bot entry point
│   └── services/      # API client
├── agent/             # AI price advisor
│   ├── main.py        # Agent entry point
│   └── tools/         # API tools for agent
├── docker-compose.yml # All services
└── Caddyfile          # Reverse proxy config
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/items/?user_id=1` | Add item to track |
| GET | `/api/items/?user_id=1` | Get all tracked items |
| GET | `/api/items/{id}/history` | Get price history |
| DELETE | `/api/items/{id}` | Remove item |
| GET | `/api/dashboard/stats?user_id=1` | Dashboard statistics |
| GET | `/health` | Health check |

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/add` | Add item to track |
| `/myitems` | View tracked items |
| `/stop <id>` | Stop tracking item |
| `/help` | Help message |

## Deployment

### University VM Setup

1. Clone repository
2. Create `.env` files in `backend/`, `bot/`, `agent/`
3. Run `docker compose up -d --build`
4. Configure Caddy with your domain
5. Run bot locally and point to VM backend URL

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql+asyncpg://pricetracker:password@db:5432/pricetracker
SECRET_KEY=your_secret_key
BACKEND_URL=http://localhost:8000
```

**Bot (.env):**
```
TELEGRAM_BOT_TOKEN=your_bot_token
BACKEND_URL=https://your-vm-domain.com
```

**Agent (.env):**
```
OPENROUTER_API_KEY=your_api_key
BACKEND_URL=http://backend:8000
```

## Version 1 vs Version 2

### Version 1 (Lab Demo)
- Add product by URL
- View tracked items list
- View price history chart
- Delete items
- Scheduler checks prices every 5 min

### Version 2 (Final Deploy)
- AI agent with price trend analysis
- Target price alerts via Telegram
- Multi-store parsing (Amazon, BestBuy)
- Polished UI with savings statistics
- Full HTTPS deployment on VM

## License

MIT

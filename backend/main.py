from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_db_and_tables
from routers import items, dashboard
from scheduler import start_scheduler

scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    create_db_and_tables()
    scheduler = start_scheduler()
    yield
    if scheduler:
        scheduler.shutdown()


app = FastAPI(title="PriceTracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

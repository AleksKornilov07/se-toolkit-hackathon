from sqlmodel import SQLModel, create_engine, Session
from config import settings

# Use SQLite for local dev, PostgreSQL for production
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgresql"):
    DATABASE_URL = db_url
else:
    DATABASE_URL = "sqlite:///./pricetracker.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

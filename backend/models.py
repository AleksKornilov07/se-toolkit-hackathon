from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Numeric
from decimal import Decimal


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    items: list["TrackedItem"] = Relationship(back_populates="user")


class TrackedItem(SQLModel, table=True):
    __tablename__ = "tracked_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    url: str
    store: str
    current_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    target_price: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2), nullable=True))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="items")
    history: list["PriceHistory"] = Relationship(back_populates="item")


class PriceHistory(SQLModel, table=True):
    __tablename__ = "price_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="tracked_items.id", ondelete="CASCADE")
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="USD")
    in_stock: bool = Field(default=True)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    item: Optional[TrackedItem] = Relationship(back_populates="history")

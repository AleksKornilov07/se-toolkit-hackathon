from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class ItemCreate(BaseModel):
    name: str
    url: str
    store: str
    target_price: float | None = None


class ItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    url: str
    store: str
    current_price: float
    target_price: float | None
    is_active: bool
    created_at: datetime


class PriceHistoryResponse(BaseModel):
    id: int
    item_id: int
    price: float
    currency: str
    in_stock: bool
    checked_at: datetime

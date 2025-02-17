from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class AppBase(BaseModel):
    name: str
    app_id: str
    rating: Optional[Decimal] = None
    rating_count: Optional[int] = None
    installs: Optional[str] = None
    min_installs: Optional[int] = None
    max_installs: Optional[int] = None
    is_free: bool
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    size: Optional[str] = None
    min_android: Optional[str] = None
    released_date: Optional[date] = None
    last_updated: Optional[date] = None
    content_rating: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    has_ads: Optional[bool] = None
    has_in_app_purchases: Optional[bool] = None
    is_editors_choice: Optional[bool] = None

class AppCreate(AppBase):
    category_id: int
    developer_id: int

class App(AppBase):
    id: int
    category_id: int
    developer_id: int
    scraped_time: datetime

    model_config = {
        'from_attributes': True
    }

class AppList(BaseModel):
    id: int
    name: str
    app_id: str
    rating: Optional[Decimal] = None
    rating_count: Optional[int] = None
    installs: Optional[str] = None
    is_free: bool
    price: Optional[Decimal] = None
    released_date: Optional[date] = None
    last_updated: Optional[date] = None
    content_rating: Optional[str] = None
    category_id: int
    developer_id: int

    model_config = {
        'from_attributes': True
    }

class AppDetail(App):
    category: 'Category'
    developer: 'Developer'

    model_config = {
        'from_attributes': True
    }

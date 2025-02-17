from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    model_config = {
        'from_attributes': True
    }

class CategoryWithApps(Category):
    apps: List['App'] = []

    model_config = {
        'from_attributes': True
    }

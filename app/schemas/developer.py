from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict

class DeveloperBase(BaseModel):
    name: str
    website: Optional[str] = None
    email: Optional[str] = None

class DeveloperCreate(DeveloperBase):
    pass

class Developer(DeveloperBase):
    id: int

    model_config = {
        'from_attributes': True
    }

class DeveloperWithApps(Developer):
    apps: List['App'] = []

    model_config = {
        'from_attributes': True
    }

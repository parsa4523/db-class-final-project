from .app import App, AppCreate, AppDetail, AppList
from .category import Category, CategoryCreate, CategoryWithApps
from .developer import Developer, DeveloperCreate, DeveloperWithApps

from pydantic import BaseModel, Field
from typing import TypeVar, Generic

T = TypeVar("T")

class MetadataModel(BaseModel):
    query_duration_ms: float = Field(..., description="Time taken to process the query in milliseconds")

class ResponseModel(BaseModel, Generic[T]):
    data: T
    metadata: MetadataModel


# Update forward references for nested models
App.model_rebuild()
Category.model_rebuild()
Developer.model_rebuild()
AppDetail.model_rebuild()
AppList.model_rebuild()
CategoryWithApps.model_rebuild()
DeveloperWithApps.model_rebuild()



__all__ = [
    "App", "AppCreate", "AppDetail", "AppList",
    "Category", "CategoryCreate", "CategoryWithApps",
    "Developer", "DeveloperCreate", "DeveloperWithApps", "ResponseModel"
]

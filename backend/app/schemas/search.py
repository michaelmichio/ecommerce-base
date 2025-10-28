from pydantic import BaseModel
from typing import List, Optional, Any, Union

class SortField(BaseModel):
    field: str
    direction: str = "asc"  # asc | desc

class SearchField(BaseModel):
    value: str
    fields: Optional[List[str]] = ["name", "description"]

class FilterField(BaseModel):
    field: str
    operator: str = "eq"  # eq | like | between | gt | lt
    value: Any

class ProductSearchRequest(BaseModel):
    page: int = 1
    limit: int = 10
    sort: Optional[List[SortField]] = None
    search: Optional[SearchField] = None
    filters: Optional[List[FilterField]] = None

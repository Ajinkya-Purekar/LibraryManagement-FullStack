from pydantic import BaseModel
from typing import Optional,List

from app.schemas.category_schema import CategoryResponse


# ---------------- BASE ----------------
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    total_copies: int
    category_id: int


# ---------------- CREATE ----------------
class BookCreate(BookBase):
    pass


# ---------------- UPDATE ----------------
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    total_copies: Optional[int] = None
    category_id: Optional[int] = None


# ---------------- RESPONSE ----------------
class BookResponse(BookBase):
    id: int
    available_copies: int
    category: CategoryResponse

    class Config:
        from_attributes = True

# ---------------PAGINATED RESPONSE -------------
class PaginatedBooksResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    pages: int
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book_schema import BookCreate, BookUpdate, BookResponse, PaginatedBooksResponse
from app.core.security import get_current_user

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

# ---------------- CREATE BOOK (ADMIN ONLY) ----------------
@router.post("/", response_model=BookResponse)
def add_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN can add books")

    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

    new_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        total_copies=book.total_copies,
        available_copies=book.total_copies,
        category_id=book.category_id
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# ---------------- GET BOOKS (SEARCH + FILTER + PAGINATION) ----------------
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from fastapi import Query, Depends
from sqlalchemy.orm import Session

@router.get("/")
def get_books(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),
    sort_by: str = Query("title"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # IMPORTANT: joinedload category
    query = db.query(Book).options(joinedload(Book.category))

    # SEARCH
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )

    # CATEGORY FILTER
    if category_id:
        query = query.filter(Book.category_id == category_id)

    # TOTAL COUNT (before pagination)
    total = query.count()

    # SORTING (safe fallback)
    sort_column = getattr(Book, sort_by, Book.title)
    sort_column = sort_column.desc() if order == "desc" else sort_column.asc()
    query = query.order_by(sort_column)

    # PAGINATION
    books = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "data": books,
        "total": total,
        "page": page,
        "size": size
    }



# ---------------- UPDATE BOOK (ADMIN ONLY) ----------------
@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN can update books")

    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.title is not None:
        db_book.title = book.title
    if book.author is not None:
        db_book.author = book.author
    if book.category_id is not None:
        db_book.category_id = book.category_id
    if book.total_copies is not None:
        diff = book.total_copies - db_book.total_copies
        db_book.total_copies = book.total_copies
        db_book.available_copies += diff

    db.commit()
    db.refresh(db_book)
    return db_book


# ---------------- DELETE BOOK (ADMIN ONLY) ----------------
@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN can delete books")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

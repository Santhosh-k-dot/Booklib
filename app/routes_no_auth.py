from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User, Book, Transaction, UserRole, TransactionStatus
from app.schemas import (
    UserCreate, UserResponse,
    BookCreate, BookUpdate, BookResponse,
    BorrowBook, TransactionResponse,
    UserLogin, Token
)
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin
)

router = APIRouter()

# ===================== AUTH (PUBLIC) =====================

@router.post("/register", response_model=UserResponse)
def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "Username already taken")

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=UserRole.USER
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not db_user or not verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(db_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
# ===================== BOOKS =====================

@router.get("/books", response_model=List[BookResponse])
@cache(expire=60)
async def get_books(
    request: Request,
    db: Session = Depends(get_db)
):
    return db.query(Book).all()


@router.get("/books/{book_id}", response_model=BookResponse)
@cache(expire=60)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@router.post("/books", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(400, "Book with this ISBN already exists")

    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        total_copies=book.total_copies,
        available_copies=book.total_copies,
        description=book.description
    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    FastAPICache.clear()
    return db_book


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(404, "Book not found")

    if book.title:
        db_book.title = book.title
    if book.author:
        db_book.author = book.author
    if book.total_copies is not None:
        diff = book.total_copies - db_book.total_copies
        db_book.total_copies = book.total_copies
        db_book.available_copies += diff
    if book.description:
        db_book.description = book.description

    db.commit()
    db.refresh(db_book)

    FastAPICache.clear()
    return db_book


@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    db.delete(book)
    db.commit()

    FastAPICache.clear()
    return {"message": "Book deleted successfully"}

# ===================== TRANSACTIONS =====================

@router.post("/borrow", response_model=TransactionResponse)
def borrow_book(
    borrow: BorrowBook,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")

    if book.available_copies <= 0:
        raise HTTPException(400, "Book not available")

    existing = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.book_id == borrow.book_id,
        Transaction.status == TransactionStatus.BORROWED
    ).first()

    if existing:
        raise HTTPException(400, "Book already borrowed")

    transaction = Transaction(
        user_id=current_user.id,
        book_id=borrow.book_id,
        status=TransactionStatus.BORROWED
    )

    book.available_copies -= 1
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.post("/return/{transaction_id}", response_model=TransactionResponse)
def return_book(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(404, "Transaction not found")

    if transaction.status == TransactionStatus.RETURNED:
        raise HTTPException(400, "Book already returned")

    transaction.status = TransactionStatus.RETURNED
    transaction.return_date = datetime.utcnow()

    book = db.query(Book).filter(Book.id == transaction.book_id).first()
    book.available_copies += 1

    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/transactions/my", response_model=List[TransactionResponse])
def my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()


@router.get("/transactions", response_model=List[TransactionResponse])
def all_transactions(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(Transaction).all()


@router.get("/users", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(User).all()
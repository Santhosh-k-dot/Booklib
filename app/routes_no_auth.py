from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

# from app.rate_limiter import limiter

from app.database import get_db
from app.models import User, Book, Transaction, UserRole, TransactionStatus
from app.schemas import (
    UserCreate, UserResponse,
    BookCreate, BookUpdate, BookResponse,
    BorrowBook, TransactionResponse,
    UserLogin, Token,
    RefreshRequest
)
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_admin
)

router = APIRouter()

# ===================== AUTH (PUBLIC) =====================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/hour")
def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken")

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
# @limiter.limit("10/hour")
def login(
    request: Request,
    username: str = Form(...),          # Manually extract username from application/x-www-form-urlencoded body
    password: str = Form(...),          # Manually extract password from application/x-www-form-urlencoded body
    db: Session = Depends(get_db)
):
    """
    Accepts the same content-type as OAuth2PasswordRequestForm (application/x-www-form-urlencoded)
    but reads fields manually via FastAPI's Form() — no OAuth2PasswordRequestForm dependency needed.
    Clients send: username=foo&password=bar in the request body.
    """
    db_user = db.query(User).filter(User.username == username).first()

    # Single combined check to prevent user enumeration attacks
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token  = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer"
    }


@router.post("/refresh", response_model=Token)
# @limiter.limit("20/hour")
def refresh(
    request: Request,
    payload: RefreshRequest,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    data = verify_token(payload.refresh_token)

    if data is None:
        raise credentials_exception
    if data.get("type") != "refresh":
        raise credentials_exception
    if data.get("sub") is None:
        raise credentials_exception

    new_access  = create_access_token({"sub": data["sub"]})
    new_refresh = create_refresh_token({"sub": data["sub"]})

    return {
        "access_token":  new_access,
        "refresh_token": new_refresh,
        "token_type":    "bearer"
    }


# ===================== BOOKS =====================

@router.get("/books", response_model=List[BookResponse])
# @limiter.limit("1000/hour")
@cache(expire=60)
async def get_books(
    request: Request,
    db: Session = Depends(get_db)
):
    return db.query(Book).all()


@router.get("/books/{book_id}", response_model=BookResponse)
# @limiter.limit("1000/hour")
@cache(expire=60)
def get_book(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("100/hour")
async def create_book(
    request: Request,
    book: BookCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Book with this ISBN already exists")

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

    await FastAPICache.clear()
    return db_book


@router.put("/books/{book_id}", response_model=BookResponse)
# @limiter.limit("100/hour")
async def update_book(
    request: Request,
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    if book.title is not None:
        db_book.title = book.title
    if book.author is not None:
        db_book.author = book.author
    if book.total_copies is not None:
        diff = book.total_copies - db_book.total_copies
        if db_book.available_copies + diff < 0:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Cannot reduce total_copies: {-diff} copies are currently borrowed"
            )
        db_book.total_copies     = book.total_copies
        db_book.available_copies += diff
    if book.description is not None:
        db_book.description = book.description

    db.commit()
    db.refresh(db_book)

    await FastAPICache.clear()
    return db_book


@router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("50/hour")
async def delete_book(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    if book.available_copies < book.total_copies:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cannot delete book: some copies are currently borrowed"
        )

    db.delete(book)
    db.commit()

    await FastAPICache.clear()
    return {"message": "Book deleted successfully"}


# ===================== TRANSACTIONS =====================

@router.post("/borrow", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("50/hour")
def borrow_book(
    request: Request,
    borrow: BorrowBook,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    if book.available_copies <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Book not available")

    existing = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.book_id == borrow.book_id,
        Transaction.status == TransactionStatus.BORROWED
    ).first()

    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You already have this book borrowed")

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
# @limiter.limit("50/hour")
def return_book(
    request: Request,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")

    if transaction.status == TransactionStatus.RETURNED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Book already returned")

    transaction.status      = TransactionStatus.RETURNED
    transaction.return_date = datetime.utcnow()

    book = db.query(Book).filter(Book.id == transaction.book_id).first()
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Associated book not found")
    book.available_copies += 1

    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/transactions/my", response_model=List[TransactionResponse])
# @limiter.limit("100/hour")
def my_transactions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()


@router.get("/transactions", response_model=List[TransactionResponse])
# @limiter.limit("500/hour")
def all_transactions(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(Transaction).all()


@router.get("/users", response_model=List[UserResponse])
# @limiter.limit("500/hour")
def get_users(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(User).all()
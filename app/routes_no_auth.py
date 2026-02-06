from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import User, Book, Transaction, UserRole, TransactionStatus
from app.schemas import (
    UserCreate, UserResponse,
    BookCreate, BookUpdate, BookResponse,
    BorrowBook, TransactionResponse,
    UserLogin, Token
)
from app.auth import get_password_hash,verify_password, create_access_token

router = APIRouter()

# ============= USER ROUTES (NO AUTH) =============

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user - --"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
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
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": db_user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }   

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Get all users - --"""
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID - --"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ============= BOOK ROUTES (NO AUTH) =============

@router.get("/books", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    """Get all books - --"""
    books = db.query(Book).all()
    return books

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get single book - --"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/books", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Add new book - --"""
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
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
    return db_book

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Update book - --"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.title:
        db_book.title = book.title
    if book.author:
        db_book.author = book.author
    if book.total_copies is not None:
        difference = book.total_copies - db_book.total_copies
        db_book.total_copies = book.total_copies
        db_book.available_copies += difference
    if book.description:
        db_book.description = book.description
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete book - --"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

# ============= TRANSACTION ROUTES (NO AUTH) =============

@router.post("/borrow/{user_id}", response_model=TransactionResponse)
def borrow_book(user_id: int, borrow: BorrowBook, db: Session = Depends(get_db)):
    """Borrow book - -- (specify user_id)"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if book exists
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if book is available
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    
    # Check if user already borrowed this book
    existing = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.book_id == borrow.book_id,
        Transaction.status == TransactionStatus.BORROWED
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already borrowed this book")
    
    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        book_id=borrow.book_id,
        status=TransactionStatus.BORROWED
    )
    
    # Decrease available copies
    book.available_copies -= 1
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.post("/return/{transaction_id}", response_model=TransactionResponse)
def return_book(transaction_id: int, db: Session = Depends(get_db)):
    """Return book - --"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.status == TransactionStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Update transaction
    transaction.return_date = datetime.utcnow()
    transaction.status = TransactionStatus.RETURNED
    
    # Increase available copies
    book = db.query(Book).filter(Book.id == transaction.book_id).first()
    book.available_copies += 1
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/transactions", response_model=List[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    """Get all transactions - --"""
    transactions = db.query(Transaction).all()
    return transactions

@router.get("/transactions/user/{user_id}", response_model=List[TransactionResponse])
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    """Get user's transactions - --"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return transactions

@router.get("/transactions/borrowed/{user_id}", response_model=List[TransactionResponse])
def get_user_borrowed_books(user_id: int, db: Session = Depends(get_db)):
    """Get user's currently borrowed books - --"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.status == TransactionStatus.BORROWED
    ).all()
    return transactions
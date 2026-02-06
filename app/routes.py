# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime

# from app.database import get_db
# from app.models import User, Book, Transaction, UserRole, TransactionStatus
# from app.schemas import (
#     UserCreate, UserLogin, UserResponse,
#     BookCreate, BookUpdate, BookResponse,
#     BorrowBook, TransactionResponse
# )
# from app.auth import (
#     get_password_hash, verify_password, create_access_token,
#     get_current_user, get_current_admin
# )

# router = APIRouter()

# # ============= AUTH ROUTES =============

# @router.post("/register", response_model=UserResponse)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     # Check if user exists
#     if db.query(User).filter(User.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")
#     if db.query(User).filter(User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="Username already taken")
    
#     # Create new user
#     db_user = User(
#         email=user.email,
#         username=user.username,
#         hashed_password=get_password_hash(user.password),
#         full_name=user.full_name,
#         role=UserRole.USER
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @router.post("/login")
# def login(user: UserLogin, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.username == user.username).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
    
#     access_token = create_access_token(data={"sub": db_user.username})
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/me", response_model=UserResponse)
# def get_me(current_user: User = Depends(get_current_user)):
#     return current_user

# # ============= BOOK ROUTES =============

# # Get all books (USER & ADMIN)
# @router.get("/books", response_model=List[BookResponse])
# def get_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     books = db.query(Book).all()
#     return books

# # Get single book (USER & ADMIN)
# @router.get("/books/{book_id}", response_model=BookResponse)
# def get_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")
#     return book

# # Add book (ADMIN ONLY)
# @router.post("/books", response_model=BookResponse)
# def create_book(book: BookCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
#     # Check if ISBN exists
#     if db.query(Book).filter(Book.isbn == book.isbn).first():
#         raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
#     db_book = Book(
#         title=book.title,
#         author=book.author,
#         isbn=book.isbn,
#         total_copies=book.total_copies,
#         available_copies=book.total_copies,
#         description=book.description
#     )
#     db.add(db_book)
#     db.commit()
#     db.refresh(db_book)
#     return db_book

# # Update book (ADMIN ONLY)
# @router.put("/books/{book_id}", response_model=BookResponse)
# def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
#     db_book = db.query(Book).filter(Book.id == book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     if book.title:
#         db_book.title = book.title
#     if book.author:
#         db_book.author = book.author
#     if book.total_copies:
#         # Adjust available copies
#         difference = book.total_copies - db_book.total_copies
#         db_book.total_copies = book.total_copies
#         db_book.available_copies += difference
#     if book.description:
#         db_book.description = book.description
    
#     db.commit()
#     db.refresh(db_book)
#     return db_book

# # Delete book (ADMIN ONLY)
# @router.delete("/books/{book_id}")
# def delete_book(book_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
#     db_book = db.query(Book).filter(Book.id == book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     db.delete(db_book)
#     db.commit()
#     return {"message": "Book deleted successfully"}

# # ============= TRANSACTION ROUTES =============

# # Borrow book (USER & ADMIN)
# @router.post("/borrow", response_model=TransactionResponse)
# def borrow_book(borrow: BorrowBook, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # Check if book exists
#     book = db.query(Book).filter(Book.id == borrow.book_id).first()
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     # Check if book is available
#     if book.available_copies <= 0:
#         raise HTTPException(status_code=400, detail="Book not available")
    
#     # Check if user already borrowed this book
#     existing = db.query(Transaction).filter(
#         Transaction.user_id == current_user.id,
#         Transaction.book_id == borrow.book_id,
#         Transaction.status == TransactionStatus.BORROWED
#     ).first()
    
#     if existing:
#         raise HTTPException(status_code=400, detail="You already borrowed this book")
    
#     # Create transaction
#     transaction = Transaction(
#         user_id=current_user.id,
#         book_id=borrow.book_id,
#         status=TransactionStatus.BORROWED
#     )
    
#     # Decrease available copies
#     book.available_copies -= 1
    
#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction

# # Return book (USER & ADMIN)
# @router.post("/return/{transaction_id}", response_model=TransactionResponse)
# def return_book(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")
    
#     if transaction.user_id != current_user.id and current_user.role != UserRole.ADMIN:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     if transaction.status == TransactionStatus.RETURNED:
#         raise HTTPException(status_code=400, detail="Book already returned")
    
#     # Update transaction
#     transaction.return_date = datetime.utcnow()
#     transaction.status = TransactionStatus.RETURNED
    
#     # Increase available copies
#     book = db.query(Book).filter(Book.id == transaction.book_id).first()
#     book.available_copies += 1
    
#     db.commit()
#     db.refresh(transaction)
#     return transaction

# # Get my borrowed books (USER)
# @router.get("/my-books", response_model=List[TransactionResponse])
# def get_my_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     transactions = db.query(Transaction).filter(
#         Transaction.user_id == current_user.id,
#         Transaction.status == TransactionStatus.BORROWED
#     ).all()
#     return transactions

# # Get all transactions (ADMIN ONLY)
# @router.get("/transactions", response_model=List[TransactionResponse])
# def get_all_transactions(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
#     transactions = db.query(Transaction).all()
#     return transactions

# # ============= USER MANAGEMENT (ADMIN ONLY) =============

# @router.get("/users", response_model=List[UserResponse])
# def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
#     users = db.query(User).all()
#     return users
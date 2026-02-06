from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# User roles
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

# Transaction status
class TransactionStatus(str, enum.Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"

# User table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    transactions = relationship("Transaction", back_populates="user")

# Book table
class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    transactions = relationship("Transaction", back_populates="book")

# Transaction table (Borrow/Return)
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.BORROWED)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    book = relationship("Book", back_populates="transactions")
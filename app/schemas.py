from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models import UserRole, TransactionStatus


# ========== USER SCHEMAS ==========
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


# ✅ UPDATED: now includes refresh_token
class Token(BaseModel):
    access_token: str
    refresh_token: str          # ✅ NEW
    token_type: str = "bearer"


# ✅ NEW: used by POST /refresh
class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole          # ✅ enum, not str
    is_active: bool

    class Config:
        from_attributes = True


# ========== BOOK SCHEMAS ==========
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    total_copies: int
    description: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    total_copies: Optional[int] = None
    description: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
    description: Optional[str]

    class Config:
        from_attributes = True


# ========== TRANSACTION SCHEMAS ==========
class BorrowBook(BaseModel):
    book_id: int


class TransactionResponse(BaseModel):
    id: int
    user_id: int            # ✅ strongly recommended
    book_id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    status: TransactionStatus   # ✅ enum, not str

    class Config:
        from_attributes = True
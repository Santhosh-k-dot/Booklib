from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

# Book schemas
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

# Transaction schemas
class BorrowBook(BaseModel):
    book_id: int

class TransactionResponse(BaseModel):
    id: int
    book_id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True
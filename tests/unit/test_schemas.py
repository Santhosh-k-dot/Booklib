import pytest
from datetime import datetime
from app.models import UserRole,TransactionStatus

from app.schemas import (
    UserCreate,
    UserLogin,
    Token,
    UserResponse,
    BookCreate,
    BookUpdate,
    BookResponse,
    BorrowBook,
    TransactionResponse,
)

# -------------------------
# USER SCHEMA TESTS
# -------------------------

def test_user_create_valid():
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="secret123",
        full_name="Test User"
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"


def test_user_create_invalid_email():
    with pytest.raises(Exception):
        UserCreate(
            email="not-an-email",
            username="testuser",
            password="secret123",
            full_name="Test User"
        )


def test_user_login_valid():
    login = UserLogin(username="admin", password="admin123")
    assert login.username == "admin"


def test_user_login_missing_password():
    with pytest.raises(Exception):
        UserLogin(username="admin")


def test_token_default_type():
    token = Token(access_token="abc123")
    assert token.token_type == "bearer"


def test_user_response_creation():
    user = UserResponse(
        id=1,
        email="user@example.com",
        username="user1",
        full_name="User One",
        role=UserRole.USER,   # ✅ FIX
        is_active=True
    )

    assert user.id == 1
    assert user.is_active is True
    assert user.role == UserRole.USER

# -------------------------
# BOOK SCHEMA TESTS
# -------------------------

def test_book_create_valid():
    book = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        isbn="1234567890",
        total_copies=10
    )

    assert book.title == "Clean Code"
    assert book.total_copies == 10


def test_book_create_missing_title():
    with pytest.raises(Exception):
        BookCreate(
            author="Robert Martin",
            isbn="1234567890",
            total_copies=10
        )


def test_book_create_invalid_total_copies():
    with pytest.raises(Exception):
        BookCreate(
            title="Clean Code",
            author="Robert Martin",
            isbn="1234567890",
            total_copies="ten"   # ❌ wrong type
        )


def test_book_update_partial():
    book = BookUpdate(title="New Title")
    assert book.title == "New Title"
    assert book.author is None


def test_book_response_creation():
    book = BookResponse(
        id=1,
        title="Clean Code",
        author="Robert Martin",
        isbn="1234567890",
        total_copies=10,
        available_copies=7,
        description=None
    )

    assert book.available_copies == 7


# -------------------------
# TRANSACTION SCHEMA TESTS
# -------------------------

def test_borrow_book_valid():
    borrow = BorrowBook(book_id=5)
    assert borrow.book_id == 5


def test_borrow_book_invalid_type():
    with pytest.raises(Exception):
        BorrowBook(book_id="five")


def test_transaction_response_valid():
    txn = TransactionResponse(
        id=1,
        user_id=1,                            # ✅ REQUIRED
        book_id=2,
        borrow_date=datetime.now(),
        return_date=None,
        status=TransactionStatus.BORROWED    # ✅ FIX
    )

    assert txn.status == TransactionStatus.BORROWED
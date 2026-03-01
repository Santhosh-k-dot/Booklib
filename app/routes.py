# from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime

# from fastapi_cache.decorator import cache
# from fastapi_cache import FastAPICache

# # from app.rate_limiter import limiter

# from app.database import get_db
# from app.models import User, Book, Transaction, UserRole, TransactionStatus
# from app.schemas import (
#     UserCreate, UserResponse,
#     BookCreate, BookUpdate, BookResponse,
#     BorrowBook, TransactionResponse,
#     UserLogin, Token,
#     RefreshRequest
# )
# from app.auth import (
#     get_password_hash,
#     verify_password,
#     create_access_token,
#     create_refresh_token,
#     verify_token,
#     get_current_user,
#     get_current_admin
# )

# router = APIRouter()
# # router is mounted in main.py with a prefix (e.g. /api) — all routes here become /api/...

# # ===================== AUTH (PUBLIC) =====================

# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# # @limiter.limit("5/hour")  # rate limit: max 5 registrations per IP per hour — uncomment to enable
# def register(
#     request: Request,      # required by rate limiter to extract client IP — kept even when limiter is disabled
#     user: UserCreate,      # validated JSON body: {email, username, password, full_name}
#     db: Session = Depends(get_db)
# ):
#     """
#     Workflow:
#     1. Check if email is already in use → 400 if taken (unique per user)
#     2. Check if username is already in use → 400 if taken (unique per user)
#     3. Hash the plain-text password before touching the DB — never store raw passwords
#     4. Create User ORM object with role=USER (all self-registered users start as regular users)
#     5. Add to DB, commit, refresh to get DB-generated fields (id, created_at, etc.)
#     6. Return the new user object — serialized via UserResponse schema (no password in output)
#     """
#     if db.query(User).filter(User.email == user.email).first():          # step 1: block duplicate email
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

#     if db.query(User).filter(User.username == user.username).first():    # step 2: block duplicate username
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken")

#     db_user = User(                                   # step 3+4: build User ORM object
#         email=user.email,
#         username=user.username,
#         hashed_password=get_password_hash(user.password),  # hash before storing — plain text never touches DB
#         full_name=user.full_name,
#         role=UserRole.USER                            # default role — admins must be promoted manually
#     )

#     db.add(db_user)       # step 5: stage insert
#     db.commit()           # write to DB — triggers DB defaults like id, created_at
#     db.refresh(db_user)   # reload from DB so response includes all generated fields
#     return db_user        # step 6: FastAPI serializes via UserResponse (excludes hashed_password)


# @router.post("/login", response_model=Token)
# # @limiter.limit("10/hour")  # rate limit: max 10 login attempts per IP per hour — uncomment to enable
# def login(
#     request: Request,
#     username: str = Form(...),     # read 'username' field from application/x-www-form-urlencoded body
#     password: str = Form(...),     # read 'password' field from application/x-www-form-urlencoded body
#     db: Session = Depends(get_db)
# ):
#     """
#     Workflow:
#     1. Read username + password from form body (application/x-www-form-urlencoded)
#     2. Look up user by username in DB
#     3. Verify password against stored hash — combine both checks into one response to prevent user enumeration
#     4. Issue a short-lived access token (30 min) signed with the user's DB ID as 'sub'
#     5. Issue a long-lived refresh token (7 days) — client stores this to silently renew access tokens
#     6. Return both tokens + token_type: 'bearer' (required by OAuth2 spec)
#     """
#     db_user = db.query(User).filter(User.username == username).first()  # step 2: look up by username

#     if not db_user or not verify_password(password, db_user.hashed_password):  # step 3: single check — avoids leaking if username exists
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",   # intentionally vague — don't reveal which field was wrong
#             headers={"WWW-Authenticate": "Bearer"},  # OAuth2 spec requires this header on 401
#         )

#     access_token  = create_access_token({"sub": str(db_user.id)})   # step 4: short-lived, used for API requests
#     refresh_token = create_refresh_token({"sub": str(db_user.id)})  # step 5: long-lived, used only for token renewal

#     return {                          # step 6: return token pair to client
#         "access_token":  access_token,
#         "refresh_token": refresh_token,  # client must store this securely (httpOnly cookie or secure storage)
#         "token_type":    "bearer"        # OAuth2 spec mandates this field
#     }


# @router.post("/refresh", response_model=Token)
# # @limiter.limit("20/hour")  # rate limit: max 20 refresh attempts per IP per hour — uncomment to enable
# def refresh(
#     request: Request,
#     payload: RefreshRequest,   # JSON body: {"refresh_token": "<token>"}
# ):
#     """
#     Workflow:
#     1. Decode and validate the submitted refresh token via verify_token()
#     2. Reject if invalid, expired, or tampered (verify_token returns None)
#     3. Reject if token type is not 'refresh' — access tokens cannot be used here
#     4. Reject if 'sub' claim is missing — malformed token
#     5. Issue a brand new access token + refresh token (token rotation — old refresh token is abandoned)
#     6. Return the new token pair — client must replace stored refresh token immediately
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid or expired refresh token",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     data = verify_token(payload.refresh_token)   # step 1+2: decode JWT — returns None if invalid/expired

#     if data is None:                             # step 2: token is expired, forged, or malformed
#         raise credentials_exception
#     if data.get("type") != "refresh":            # step 3: reject access tokens submitted to this endpoint
#         raise credentials_exception
#     if data.get("sub") is None:                  # step 4: malformed token — user ID claim is missing
#         raise credentials_exception

#     new_access  = create_access_token({"sub": data["sub"]})   # step 5: fresh 30-min access token
#     new_refresh = create_refresh_token({"sub": data["sub"]})  # step 5: fresh 7-day refresh token (old one abandoned)

#     return {                           # step 6: return rotated token pair
#         "access_token":  new_access,
#         "refresh_token": new_refresh,  # client must replace old refresh token with this immediately
#         "token_type":    "bearer"
#     }


# # ===================== BOOKS =====================

# @router.get("/books", response_model=List[BookResponse])
# # @limiter.limit("1000/hour")
# @cache(expire=60)   # cache response in Redis for 60 seconds — reduces repeated DB hits on this read-heavy endpoint
# async def get_books(
#     request: Request,   # required by @cache decorator to build a cache key from the request URL
#     db: Session = Depends(get_db)
# ):
#     """
#     Workflow:
#     1. Check cache — if a cached response exists (within 60s), return it immediately (no DB hit)
#     2. If not cached — query all books from DB
#     3. Return list — FastAPI serializes each book via BookResponse schema
#     4. Cache the response for the next 60 seconds automatically
#     """
#     return db.query(Book).all()  # step 2: full table scan — consider adding pagination for large datasets


# @router.get("/books/{book_id}", response_model=BookResponse)
# # @limiter.limit("1000/hour")
# @cache(expire=60)   # cache individual book lookup for 60 seconds — avoids repeated single-row queries
# def get_book(
#     request: Request,
#     book_id: int,       # path parameter — FastAPI auto-parses and validates as int
#     db: Session = Depends(get_db)
# ):
#     """
#     Workflow:
#     1. Check cache — return cached result if available (no DB hit)
#     2. Query DB for book by ID
#     3. Raise 404 if not found
#     4. Return book — serialized via BookResponse schema and cached for 60 seconds
#     """
#     book = db.query(Book).filter(Book.id == book_id).first()  # step 2: single row lookup by primary key
#     if not book:                                               # step 3: book doesn't exist
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
#     return book                                                # step 4: return and cache


# @router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
# # @limiter.limit("100/hour")
# async def create_book(
#     request: Request,
#     book: BookCreate,                               # JSON body: {title, author, isbn, total_copies, description}
#     db: Session = Depends(get_db),
#     admin: User = Depends(get_current_admin)        # authentication + admin role check runs first — 401/403 if fails
# ):
#     """
#     Workflow:
#     1. get_current_admin dependency runs — authenticates request and confirms ADMIN role (401/403 on failure)
#     2. Check for duplicate ISBN — ISBNs are globally unique book identifiers → 400 if already exists
#     3. Create Book ORM object — available_copies = total_copies (all available on creation, none borrowed yet)
#     4. Add to DB, commit, refresh to get DB-generated fields (id, created_at, etc.)
#     5. Clear the entire cache — ensures /books list and any cached book details are invalidated immediately
#     6. Return the newly created book — serialized via BookResponse schema
#     """
#     if db.query(Book).filter(Book.isbn == book.isbn).first():  # step 2: ISBN must be unique across all books
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Book with this ISBN already exists")

#     db_book = Book(                             # step 3: build Book ORM object
#         title=book.title,
#         author=book.author,
#         isbn=book.isbn,
#         total_copies=book.total_copies,
#         available_copies=book.total_copies,     # all copies available at creation — none borrowed yet
#         description=book.description
#     )

#     db.add(db_book)       # step 4: stage insert
#     db.commit()           # write to DB
#     db.refresh(db_book)   # reload to get DB-generated fields like id

#     await FastAPICache.clear()  # step 5: bust cache — new book must appear in /books immediately
#     return db_book              # step 6: return created book


# @router.put("/books/{book_id}", response_model=BookResponse)
# # @limiter.limit("100/hour")
# async def update_book(
#     request: Request,
#     book_id: int,
#     book: BookUpdate,       # partial update — all fields are Optional, only provided fields are updated
#     db: Session = Depends(get_db),
#     admin: User = Depends(get_current_admin)  # authentication + admin role check — 401/403 on failure
# ):
#     """
#     Workflow:
#     1. get_current_admin dependency runs — confirms ADMIN role (401/403 on failure)
#     2. Look up book by ID — 404 if not found
#     3. Apply only the fields that were explicitly provided (None = not sent = skip)
#     4. For total_copies changes: calculate the diff and guard against going negative on available_copies
#        (negative would mean borrowers hold more copies than the book has — data integrity violation)
#     5. Commit updates and refresh from DB
#     6. Clear cache — stale book data must not be served after an update
#     7. Return updated book — serialized via BookResponse schema
#     """
#     db_book = db.query(Book).filter(Book.id == book_id).first()  # step 2: fetch book by primary key
#     if not db_book:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

#     if book.title is not None:          # step 3: only update fields the client explicitly sent
#         db_book.title = book.title
#     if book.author is not None:
#         db_book.author = book.author
#     if book.total_copies is not None:
#         diff = book.total_copies - db_book.total_copies  # step 4: positive = adding copies, negative = removing
#         if db_book.available_copies + diff < 0:          # guard: can't remove more copies than are available
#             raise HTTPException(
#                 status.HTTP_400_BAD_REQUEST,
#                 f"Cannot reduce total_copies: {-diff} copies are currently borrowed"
#             )
#         db_book.total_copies     = book.total_copies
#         db_book.available_copies += diff    # adjust available proportionally — maintains the borrow count
#     if book.description is not None:
#         db_book.description = book.description

#     db.commit()           # step 5: persist all changes atomically
#     db.refresh(db_book)   # reload to reflect DB state in the returned object

#     await FastAPICache.clear()  # step 6: invalidate cache — clients must see updated data immediately
#     return db_book              # step 7: return updated book


# @router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
# # @limiter.limit("50/hour")
# async def delete_book(
#     request: Request,
#     book_id: int,
#     db: Session = Depends(get_db),
#     admin: User = Depends(get_current_admin)  # authentication + admin role check — 401/403 on failure
# ):
#     """
#     Workflow:
#     1. get_current_admin dependency runs — confirms ADMIN role (401/403 on failure)
#     2. Look up book by ID — 404 if not found
#     3. Guard: reject deletion if any copies are currently borrowed
#        (available < total means some copies are out — deleting would orphan those transactions)
#     4. Delete the book row from DB and commit
#     5. Clear cache — deleted book must not appear in /books or /books/{id} responses
#     6. Return success message
#     """
#     book = db.query(Book).filter(Book.id == book_id).first()  # step 2: fetch book by primary key
#     if not book:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

#     if book.available_copies < book.total_copies:  # step 3: some copies are borrowed — block deletion
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST,
#             "Cannot delete book: some copies are currently borrowed"
#         )

#     db.delete(book)   # step 4: mark for deletion
#     db.commit()       # write deletion to DB

#     await FastAPICache.clear()                        # step 5: bust cache
#     return {"message": "Book deleted successfully"}   # step 6: co
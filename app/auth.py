from passlib.context import CryptContext          # Provides password hashing utilities (bcrypt, argon2, etc.)
from jose import jwt, JWTError                    # JWT encoding/decoding and error handling
from datetime import datetime, timedelta          # Used to calculate token expiration timestamps
from fastapi import Depends, HTTPException, status # FastAPI dependency injection, HTTP errors, and status codes
from fastapi.security import OAuth2PasswordBearer # Extracts Bearer token from Authorization header automatically
from sqlalchemy.orm import Session                # SQLAlchemy session type for DB queries
from app.database import get_db                   # Dependency that yields a DB session per request
from app.models import User, UserRole             # ORM models: User table + UserRole enum (e.g. ADMIN, USER)
import os                                         # Used to read environment variables (SECRET_KEY)

# ===================== PASSWORD CONFIG =====================

pwd_context = CryptContext(
    schemes=["bcrypt"],     # Use bcrypt as the hashing algorithm (industry standard for passwords)
    deprecated="auto",      # Automatically mark older/weaker hashes as deprecated for rehashing
    bcrypt__rounds=12       # Work factor: 2^12 = 4096 iterations — balances security and performance
)

# ===================== JWT CONFIG =====================

SECRET_KEY = os.getenv(
    "SECRET_KEY",                                               # Read from environment variable for production safety
    "711fc4b2bf772f150f21291800653292612456e2af773dff1de7fb56d00b89cc"  # Fallback default (dev only — never use in prod)
)

ALGORITHM = "HS256"                    # HMAC-SHA256 — symmetric signing algorithm for JWTs
ACCESS_TOKEN_EXPIRE_MINUTES = 30       # Access tokens expire after 30 minutes (short-lived for security)
REFRESH_TOKEN_EXPIRE_DAYS = 7          # Refresh tokens expire after 7 days (longer-lived for UX convenience)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")  # Tells FastAPI where clients obtain tokens (used in Swagger UI too)

# ===================== PASSWORD HELPERS =====================

def get_password_hash(password: str) -> str:
    if len(password.encode("utf-8")) > 72:  # bcrypt silently truncates passwords beyond 72 bytes — handle it explicitly
        password = password[:72]            # Slice to 72 chars to ensure consistent hashing behavior
    return pwd_context.hash(password)       # Hash the password using bcrypt with the configured rounds

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode("utf-8")) > 72:  # Apply the same 72-byte truncation as during hashing
        plain_password = plain_password[:72]       # Ensures comparison is against the same truncated value
    return pwd_context.verify(plain_password, hashed_password)  # Securely compares plain vs hashed (timing-safe)

# ===================== TOKEN CREATION =====================

def create_access_token(
    data: dict,                        # Payload to encode (typically {"sub": user_id})
    # expires_delta: timedelta | None = None  # Optional custom expiry; falls back to default if not provided
) -> str:
    to_encode = data.copy()            # Copy to avoid mutating the original dict passed by the caller
    expire = datetime.utcnow() + (
         timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Use custom delta or default 30 min
    )
    to_encode.update({"exp": expire, "type": "access"})  # Add expiry + token type tag to prevent token misuse
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)        # Sign and encode the JWT string

def create_refresh_token(
    data: dict,                        # Payload to encode (typically {"sub": user_id})
    # expires_delta: timedelta | None = None  # Optional custom expiry; falls back to default if not provided
) -> str:
    to_encode = data.copy()            # Copy to avoid mutating the caller's dict
    expire = datetime.utcnow() + (
         timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)  # Use custom delta or default 7 days
    )
    to_encode.update({"exp": expire, "type": "refresh"})  # Tag as "refresh" so it can't be used as an access token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   # Sign and encode the refresh JWT string

# ===================== CURRENT USER =====================

def get_current_user(
    token: str = Depends(oauth2_scheme),  # Automatically extracts Bearer token from the Authorization header
    db: Session = Depends(get_db)         # Injects a DB session scoped to this request
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,         # 401 = unauthenticated (not to be confused with 403)
        detail="Could not validate credentials",          # Generic message avoids leaking internal details
        headers={"WWW-Authenticate": "Bearer"},           # Required by OAuth2 spec to signal Bearer auth scheme
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode and verify JWT signature + expiry
        if payload.get("type") != "access":   # Reject refresh tokens being used where access tokens are expected
            raise credentials_exception
        user_id = payload.get("sub")          # "sub" (subject) claim holds the user's ID as a string
        if user_id is None:                   # Malformed token — missing subject claim
            raise credentials_exception
    except JWTError:                          # Catches expired, tampered, or malformed tokens
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()  # Look up user in DB by ID from token
    if not user:                              # User was deleted after token was issued
        raise credentials_exception

    # if not user.is_active:                   # Soft-disabled accounts are forbidden even with valid tokens
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,  # 403 = authenticated but not authorized
    #         detail="Inactive user"
    #     )

    return user  # Return the authenticated User ORM object to be used by route handlers

def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Attempt to decode and validate JWT
        return payload   # Return decoded claims dict if valid
    except JWTError:
        return None      # Return None silently for invalid/expired tokens (caller decides what to do)

# ===================== ADMIN CHECK =====================

def get_current_admin(
    current_user: User = Depends(get_current_user)  # First authenticates user via get_current_user dependency
) -> User:
    if current_user.role != UserRole.ADMIN:  # Check role — only ADMIN enum value passes
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 403 = authenticated but lacks required permissions
            detail="Admin access required"
        )
    return current_user  # Return the admin User object to the route handler
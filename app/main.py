from fastapi import FastAPI
from app.database import engine, Base
from app.routes_no_auth import router
from app.cache import init_cache

# Rate limiter imports
from app.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
)

# Initialize cache on startup
@app.on_event("startup")
async def startup():
    await init_cache()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 CRITICAL: Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Library Management System, open in Swagger"}

@app.get("/health")
def health():
    return {"status": "ok"}
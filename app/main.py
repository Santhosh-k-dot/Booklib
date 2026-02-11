from fastapi import FastAPI
from app.database import engine, Base
from app.routes_no_auth import router
from app.cache import init_cache

# 🔽 ADD THESE IMPORTS
from app.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Create database tables
Base.metadata.create_all(bind=engine)

#add_middleware

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Library Management System",
)

# 🔹 INIT REDIS CACHE
@app.on_event("startup")
def startup():
    init_cache()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 REGISTER RATE LIMITER (CRITICAL)
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

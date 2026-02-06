from fastapi import FastAPI
from app.database import engine, Base
# from app.routes import router  # Comment out the old one
from app.routes_no_auth import router  # Use the no-auth version

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Library Management System",
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Library Management System, open in Swagger"
    }
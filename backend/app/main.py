from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import user, book, issue, category
from app.routes import auth_routes, book_routes, issue_routes
from app.routes import admin_routes, category_routes
from app.routes import user_routes

app = FastAPI(title="Library Management System")

# =======================
# CORS CONFIGURATION
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# CREATE DATABASE TABLES
# =======================
Base.metadata.create_all(bind=engine)

# =======================
# ROOT ENDPOINT
# =======================
@app.get("/")
def root():
    return {"status": "Backend is running"}

# =======================
# ROUTES
# =======================
app.include_router(auth_routes.router)
app.include_router(book_routes.router)
app.include_router(issue_routes.router)
app.include_router(admin_routes.router)
app.include_router(category_routes.router,prefix="/categories")
app.include_router(user_routes.router)
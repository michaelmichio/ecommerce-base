import os
import logging
import traceback

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import Base, engine, SessionLocal
from app.core.config import get_settings
from app.schemas.response import ErrorResponse, SuccessResponse
from app.api.routes import auth, users, admin, products, upload
from app.core.seed import seed_roles_and_users


# ==============================================================================
# 🔧 Initialization
# ==============================================================================

settings = get_settings()

# Seed initial roles and users (only runs if missing)
seed_roles_and_users()

# Create tables (temporary until Alembic migration enabled)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


# ==============================================================================
# 🌐 CORS — Best Practice, Single Middleware Only
# ==============================================================================

# Always include localhost for Next.js dev
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Merge .env origins (optional)
if settings.BACKEND_CORS_ORIGINS:
    env_origins = [
        o.strip()
        for o in settings.BACKEND_CORS_ORIGINS.split(",")
        if o.strip()
    ]
    origins = list(set(default_origins + env_origins))
else:
    origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # required for HttpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# 🧾 Global Error Formatting
# ==============================================================================

def format_error(code: int, type_: str, message: str) -> JSONResponse:
    """Standardized error formatter."""
    return JSONResponse(
        status_code=code,
        content=ErrorResponse(
            error={
                "code": code,
                "type": type_,
                "message": message,
            }
        ).dict()
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return format_error(
        400,
        "IntegrityError",
        "Database constraint violated (duplicate or invalid reference)."
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_error(exc.status_code, "HTTPException", exc.detail)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return format_error(
        500,
        "InternalServerError",
        str(exc) or "An unexpected error occurred."
    )


# ==============================================================================
# 🧭 Logging — Rotating, Clean, Not Overly Verbose
# ==============================================================================

ENV = os.getenv("APP_ENV", "development")

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "app.log")

file_handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO if ENV == "development" else logging.WARNING,
    handlers=[file_handler, logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# ==============================================================================
# 📦 Request Logging Middleware (clean output)
# ==============================================================================

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"➡️  {request.method} {request.url.path}")

        # Log body for modifying requests (limit 300 chars)
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.body()
                if body:
                    snippet = (
                        body.decode("utf-8")[:300]
                        .replace("\n", "")
                        .replace("\r", "")
                    )
                    logging.info(f"📦 Body: {snippet}")
            except Exception:
                logging.info("📦 Body: <unreadable>")

        try:
            response = await call_next(request)
            logging.info(f"⬅️  {response.status_code} {request.method} {request.url.path}")
            return response
        except Exception as e:
            logging.exception(f"💥 Exception on {request.method} {request.url.path}: {e}")
            raise

app.add_middleware(LoggingMiddleware)


# ==============================================================================
# 🚀 Router Registration (clean grouping)
# ==============================================================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(upload.router)


# ==============================================================================
# 🗃 Database Dependency (Best Practice)
# ==============================================================================

def get_db():
    """DB session dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# 🩺 Health Check
# ==============================================================================

@app.get("/health", response_model=SuccessResponse)
def health(db: Session = Depends(get_db)):
    return SuccessResponse(data={"status": "ok"})

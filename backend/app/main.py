import os
import logging
import traceback
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import TimedRotatingFileHandler
from fastapi.exceptions import HTTPException

from app.core.database import SessionLocal, Base, engine
from app.core.config import get_settings
from app.api.routes import auth, users, admin, products, upload
from app.core.seed import seed_roles
from app.schemas.response import ErrorResponse, SuccessResponse

# ==========================================
# 🧩 Inisialisasi & Setup Awal
# ==========================================
seed_roles()
settings = get_settings()
Base.metadata.create_all(bind=engine)  # sementara, nanti diganti Alembic

app = FastAPI(title=settings.PROJECT_NAME)

# ==========================================
# 🧱 Global Error Handlers (SuccessResponse & ErrorResponse)
# ==========================================

def format_error(code: int, type_: str, message: str) -> JSONResponse:
    """Helper untuk membuat response error standar"""
    return JSONResponse(
        status_code=code,
        content=ErrorResponse(
            error={"code": code, "type": type_, "message": message}
        ).dict()
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return format_error(400, "IntegrityError", "Database constraint violated (duplicate or invalid reference).")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_error(exc.status_code, "HTTPException", exc.detail)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return format_error(500, "InternalServerError", str(exc) or "An unexpected error occurred.")

# ==========================================
# 🌐 CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.BACKEND_CORS_ORIGINS:
    origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ==========================================
# 🧾 Logging setup (rotation)
# ==========================================
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
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, logging.StreamHandler()],
)

# ==========================================
# 🧭 Logging Middleware
# ==========================================
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"➡️  {request.method} {request.url.path}")
        try:
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

            response = await call_next(request)
            logging.info(f"⬅️  {response.status_code} {request.method} {request.url.path}")
            return response
        except Exception as e:
            logging.exception(f"💥 Exception on {request.method} {request.url.path}: {e}")
            raise

app.add_middleware(LoggingMiddleware)

# ==========================================
# 🧩 Routers
# ==========================================
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(upload.router)

# ==========================================
# 🗃️ Database Dependency
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 🩺 Health check
# ==========================================
@app.get("/health", response_model=SuccessResponse)
def health(db: Session = Depends(get_db)):
    return SuccessResponse(data={"status": "ok"})

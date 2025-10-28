import traceback
import logging
import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import TimedRotatingFileHandler

from app.core.database import SessionLocal, Base, engine
from app.core.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, admin, products, upload
from app.core.seed import seed_roles
from app.schemas.response import ErrorResponse

seed_roles()

settings = get_settings()
Base.metadata.create_all(bind=engine)  # sementara, nanti diganti Alembic

app = FastAPI(title=settings.PROJECT_NAME)

def error_json(code: int, type_: str, message: str) -> JSONResponse:
    """helper untuk membuat response error standard"""
    return JSONResponse(
        status_code=code,
        content=ErrorResponse(
            error={
                "code": code,
                "type": type_,
                "message": message
            }
        ).dict()
    )

# 🔹 Database constraint error (duplicate, FK, dsb.)
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    print("❗ IntegrityError:", exc)
    return error_json(400, "IntegrityError", "Database constraint violated (duplicate or invalid reference).")

# 🔹 HTTP Exception (misalnya raise HTTPException)
from fastapi.exceptions import HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_json(exc.status_code, "HTTPException", exc.detail)

# 🔹 Generic Python exception (fallback)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("⚠️ Unhandled Exception:", exc)
    traceback.print_exc()
    return error_json(500, "InternalServerError", "An unexpected error occurred. Please contact administrator.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Environment & directories
ENV = os.getenv("APP_ENV", "development")
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Setup log rotation
log_file = os.path.join(LOG_DIR, "app.log")

# Membuat handler yang rotate setiap hari, simpan 7 file log terakhir
file_handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",   # rotate setiap tengah malam
    interval=1,
    backupCount=7,     # keep 7 hari terakhir
    encoding="utf-8"
)

# file_handler = RotatingFileHandler(
#     log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
# )

# Format log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Tambahkan handler ke root logger
logging.basicConfig(
    level=logging.INFO if ENV == "development" else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, logging.StreamHandler()],
)

# ✅ Middleware logging
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

# ✅ Tambahkan middleware setelah CORS
app.add_middleware(LoggingMiddleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(upload.router)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Dependency untuk session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}

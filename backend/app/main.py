from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import traceback
from sqlalchemy.orm import Session

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

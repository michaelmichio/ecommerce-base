from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, admin, products, upload
from app.core.seed import seed_roles

seed_roles()

settings = get_settings()
Base.metadata.create_all(bind=engine)  # sementara, nanti diganti Alembic

app = FastAPI(title=settings.PROJECT_NAME)

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

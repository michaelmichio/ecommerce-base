from app.models.role import Role
from app.core.database import SessionLocal

def seed_roles():
    db = SessionLocal()
    if not db.query(Role).filter(Role.name == "admin").first():
        db.add(Role(name="admin", description="Administrator"))
    if not db.query(Role).filter(Role.name == "user").first():
        db.add(Role(name="user", description="Regular user"))
    db.commit()
    db.close()

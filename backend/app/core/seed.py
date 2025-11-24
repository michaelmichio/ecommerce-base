from sqlalchemy.exc import SQLAlchemyError
from app.core.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash


def seed_roles_and_users():
    """
    Seeds essential roles and initial admin/user accounts.
    Safe, idempotent, and can be run multiple times.
    """
    db = SessionLocal()

    try:
        created_roles = []
        created_users = []

        # =====================================================================
        # Seed Roles
        # =====================================================================
        required_roles = [
            {"name": "admin", "description": "Administrator"},
            {"name": "user", "description": "Regular user"},
        ]

        for role_data in required_roles:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                new_role = Role(**role_data)
                db.add(new_role)
                created_roles.append(role_data["name"])

        db.commit()  # commit roles before assigning users

        # Fetch roles for user assignment
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        user_role = db.query(Role).filter(Role.name == "user").first()

        # =====================================================================
        # Seed Users
        # =====================================================================

        users_to_seed = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "role": admin_role,
            },
            {
                "email": "user@example.com",
                "password": "user123",
                "role": user_role,
            },
        ]

        for u in users_to_seed:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if not existing_user:
                new_user = User(
                    email=u["email"],
                    hashed_password=get_password_hash(u["password"]),
                    role_id=u["role"].id,
                )
                db.add(new_user)
                created_users.append(u["email"])

        db.commit()

        # Logging
        if created_roles:
            print(f"[seed] Created roles: {', '.join(created_roles)}")
        if created_users:
            print(f"[seed] Created users: {', '.join(created_users)}")

        if not created_roles and not created_users:
            print("[seed] Nothing to seed. Everything already exists.")

    except SQLAlchemyError as e:
        db.rollback()
        print("[seed] Error during seeding:", str(e))
        raise

    finally:
        db.close()

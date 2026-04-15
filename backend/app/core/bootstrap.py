from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Base, User


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_admin = db.scalar(
            select(User).where(User.email == settings.default_admin_email)
        )
        if existing_admin:
            return

        db.add(
            User(
                name="Admin",
                email=settings.default_admin_email,
                password_hash=hash_password(settings.default_admin_password),
                role="admin",
            )
        )
        db.commit()

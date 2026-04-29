from datetime import datetime
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from domain.entities import UserRole
from infrastructure.models import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USERS = [
    {
        "email": "courier@foodrush.kz",
        "password": "Courier123!",
        "full_name": "Dana Delivery",
        "role": UserRole.courier,
    },
    {
        "email": "admin@foodrush.kz",
        "password": "Admin123!",
        "full_name": "Aruzhan Operations",
        "role": UserRole.admin,
    },
]


def seed_demo_users(session: Session) -> None:
    for user_data in DEMO_USERS:
        existing_user = session.query(UserModel).filter(UserModel.email == user_data["email"]).first()
        if existing_user is not None:
            continue

        session.add(
            UserModel(
                id=uuid4(),
                email=user_data["email"],
                hashed_password=pwd_context.hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
        )

    session.commit()

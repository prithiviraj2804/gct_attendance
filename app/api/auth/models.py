import uuid

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.utils.password_utils import get_password_hash
from sqlalchemy.orm import validates


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users", lazy='joined')

    @validates('password')
    def validate_password(self, key, password):
        return get_password_hash(password)



@event.listens_for(User.__table__, 'after_create')
def insert_default_admin_user(target, connection, **kw):
    session = Session(bind=connection)
    admin_role = session.query(Role).filter_by(name='admin').first()
    hashed_password = get_password_hash("admin@123")
    if admin_role:
        session.add(User(
            username='admin',
            name='Administrator',
            password=hashed_password,  # You should hash the password in a real scenario
            role_id=admin_role.id
        ))
        session.commit()


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    users = relationship("User", back_populates="role", lazy='raise')


@event.listens_for(Role.__table__, 'after_create')
def insert_initial_roles(target, connection, **kw):
    session = Session(bind=connection)
    session.add_all([
        Role(name='admin'),
        Role(name='faculty')
    ])
    session.commit()

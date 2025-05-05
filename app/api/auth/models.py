import uuid

from sqlalchemy import UUID, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.utils.password_utils import get_password_hash
from sqlalchemy.orm import validates

'''
============================================
Role Models
===========================================
'''

class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    users = relationship("User", back_populates="role", lazy='raise')


@event.listens_for(Role.__table__, 'after_create')
def insert_initial_roles(target, connection, **kw):
    session = Session(bind=connection)
    session.add_all([
        Role(name='admin'),
        Role(name='hod'),
        Role(name='faculty'),
        Role(name='advisor')  # Added advisor role
    ])
    session.commit()

    
'''
============================================
User Models
===========================================
'''

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    role: Mapped[Role] = relationship(
        "Role", back_populates="users", lazy="joined"
    )

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    department: Mapped[dict] = relationship(
        "Department",
        back_populates="users",
        foreign_keys=[department_id],
        lazy="selectin",
    )

    section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), nullable=True
    )
    section: Mapped[dict] = relationship(
        "Section", back_populates="users", lazy="selectin"
    )

    # New field to mark a user as an advisor for a section
    is_section_advisor: Mapped[bool] = mapped_column(Boolean, default=False)

    teaching_assignments: Mapped[list[dict]] = relationship(
        "StaffSubjectSection",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # New relationship for sections where user is advisor
    advised_sections = relationship(
        "Section", 
        back_populates="advisor", 
        foreign_keys="Section.advisor_id",
        lazy="selectin"
    )

@event.listens_for(User.__table__, 'after_create')
def insert_default_admin_user(target, connection, **kw):
    session = Session(bind=connection)
    admin_role = session.query(Role).filter_by(name='admin').first()
    if admin_role:
        hashed = get_password_hash("admin@123")
        session.add(
            User(
                username='admin',
                name='Administrator',
                password=hashed,
                role_id=admin_role.id
            )
        )
        session.commit()

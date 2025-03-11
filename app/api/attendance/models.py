from datetime import datetime
import uuid
from requests import Session
from sqlalchemy import Column, DateTime, Integer, String,ForeignKey,UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.password_utils import get_password_hash
from sqlalchemy.orm import validates
from sqlalchemy import event


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


# Model for Batch
class Batch(Base):
    __tablename__ = 'batches'
    
    name = Column(String, unique=True, index=True)  # e.g., "2022-2026"
    
    years = relationship("Year", back_populates="batch")


# Model for Year (Each batch has multiple years)
class Year(Base):
    __tablename__ = 'years'
    
    name = Column(String)  # e.g., "Year 1", "Year 2"
    batch_id = Column(UUID, ForeignKey('batches.id'))  # Link to the batch this year belongs to
    
    batch = relationship("Batch", back_populates="years")
    sections = relationship("Section", back_populates="year")


# Model for Section (A section for each year)
class Section(Base):
    __tablename__ = 'sections'
    
    name = Column(String)  # Section name (e.g., "A", "B")
    year_id = Column(UUID, ForeignKey('years.id'))  # Link to the year this section belongs to
    
    year = relationship("Year", back_populates="sections")
    students = relationship("Student", back_populates="section")


# Model for Student
class Student(Base):
    __tablename__ = 'students'
    
    name = Column(String, index=True)
    section_id = Column(UUID, ForeignKey('sections.id'))  # Link to section
    section = relationship("Section", back_populates="students")
    
    attendances = relationship("Attendance", back_populates="student")


# Model for Attendance
class Attendance(Base):
    __tablename__ = 'attendance'
    
    student_id = Column(UUID, ForeignKey('students.id'))
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Absent")  # "Present" or "Absent"
    
    student = relationship("Student", back_populates="attendances")
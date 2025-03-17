from datetime import datetime
import uuid
from sqlalchemy import Column, Date, DateTime, String, ForeignKey, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

# Department Model
class Department(Base):
    __tablename__ = 'departments'

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    batches = relationship("Batch", back_populates="department")


# Batch Model
class Batch(Base):
    __tablename__ = 'batches'
    
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)

    department = relationship("Department", back_populates="batches")
    years = relationship("Year", back_populates="batch")


# Year Model
class Year(Base):
    __tablename__ = 'years'
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('batches.id'), nullable=False)

    batch = relationship("Batch", back_populates="years")
    sections = relationship("Section", back_populates="year")


# Section Model
class Section(Base):
    __tablename__ = 'sections'
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    year_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('years.id'), nullable=False)

    users = relationship("User", back_populates="section")
    year = relationship("Year", back_populates="sections")
    students = relationship("Student", back_populates="section")


# Student Model
class Student(Base):
    __tablename__ = 'students'
    
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")


# Attendance Model
class Attendance(Base):
    __tablename__ = 'attendance'
    
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    date: Mapped[Date] = mapped_column(Date, default=datetime.utcnow().date, index=True)
    status: Mapped[str] = mapped_column(String, default="Absent")  # "Present" or "Absent"

    student = relationship("Student", back_populates="attendances")

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (UUID, Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, String, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.auth.models import User
from app.core.database import Base


# Department Model
class Department(Base):
    __tablename__ = 'departments'

    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)

    hod_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    hod = relationship("User", foreign_keys=[hod_id])  # Specify foreign_keys explicitly
    
    users = relationship("User", back_populates="department", foreign_keys=[User.department_id])

    batches = relationship("Batch", back_populates="department")

    __table_args__ = (
        UniqueConstraint('hod_id', name='unique_hod_per_user'),
    )

# Batch Model
class Batch(Base):
    __tablename__ = 'batches'

    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)

    department = relationship("Department", back_populates="batches")
    years = relationship("Year", back_populates="batch")


# Year Model
class Year(Base):
    __tablename__ = 'years'

    name: Mapped[str] = mapped_column(String, nullable=False)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('batches.id'), nullable=False)

    batch = relationship("Batch", back_populates="years")
    sections = relationship("Section", back_populates="year")


# Section Model
class Section(Base):
    __tablename__ = 'sections'

    name: Mapped[str] = mapped_column(String, nullable=False)
    year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('years.id'), nullable=False)

    users = relationship("User", back_populates="section")
    year = relationship("Year", back_populates="sections")
    students = relationship("Student", back_populates="section")

    timetable = relationship("Timetable", back_populates="section")
    attendances = relationship("Attendance", back_populates="section")


# Student Model
class Student(Base):
    __tablename__ = 'students'

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    register_number: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)
    roll_number: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="students")


# Subject Model
class Timetable(Base):
    __tablename__ = 'timetables'

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False, unique=True)

    section = relationship("Section", back_populates="timetable")
    timetable_slots = relationship("TimetableSlot", back_populates="timetable")


class TimetableSlot(Base):
    __tablename__ = 'timetable_slots'

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('timetables.id'), nullable=False)
    # 1 = Monday, 2 = Tuesday, etc.
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    # Store the day's schedule as a JSONB object
    schedule: Mapped[dict] = mapped_column(JSONB, nullable=False)

    timetable = relationship("Timetable", back_populates="timetable_slots")


class Attendance(Base):
    __tablename__ = 'attendances'

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)
    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, index=True)
    # 1 = Monday, 2 = Tuesday, etc.
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    hour: Mapped[int] = mapped_column(
        Integer, nullable=False)  # 1 to 7 (or more if needed)
    # {"student_id_1": true, "student_id_2": false}
    attendance_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    section = relationship("Section", back_populates="attendances")
    __table_args__ = (
        UniqueConstraint('section_id', 'date', 'day_of_week',
                         'hour', name='_unique_attendance'),
    )

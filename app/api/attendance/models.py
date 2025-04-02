from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, ForeignKey, UUID, UniqueConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

# Department Model
class Department(Base):
    __tablename__ = 'departments'

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    code = Column(String, unique=True, nullable=False)

    batches = relationship("Batch", back_populates="department")
    faculty_members = relationship("Faculty", back_populates="department")
    subjects = relationship("Subject", back_populates="department")


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
    class_advisor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("faculty.user_id"), nullable=True)

    # Relationships
    year = relationship("Year", back_populates="sections")
    class_advisor = relationship("Faculty", back_populates="advised_sections")
    students = relationship("Student", back_populates="section")
    timetables = relationship("Timetable", back_populates="section")
    users = relationship("User", back_populates="section")


# Student Model
class Student(Base):
    __tablename__ = 'students'
    
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="students")
    attendance_records = relationship("AttendanceRecord", back_populates="student")


# Subject Model
class Subject(Base):
    __tablename__ = "subjects"

    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)

    # Relationships
    department = relationship("Department", back_populates="subjects")
    timetable_entries = relationship("TimetableEntry", back_populates="subject")


class Timetable(Base):
    __tablename__ = "timetables"

    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)

    # Relationships
    section = relationship("Section", back_populates="timetables")
    entries = relationship("TimetableEntry", back_populates="timetable")
    timetable_slots = relationship("TimetableSlot", back_populates="timetable")


class DayOrder(Base):
    __tablename__ = "day_orders"

    name = Column(String, nullable=False)
    order_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint for order number
    __table_args__ = (
        UniqueConstraint('order_number', name='uq_day_order_number'),
    )

    # Relationships
    timetable_entries = relationship("TimetableEntry", back_populates="day_order")
    current_day_orders = relationship("CurrentDayOrder", back_populates="day_order")


class CurrentDayOrder(Base):
    __tablename__ = "current_day_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False, unique=True)
    day_order_id = Column(UUID(as_uuid=True), ForeignKey("day_orders.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    day_order = relationship("DayOrder", back_populates="current_day_orders")


class TimetableSlot(Base):
    __tablename__ = 'timetable_slots'

    timetable_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('timetables.id'), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    subject_code: Mapped[str] = mapped_column(String, nullable=False)

    timetable = relationship("Timetable", back_populates="timetable_slots")


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    timetable_id = Column(UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False)
    day_order_id = Column(UUID(as_uuid=True), ForeignKey("day_orders.id"), nullable=False)
    hour = Column(Integer, nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)

    # Unique constraint for timetable, day order, and hour
    __table_args__ = (
        UniqueConstraint('timetable_id', 'day_order_id', 'hour', name='uq_timetable_day_hour'),
    )

    # Relationships
    timetable = relationship("Timetable", back_populates="entries")
    day_order = relationship("DayOrder", back_populates="timetable_entries")
    subject = relationship("Subject", back_populates="timetable_entries")
    faculty = relationship("Faculty", backref="timetable_entries")
    attendance_sessions = relationship("AttendanceSession", back_populates="timetable_entry")


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    date = Column(DateTime, nullable=False)
    timetable_entry_id = Column(UUID(as_uuid=True), ForeignKey("timetable_entries.id"), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)

    # Unique constraint for date and timetable entry
    __table_args__ = (
        UniqueConstraint('date', 'timetable_entry_id', name='uq_attendance_date_entry'),
    )

    # Relationships
    timetable_entry = relationship("TimetableEntry", back_populates="attendance_sessions")
    faculty = relationship("Faculty", backref="attendance_sessions")
    records = relationship("AttendanceRecord", back_populates="session")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    session_id = Column(UUID(as_uuid=True), ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    is_present = Column(Boolean, default=False)

    # Unique constraint for session and student
    __table_args__ = (
        UniqueConstraint('session_id', 'student_id', name='uq_attendance_session_student'),
    )

    # Relationships
    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student", back_populates="attendance_records")

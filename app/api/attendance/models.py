from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, ForeignKey, UUID, UniqueConstraint
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

    timetable = relationship("Timetable", back_populates="section")


# Student Model
class Student(Base):
    __tablename__ = 'students'
    
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")


# Subject Model
class Timetable(Base):
    __tablename__ = 'timetables'

    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="timetable")
    timetable_slots = relationship("TimetableSlot", back_populates="timetable") 




class TimetableSlot(Base):
    __tablename__ = 'timetable_slots'

    timetable_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('timetables.id'), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = Monday, 2 = Tuesday, etc.
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 7, representing the 7 hours in a day
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    subject_code: Mapped[str] = mapped_column(String, nullable=False)

    timetable = relationship("Timetable", back_populates="timetable_slots")


class Attendance(Base):
    __tablename__ = 'attendances'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    timetable_slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('timetable_slots.id'), nullable=False)
    is_present: Mapped[bool] = mapped_column(Boolean, nullable=False)

    student = relationship("Student", back_populates="attendances")
    timetable_slot = relationship("TimetableSlot")  # Links to a specific subject period

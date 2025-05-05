import uuid
from datetime import date
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
        String, unique=True, nullable=False, index=True
    )

    hod_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    hod: Mapped["User"] = relationship("User", foreign_keys=[hod_id])

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="department",
        foreign_keys=[User.department_id],
        lazy="selectin",
    )
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="department", lazy="selectin"
    )
    batches: Mapped[list["Batch"]] = relationship(
        "Batch", back_populates="department"
    )

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
        UUID(as_uuid=True), ForeignKey('years.id'), nullable=False
    )
    
    # Add advisor relationship
    advisor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=True
    )
    
    year: Mapped[Year] = relationship(
        "Year", back_populates="sections"
    )

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="section", foreign_keys=[User.section_id]
    )
    
    # Add advisor relationship
    advisor: Mapped["User"] = relationship(
        "User", back_populates="advised_sections", foreign_keys=[advisor_id]
    )
    
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="section"
    )
    timetable: Mapped["Timetable"] = relationship(
        "Timetable", back_populates="section",
        uselist=False,
        cascade="all, delete-orphan"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="section"
    )
    teaching_assignments: Mapped[list["StaffSubjectSection"]] = relationship(
        "StaffSubjectSection",
        back_populates="section",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

class Subject(Base):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    department: Mapped[Department] = relationship(
        "Department", back_populates="subjects", lazy="selectin"
    )

    teaching_assignments: Mapped[list["StaffSubjectSection"]] = relationship(
        "StaffSubjectSection",
        back_populates="subject",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

class StaffSubjectSection(Base):
    __tablename__ = "staff_subject_sections"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), primary_key=True
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="teaching_assignments"
    )
    subject: Mapped[Subject] = relationship(
        "Subject", back_populates="teaching_assignments"
    )
    section: Mapped[Section] = relationship(
        "Section", back_populates="teaching_assignments"
    )


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
    
    # Add relationship to attendance records
    attendance_records: Mapped[list["StudentAttendance"]] = relationship(
        "StudentAttendance", back_populates="student", cascade="all, delete-orphan"
    )

class Timetable(Base):
    __tablename__ = 'timetables'

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False, unique=True
    )
    section: Mapped[Section] = relationship(
        "Section", back_populates="timetable"
    )
    timetable_slots: Mapped[list["TimetableSlot"]] = relationship(
        "TimetableSlot",
        back_populates="timetable",
        cascade="all, delete-orphan"
    )


class TimetableSlot(Base):
    __tablename__ = 'timetable_slots'

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('timetables.section_id'), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    schedule: Mapped[dict] = mapped_column(JSONB, nullable=False)

    timetable: Mapped[Timetable] = relationship(
        "Timetable", back_populates="timetable_slots"
    )

class Attendance(Base):
    __tablename__ = 'attendances'

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False
    )
    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Remove attendance_data field and use StudentAttendance records instead
    # attendance_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    section: Mapped[Section] = relationship(
        "Section", back_populates="attendances"
    )
    subject: Mapped[Subject] = relationship("Subject")
    faculty: Mapped[User] = relationship("User")
    
    # Add relationship to student attendance records
    student_records: Mapped[list["StudentAttendance"]] = relationship(
        "StudentAttendance", back_populates="attendance", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            'section_id', 'subject_id', 'attendance_date', 'day_of_week', 'hour', 
            name='_unique_attendance'
        ),
    )

# New model to track individual student attendance
class StudentAttendance(Base):
    __tablename__ = 'student_attendances'
    
    attendance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('attendances.id'), primary_key=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('students.id'), primary_key=True
    )
    is_present: Mapped[bool] = mapped_column(Boolean, default=False)
    
    attendance: Mapped[Attendance] = relationship(
        "Attendance", back_populates="student_records"
    )
    student: Mapped[Student] = relationship(
        "Student", back_populates="attendance_records"
    )

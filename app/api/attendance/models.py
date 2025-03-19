from datetime import datetime
import uuid
from sqlalchemy import Column, Date, DateTime, Integer, String, ForeignKey, UUID, UniqueConstraint
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
    year_subjects = relationship("YearSubject", back_populates="year")
    
    # For easy access, you can also define a method to get all subjects of this year
    @property
    def subjects(self):
        return [ys.subject for ys in self.year_subjects]


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
class Subject(Base):
    __tablename__ = 'subjects'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationship with Year to assign subjects to a specific year
    years = relationship("YearSubject", back_populates="subject")


# YearSubject Association Table
class YearSubject(Base):
    __tablename__ = 'year_subjects'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('years.id'), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)

    year = relationship("Year", back_populates="year_subjects")
    subject = relationship("Subject", back_populates="years")

# Timetable Model (for each day of the week)
class Timetable(Base):
    __tablename__ = 'timetables'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_of_week: Mapped[str] = mapped_column(String, nullable=False)  # 'Monday', 'Tuesday', etc.
    
    # For each hour, instead of a string, reference the Subject via ForeignKey
    hour_1_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_2_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_3_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_4_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_5_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_6_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_7_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=False)
    hour_8_subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subjects.id'), nullable=True)

    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)

    section = relationship("Section", back_populates="timetable")
    
    # Relationship with subjects for each hour
    hour_1_subject = relationship("Subject", foreign_keys=[hour_1_subject_id])
    hour_2_subject = relationship("Subject", foreign_keys=[hour_2_subject_id])
    hour_3_subject = relationship("Subject", foreign_keys=[hour_3_subject_id])
    hour_4_subject = relationship("Subject", foreign_keys=[hour_4_subject_id])
    hour_5_subject = relationship("Subject", foreign_keys=[hour_5_subject_id])
    hour_6_subject = relationship("Subject", foreign_keys=[hour_6_subject_id])
    hour_7_subject = relationship("Subject", foreign_keys=[hour_7_subject_id])
    hour_8_subject = relationship("Subject", foreign_keys=[hour_8_subject_id])
    
    attendances = relationship("Attendance", back_populates="timetable")

# Attendance Model (Unchanged)
class Attendance(Base):
    __tablename__ = 'attendance'
    
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    timetable_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('timetables.id'), nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, default="Absent")
    date: Mapped[str] = mapped_column(String, nullable=False)

    student = relationship("Student", back_populates="attendances")
    timetable = relationship("Timetable", back_populates="attendances")

    __table_args__ = (
        UniqueConstraint('student_id', 'date', 'hour', name='unique_student_hour'),
    )
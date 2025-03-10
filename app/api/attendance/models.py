from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String,ForeignKey,UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = 'students'
    
    name = Column(String, index=True)
    section = Column(String, index=True)
    
    attendances = relationship("Attendance", back_populates="student")

# Model for Attendance
class Attendance(Base):
    __tablename__ = 'attendance'
    
    student_id = Column(UUID, ForeignKey('students.id'))
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Absent")  # "Present" or "Absent"
    
    student = relationship("Student", back_populates="attendances")
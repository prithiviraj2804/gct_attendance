from datetime import date
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import File, UploadFile
from numpy import datetime64
from pydantic import BaseModel, Field


class UploadFileSchema(BaseModel):
    batch_name: str
    year_name: str
    section_name: str

    class Config:
        from_attributes = True


class DepartmentCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True


class BatchCreate(BaseModel):
    name: str
    department_id: UUID

    class Config:
        from_attributes = True


class YearCreate(BaseModel):
    name: str
    batch_id: UUID

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    name: str
    year_id: UUID

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: UUID
    name: str
    section_id: UUID


class StudentUUIDs(BaseModel):
    student_uuids: list[UUID]

    class Config:
        from_attributes = True

class TimetableSlotCreate(BaseModel):
    day_of_week: int  # 1 to 6 (Mon-Sat)
    schedule: Dict[str, Dict[str, str]]  # {"1": {"subject_name": "Math", "subject_code": "MAT101"}, ...}

    class Config:
        orm_mode = True


class TimetableCreate(BaseModel):
    section_id: UUID
    slots: List[TimetableSlotCreate] = Field(..., description="List of timetable slots for each day")

    class Config:
        orm_mode = True

class TimetableSlotResponse(BaseModel):
    id: UUID
    timetable_id: UUID
    day_of_week: int
    hour: int
    subject_name: str
    subject_code: str

    class Config:
        orm_mode = True


class TimetableResponse(BaseModel):
    id: UUID
    slots: List[TimetableSlotResponse]

    class Config:
        orm_mode = True


# Individual student attendance within a batch
class StudentAttendance(BaseModel):
    student_id: UUID
    is_present: bool

# Attendance record for a specific day and hour
class AttendanceRecord(BaseModel):
    day_of_week: int  # 1 = Monday, 2 = Tuesday, etc.
    hour: int  # 1 to 7 (or more if needed)
    students: Dict[str, bool]  # {"student_id_1": true, "student_id_2": false}

# Batch attendance input
class AttendanceBatchCreate(BaseModel):
    date: date
    section_id: UUID
    records: List[AttendanceRecord]
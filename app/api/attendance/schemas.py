from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import File, UploadFile
from numpy import datetime64
from pydantic import BaseModel


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

class TimetableCreate(BaseModel):
    section_id: UUID
    day_of_week: str  # e.g., "Monday", "Tuesday", etc.
    hour_1_subject: str
    hour_2_subject: str
    hour_3_subject: str
    hour_4_subject: str
    hour_5_subject: str
    hour_6_subject: str
    hour_7_subject: str
    hour_8_subject: Optional[str] = None

    class Config:
        from_attributes = True

class TimetableResponse(BaseModel):
    id: UUID
    section_id: UUID
    day_of_week: str
    hour_1_subject: str
    hour_2_subject: str
    hour_3_subject: str
    hour_4_subject: str
    hour_5_subject: str
    hour_6_subject: str
    hour_7_subject: str
    hour_8_subject: Optional[str] = None

class AttendanceCreate(BaseModel):
    day_of_week: str
    date: datetime
    hour : str
    attendance_data: List[UUID] 

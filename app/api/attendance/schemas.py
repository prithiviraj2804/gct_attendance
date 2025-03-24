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

class TimetableSlotCreate(BaseModel):
    day_of_week: int  # 1 to 6 (Mon-Sat)
    hour: int  # 1 to 7
    subject_name: str
    subject_code: str

    class Config:
        orm_mode = True


class TimetableCreate(BaseModel):
    slots: List[TimetableSlotCreate]

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
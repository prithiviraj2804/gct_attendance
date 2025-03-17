from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import File, UploadFile
from pydantic import BaseModel


class UploadFileSchema(BaseModel):
    batch_name: str
    year_name: str
    section_name: str

    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    student_id: UUID
    date: Optional[datetime] = None  # Defaults to today if not provided
    status: str = "Absent"  # "Present" or "Absent"

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
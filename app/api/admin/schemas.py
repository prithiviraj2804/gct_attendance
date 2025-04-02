from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Department schemas
class DepartmentBase(BaseModel):
    name: str
    code: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Batch schemas
class BatchBase(BaseModel):
    name: str
    start_year: int
    end_year: int
    department_id: int

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    name: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    department_id: Optional[int] = None

class BatchResponse(BatchBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Year schemas
class YearBase(BaseModel):
    name: str
    year_number: int
    batch_id: int

class YearCreate(YearBase):
    pass

class YearUpdate(BaseModel):
    name: Optional[str] = None
    year_number: Optional[int] = None
    batch_id: Optional[int] = None

class YearResponse(YearBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Section schemas
class SectionBase(BaseModel):
    name: str
    year_id: int
    class_advisor_id: Optional[int] = None

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    name: Optional[str] = None
    year_id: Optional[int] = None
    class_advisor_id: Optional[int] = None

class SectionResponse(SectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Student schemas
class StudentBase(BaseModel):
    roll_number: str
    name: str
    email: EmailStr
    section_id: int

class StudentCreate(StudentBase):
    pass

class StudentBulkCreate(BaseModel):
    students: List[StudentCreate]

class StudentUpdate(BaseModel):
    roll_number: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    section_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Subject schemas
class SubjectBase(BaseModel):
    code: str
    name: str
    department_id: int

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    department_id: Optional[int] = None

class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# DayOrder schemas
class DayOrderBase(BaseModel):
    name: str
    order_number: int

class DayOrderCreate(DayOrderBase):
    pass

class DayOrderUpdate(BaseModel):
    name: Optional[str] = None
    order_number: Optional[int] = None

class DayOrderResponse(DayOrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# CurrentDayOrder schemas
class CurrentDayOrderBase(BaseModel):
    date: datetime
    day_order_id: int

class CurrentDayOrderCreate(CurrentDayOrderBase):
    pass

class CurrentDayOrderUpdate(BaseModel):
    day_order_id: Optional[int] = None

class CurrentDayOrderResponse(CurrentDayOrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Timetable schemas
class TimetableBase(BaseModel):
    section_id: int
    effective_from: datetime
    effective_to: Optional[datetime] = None
    is_active: bool = True

class TimetableCreate(TimetableBase):
    pass

class TimetableUpdate(BaseModel):
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: Optional[bool] = None

class TimetableResponse(TimetableBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# TimetableEntry schemas
class TimetableEntryBase(BaseModel):
    timetable_id: int
    day_order_id: int
    hour: int
    subject_id: int
    faculty_id: int

class TimetableEntryCreate(TimetableEntryBase):
    pass

class TimetableEntryBulkCreate(BaseModel):
    entries: List[TimetableEntryCreate]

class TimetableEntryUpdate(BaseModel):
    subject_id: Optional[int] = None
    faculty_id: Optional[int] = None

class TimetableEntryResponse(TimetableEntryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Complete timetable with entries
class CompleteTimeTableEntry(BaseModel):
    day_order: str
    hour: int
    subject_code: str
    subject_name: str
    faculty_name: str

class CompleteTimetable(BaseModel):
    section_name: str
    year_name: str
    batch_name: str
    department_name: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    entries: List[CompleteTimeTableEntry]


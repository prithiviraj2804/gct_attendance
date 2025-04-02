from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_session
from ..auth.models import User
from app.utils.security import get_admin_user
from .schemas import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    BatchCreate, BatchUpdate, BatchResponse,
    YearCreate, YearUpdate, YearResponse,
    SectionCreate, SectionUpdate, SectionResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    StudentResponse
)
from .schemas import (
    DayOrderCreate, DayOrderUpdate, DayOrderResponse,
    CurrentDayOrderCreate, CurrentDayOrderUpdate, CurrentDayOrderResponse
)
from app.api.auth.schemas import FacultyCreate, FacultyResponse, FacultyWithUserResponse
from .services import (
    create_department, get_department, get_departments, update_department, delete_department,
    create_batch, get_batch, get_batches, update_batch, delete_batch,
    create_year, get_year, get_years, update_year, delete_year,
    create_section, get_section, get_sections, update_section, delete_section,
    create_subject, get_subject, get_subjects, update_subject, delete_subject,
    create_day_order, get_day_order, get_day_orders, update_day_order, delete_day_order,
)
from .services import create_faculty, get_faculty_by_id, get_faculty_members

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)],
    responses={401: {"description": "Unauthorized"}, 403: {"description": "Forbidden"}},
)

# Department routes
@router.post("/departments", response_model=DepartmentResponse)
async def create_department_route(
    department: DepartmentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_department(db, department)

@router.get("/departments", response_model=List[DepartmentResponse])
async def read_departments(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_departments(db, skip, limit)

@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def read_department(
    department_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_department(db, department_id)

@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department_route(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_department(db, department_id, department)

@router.delete("/departments/{department_id}")
async def delete_department_route(
    department_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_department(db, department_id)

# Batch routes
@router.post("/batches", response_model=BatchResponse)
async def create_batch_route(
    batch: BatchCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_batch(db, batch)

@router.get("/batches", response_model=List[BatchResponse])
async def read_batches(
    department_id: int = None,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_batches(db, department_id, skip, limit)

@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def read_batch(
    batch_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_batch(db, batch_id)

@router.put("/batches/{batch_id}", response_model=BatchResponse)
async def update_batch_route(
    batch_id: int,
    batch: BatchUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_batch(db, batch_id, batch)

@router.delete("/batches/{batch_id}")
async def delete_batch_route(
    batch_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_batch(db, batch_id)

# Year routes
@router.post("/years", response_model=YearResponse)
async def create_year_route(
    year: YearCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_year(db, year)

@router.get("/years", response_model=List[YearResponse])
async def read_years(
    batch_id: int = None,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_years(db, batch_id, skip, limit)

@router.get("/years/{year_id}", response_model=YearResponse)
async def read_year(
    year_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_year(db, year_id)

@router.put("/years/{year_id}", response_model=YearResponse)
async def update_year_route(
    year_id: int,
    year: YearUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_year(db, year_id, year)

@router.delete("/years/{year_id}")
async def delete_year_route(
    year_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_year(db, year_id)

# Section routes
@router.post("/sections", response_model=SectionResponse)
async def create_section_route(
    section: SectionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_section(db, section)

@router.get("/sections", response_model=List[SectionResponse])
async def read_sections(
    year_id: int = None,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_sections(db, year_id, skip, limit)

@router.get("/sections/{section_id}", response_model=SectionResponse)
async def read_section(
    section_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_section(db, section_id)

@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section_route(
    section_id: int,
    section: SectionUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_section(db, section_id, section)

@router.delete("/sections/{section_id}")
async def delete_section_route(
    section_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_section(db, section_id)

# Subject routes
@router.post("/subjects", response_model=SubjectResponse)
async def create_subject_route(
    subject: SubjectCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_subject(db, subject)

@router.get("/subjects", response_model=List[SubjectResponse])
async def read_subjects(
    department_id: int = None,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_subjects(db, department_id, skip, limit)

@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def read_subject(
    subject_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_subject(db, subject_id)

@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject_route(
    subject_id: int,
    subject: SubjectUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_subject(db, subject_id, subject)

@router.delete("/subjects/{subject_id}")
async def delete_subject_route(
    subject_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_subject(db, subject_id)

# Day Order routes
@router.post("/day-orders", response_model=DayOrderResponse)
async def create_day_order_route(
    day_order: DayOrderCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_day_order(db, day_order)

@router.get("/day-orders", response_model=List[DayOrderResponse])
async def read_day_orders(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_day_orders(db, skip, limit)

@router.get("/day-orders/{day_order_id}", response_model=DayOrderResponse)
async def read_day_order(
    day_order_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_day_order(db, day_order_id)

@router.put("/day-orders/{day_order_id}", response_model=DayOrderResponse)
async def update_day_order_route(
    day_order_id: int,
    day_order: DayOrderUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await update_day_order(db, day_order_id, day_order)

@router.delete("/day-orders/{day_order_id}")
async def delete_day_order_route(
    day_order_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await delete_day_order(db, day_order_id)

# Faculty routes
@router.post("/faculty", response_model=FacultyWithUserResponse)
async def create_faculty_route(
    faculty: FacultyCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await create_faculty(db, faculty)

@router.get("/faculty", response_model=List[FacultyResponse])
async def read_faculty_members(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_faculty_members(db, skip, limit)

@router.get("/faculty/{faculty_id}", response_model=FacultyResponse)
async def read_faculty(
    faculty_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    return await get_faculty_by_id(db, faculty_id)

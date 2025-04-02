from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status, UploadFile
from typing import List
from app.api.attendance.models import Department, Batch, Year, Section, Student, Subject, DayOrder
from app.api.admin.schemas import (
    DepartmentCreate, DepartmentUpdate, 
    BatchCreate, BatchUpdate, 
    YearCreate, YearUpdate, 
    SectionCreate, SectionUpdate,
    SubjectCreate, SubjectUpdate,
    DayOrderCreate, DayOrderUpdate
)
from app.api.auth.models import User, Faculty
from app.api.auth.schemas import UserCreate, UserUpdate, FacultyCreate, FacultyUpdate

# Department services
async def create_department(db: AsyncSession, department: DepartmentCreate):
    db_department = Department(**department.dict())
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department

async def get_department(db: AsyncSession, department_id: int):
    result = await db.execute(select(Department).filter(Department.id == department_id))
    db_department = result.scalar_one_or_none()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department

async def get_departments(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Department).offset(skip).limit(limit))
    return result.scalars().all()

async def update_department(db: AsyncSession, department_id: int, department: DepartmentUpdate):
    db_department = await get_department(db, department_id)
    update_data = department.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_department, key, value)
    await db.commit()
    await db.refresh(db_department)
    return db_department

async def delete_department(db: AsyncSession, department_id: int):
    db_department = await get_department(db, department_id)
    await db.delete(db_department)
    await db.commit()
    return {"message": "Department deleted successfully"}

# Batch services
async def create_batch(db: AsyncSession, batch: BatchCreate):
    db_batch = Batch(**batch.dict())
    db.add(db_batch)
    await db.commit()
    await db.refresh(db_batch)
    return db_batch

async def get_batch(db: AsyncSession, batch_id: int):
    result = await db.execute(select(Batch).filter(Batch.id == batch_id))
    db_batch = result.scalar_one_or_none()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch

async def get_batches(db: AsyncSession, department_id: int = None, skip: int = 0, limit: int = 100):
    query = select(Batch)
    if department_id:
        query = query.filter(Batch.department_id == department_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_batch(db: AsyncSession, batch_id: int, batch: BatchUpdate):
    db_batch = await get_batch(db, batch_id)
    update_data = batch.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_batch, key, value)
    await db.commit()
    await db.refresh(db_batch)
    return db_batch

async def delete_batch(db: AsyncSession, batch_id: int):
    db_batch = await get_batch(db, batch_id)
    await db.delete(db_batch)
    await db.commit()
    return {"message": "Batch deleted successfully"}

# Year services
async def create_year(db: AsyncSession, year: YearCreate):
    db_year = Year(**year.dict())
    db.add(db_year)
    await db.commit()
    await db.refresh(db_year)
    return db_year

async def get_year(db: AsyncSession, year_id: int):
    result = await db.execute(select(Year).filter(Year.id == year_id))
    db_year = result.scalar_one_or_none()
    if not db_year:
        raise HTTPException(status_code=404, detail="Year not found")
    return db_year

async def get_years(db: AsyncSession, batch_id: int = None, skip: int = 0, limit: int = 100):
    query = select(Year)
    if batch_id:
        query = query.filter(Year.batch_id == batch_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_year(db: AsyncSession, year_id: int, year: YearUpdate):
    db_year = await get_year(db, year_id)
    update_data = year.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_year, key, value)
    await db.commit()
    await db.refresh(db_year)
    return db_year

async def delete_year(db: AsyncSession, year_id: int):
    db_year = await get_year(db, year_id)
    await db.delete(db_year)
    await db.commit()
    return {"message": "Year deleted successfully"}

# Section services
async def create_section(db: AsyncSession, section: SectionCreate):
    db_section = Section(**section.dict())
    db.add(db_section)
    await db.commit()
    await db.refresh(db_section)
    return db_section

async def get_section(db: AsyncSession, section_id: int):
    result = await db.execute(select(Section).filter(Section.id == section_id))
    db_section = result.scalar_one_or_none()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

async def get_sections(db: AsyncSession, year_id: int = None, skip: int = 0, limit: int = 100):
    query = select(Section)
    if year_id:
        query = query.filter(Section.year_id == year_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_section(db: AsyncSession, section_id: int, section: SectionUpdate):
    db_section = await get_section(db, section_id)
    update_data = section.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_section, key, value)
    await db.commit()
    await db.refresh(db_section)
    return db_section

async def delete_section(db: AsyncSession, section_id: int):
    db_section = await get_section(db, section_id)
    await db.delete(db_section)
    await db.commit()
    return {"message": "Section deleted successfully"}

# Subject services
async def create_subject(db: AsyncSession, subject: SubjectCreate):
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    await db.commit()
    await db.refresh(db_subject)
    return db_subject

async def get_subject(db: AsyncSession, subject_id: int):
    result = await db.execute(select(Subject).filter(Subject.id == subject_id))
    db_subject = result.scalar_one_or_none()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

async def get_subjects(db: AsyncSession, department_id: int = None, skip: int = 0, limit: int = 100):
    query = select(Subject)
    if department_id:
        query = query.filter(Subject.department_id == department_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_subject(db: AsyncSession, subject_id: int, subject: SubjectUpdate):
    db_subject = await get_subject(db, subject_id)
    update_data = subject.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subject, key, value)
    await db.commit()
    await db.refresh(db_subject)
    return db_subject

async def delete_subject(db: AsyncSession, subject_id: int):
    db_subject = await get_subject(db, subject_id)
    await db.delete(db_subject)
    await db.commit()
    return {"message": "Subject deleted successfully"}

# Day Order services
async def create_day_order(db: AsyncSession, day_order: DayOrderCreate):
    db_day_order = DayOrder(**day_order.dict())
    db.add(db_day_order)
    await db.commit()
    await db.refresh(db_day_order)
    return db_day_order

async def get_day_order(db: AsyncSession, day_order_id: int):
    result = await db.execute(select(DayOrder).filter(DayOrder.id == day_order_id))
    db_day_order = result.scalar_one_or_none()
    if not db_day_order:
        raise HTTPException(status_code=404, detail="Day Order not found")
    return db_day_order

async def get_day_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(DayOrder).offset(skip).limit(limit))
    return result.scalars().all()

async def update_day_order(db: AsyncSession, day_order_id: int, day_order: DayOrderUpdate):
    db_day_order = await get_day_order(db, day_order_id)
    update_data = day_order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_day_order, key, value)
    await db.commit()
    await db.refresh(db_day_order)
    return db_day_order

async def delete_day_order(db: AsyncSession, day_order_id: int):
    db_day_order = await get_day_order(db, day_order_id)
    await db.delete(db_day_order)
    await db.commit()
    return {"message": "Day Order deleted successfully"}

# User and Faculty services
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def get_faculty_by_id(db: AsyncSession, faculty_id: int):
    result = await db.execute(select(Faculty).filter(Faculty.id == faculty_id))
    return result.scalar_one_or_none()

async def get_faculty_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Faculty).filter(Faculty.user_id == user_id))
    return result.scalar_one_or_none()

async def get_faculty_members(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Faculty).offset(skip).limit(limit))
    return result.scalars().all()

async def create_faculty(db: AsyncSession, faculty_create: FacultyCreate):
    if await get_user_by_username(db, faculty_create.user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await get_user_by_email(db, faculty_create.user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    from . import create_user
    user = await create_user(db, faculty_create.user)
    
    db_faculty = Faculty(
        user_id=user.id,
        department_id=faculty_create.department_id,
        employee_id=faculty_create.employee_id,
        designation=faculty_create.designation
    )
    db.add(db_faculty)
    await db.commit()
    await db.refresh(db_faculty)
    return db_faculty

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_faculty(db: AsyncSession, faculty_id: int, faculty_update: FacultyUpdate):
    db_faculty = await get_faculty_by_id(db, faculty_id)
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    update_data = faculty_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_faculty, key, value)
    
    await db.commit()
    await db.refresh(db_faculty)
    return db_faculty

async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(db_user)
    await db.commit()
    return {"message": "User deleted successfully"}

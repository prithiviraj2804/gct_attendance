from datetime import datetime
import io
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import UUID

from app.api.attendance.models import Attendance, Student, Batch, Year, Section
from app.api.attendance.services import AttendanceService
from main import templates
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pandas as pd

router = APIRouter()

@router.post("/upload_students/")
async def upload_students(
    batch_name: str = Form(...),  # Accept 'batch_name' from form data
    year_name: str = Form(...),   # Accept 'year_name' from form data
    section_name: str = Form(...), # Accept 'section_name' from form data
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    # Pass batch_name, year_name, and section_name to the service
    result = await AttendanceService(db).upload_file(file, batch_name, year_name, section_name)
    return result

@router.get("/upload_students/")
async def upload_students(request: Request):
    return templates.TemplateResponse("upload_students.html", {"request": request})

@router.get("/mark_attendance/{batch_name}/{year_name}/{section_name}")
async def mark_attendance(batch_name: str, year_name: str, section_name: str, request: Request, db: AsyncSession = Depends(get_session)):
    # Pass batch_name, year_name, and section_name to the service to get the students
    result = await AttendanceService(db).get_students(batch_name, year_name, section_name, request)
    return result

@router.post("/submit_attendance/{batch_name}/{year_name}/{section_name}")
async def submit_attendance(batch_name: str, year_name: str, section_name: str, attendance_data: List[dict], db: AsyncSession = Depends(get_session)):
    # Pass batch_name, year_name, section_name, and attendance_data to the service for submission
    result = await AttendanceService(db).submit_attendance(batch_name, year_name, section_name, attendance_data)
    return result

@router.get("/view_attendance/{batch_name}/{year_name}/{section_name}")
async def view_attendance(batch_name: str, year_name: str, section_name: str, request: Request, db: AsyncSession = Depends(get_session)):
    # Pass batch_name, year_name, and section_name to the service for viewing attendance
    result = await AttendanceService(db).view_attendance(batch_name, year_name, section_name, request)
    return result


'''
=======================================================
Batch , Year, Section, Student, Attendance
=======================================================

'''

# POST route to create a new batch
@router.post("/batch/")
async def create_batch(name: str = Form(...), db: AsyncSession = Depends(get_session)):
    batch = Batch(name=name)
    db.add(batch)
    await db.commit()
    return {"message": "Batch created successfully!", "batch": {"id": batch.id, "name": batch.name}}

# GET route to get all batches
@router.get("/batch/")
async def get_batches(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Batch))
    batches = result.scalars().all()
    return {"batches": [{"id": batch.id, "name": batch.name} for batch in batches]}

# POST route to create a new year under a specific batch
@router.post("/year/{batch_id}/")
async def create_year(batch_id: str, name: str = Form(...), db: AsyncSession = Depends(get_session)):
    # Check if the batch exists
    batch = await db.execute(select(Batch).filter(Batch.id == batch_id))
    batch = batch.scalars().first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    year = Year(name=name, batch_id=batch_id)
    db.add(year)
    await db.commit()
    return {"message": "Year created successfully!", "year": {"id": year.id, "name": year.name}}

# GET route to get all years for a specific batch
@router.get("/year/{batch_id}/")
async def get_years(batch_id: str, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Year).filter(Year.batch_id == batch_id))
    years = result.scalars().all()
    return {"years": [{"id": year.id, "name": year.name} for year in years]}

# GET route to get all years
@router.get("/year/")
async def get_all_years(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Year))
    years = result.scalars().all()
    return {"years": [{"id": year.id, "batch_id": year.batch_id, "name": year.name} for year in years]}

# POST route to create a new section under a specific year
@router.post("/section/{year_id}/")
async def create_section(year_id: str, name: str = Form(...), db: AsyncSession = Depends(get_session)):
    # Check if the year exists
    year = await db.execute(select(Year).filter(Year.id == year_id))
    year = year.scalars().first()
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")

    section = Section(name=name, year_id=year_id)
    db.add(section)
    await db.commit()
    return {"message": "Section created successfully!", "section": {"id": section.id, "name": section.name}}

# GET route to get all sections for a specific year
@router.get("/section/{year_id}/")
async def get_sections(year_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Section).filter(Section.year_id == year_id))
    sections = result.scalars().all()
    return {"sections": [{"id": section.id, "name": section.name} for section in sections]}

# GET route to get all sections
@router.get("/section/")
async def get_all_sections(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Section))
    sections = result.scalars().all()
    return {"sections": [{"id": section.id, "year_id": section.year_id, "name": section.name} for section in sections]}

@router.get("/add_batch/")
async def add_batch(request: Request):
    return templates.TemplateResponse("add_batch.html", {"request": request})

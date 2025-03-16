import io
from datetime import datetime
from typing import List

import pandas as pd
from fastapi import (APIRouter, Depends, File, Form, HTTPException, Request,
                     UploadFile)
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.attendance.models import Attendance, Batch, Section, Student, Year
from app.api.attendance.schemas import AttendanceCreate, BatchCreate, DepartmentCreate, SectionCreate, UploadFileSchema, YearCreate
from app.api.attendance.services import AttendanceService
from app.core.database import get_session
from app.utils.security import get_current_user
from main import templates

router = APIRouter()


@router.post("/upload_students/")
async def upload_students(
    data: UploadFileSchema,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
):
    # Pass batch_name, year_name, and section_name to the service
    result = await AttendanceService(db).upload_file(data, file)
    return result




'''
=======================================================
Batch , Year, Section, Student, Attendance
=======================================================

'''

@router.post("/create_department/")
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Access Denied: Only admins can create departments.")

    return await AttendanceService(db).create_department(department_data)

@router.post("/create_batch/")
async def create_batch(
    batch_data: BatchCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Access Denied: Only admins can create batches.")

    return await AttendanceService(db).create_batch(batch_data)

@router.post("/create_year/")
async def create_year(
    year_data: YearCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Access Denied: Only admins can create years.")

    return await AttendanceService(db).create_year(year_data)

@router.post("/create_section/")
async def create_section(
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Access Denied: Only admins can create sections.")

    return await AttendanceService(db).create_section(section_data)


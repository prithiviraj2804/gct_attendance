import io
from datetime import datetime
from typing import List
from uuid import UUID

import pandas as pd
from fastapi import (APIRouter, Depends, File, Form, HTTPException, 
                     UploadFile)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.attendance.schemas import ( BatchCreate,
                                        DepartmentCreate, SectionCreate,
                                        StudentCreate, StudentResponse, StudentUUIDs,
                                         YearCreate)
from app.api.attendance.services import AttendanceService
from app.core.database import get_session
from app.utils.security import get_current_user
from main import templates

router = APIRouter()


@router.post("/upload_students/")
async def upload_students(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),  # Get user from JWT token
):
    print("User: ", user.role.name)
    # Ensure the user is a faculty
    if not user or user.role.name != "faculty" :
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    # Automatically assign students to the user's section
    result = await AttendanceService(db).upload_file(file, user.section_id)
    
    return result

@router.get("/students", response_model=List[StudentResponse])
async def fetch_students(
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    students = await AttendanceService(db).get_students_by_section(user)
    return students

@router.get("/students/{student_id}",response_model=StudentResponse)
async def fetch_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    student = await AttendanceService(db).get_student(student_id)
    return student

@router.post("/students/")
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    
    if not user or user.role.name != "faculty" :
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).create_student(student_data, user.section_id)

@router.put("/students/{student_id}")
async def update_student(
    student_id: UUID,
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "faculty" :
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).update_student(student_data, student_id) 

@router.delete("/students/{student_id}")
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    if not user or user.role.name != "faculty" :
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).delete_student(student_id)


@router.post("/mark_attendance/")
async def mark_attendance(
    student_uuids: StudentUUIDs,  # List of student UUIDs to mark attendance for
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),  # Get the current logged-in user
):
    # Ensure the user has the correct role (faculty)
    if not user or user.role.name != "faculty":
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can mark attendance.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    # Call the service to mark attendance for the specified students
    return await AttendanceService(db).mark_attendance(student_uuids, user.section_id)

@router.get("/download_attendance/")
async def download_attendance(
    db: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
):
    # Ensure the user has the correct role (faculty)
    if not user or user.role.name != "faculty":
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can download attendance.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="Error: You are not assigned to any section.")

    # Call the service to download attendance data
    attendance_data = await AttendanceService(db).download_attendance(user.section_id)

    # Convert the data to a CSV file
    df = pd.DataFrame(attendance_data)
    csv = df.to_csv(index=False)

    # Return the CSV file as a downloadable file
    return csv
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


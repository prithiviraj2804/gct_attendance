import io
from datetime import datetime
from typing import List
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.attendance.schemas import (AttendanceBatchCreate, AttendanceCreate, BatchCreate, DepartmentCreate,
                                        SectionCreate, StudentCreate,
                                        StudentResponse, TimetableCreate, TimetableResponse,
                                        YearCreate)
from app.api.attendance.services import AttendanceService
from app.core.database import get_session
from app.utils.security import get_current_user
from main import templates

router = APIRouter()

'''
===========================================================
# Students CRUD 
=============================================================

'''


@router.post("/upload_students/", tags=["Students"])
async def upload_students(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),  # Get user from JWT token
):
    print("User: ", user.role.name)
    # Ensure the user is a faculty
    if not user or user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    # Automatically assign students to the user's section
    result = await AttendanceService(db).upload_file(file, user.section_id)

    return result


@router.get("/students", response_model=List[StudentResponse], tags=["Students"])
async def fetch_students(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    students = await AttendanceService(db).get_students_by_section(user)
    return students


@router.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
async def fetch_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    student = await AttendanceService(db).get_student(student_id)
    return student


@router.post("/students/", tags=["Students"])
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):

    if not user or user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).create_student(student_data, user.section_id)


@router.put("/students/{student_id}", tags=["Students"])
async def update_student(
    student_id: UUID,
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).update_student(student_data, student_id)


@router.delete("/students/{student_id}", tags=["Students"])
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).delete_student(student_id)


'''
=======================================================
# Timetable CRUD
=======================================================
'''


@router.post("/timetable/{section_id}", tags=["Timetable"])
async def assign_timetable_to_section(
    section_id: UUID,
    timetable_data: TimetableCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload student data.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    return await AttendanceService(db).assign_timetable(section_id, timetable_data.slots)


@router.get("/timetable/{section_id}", tags=["Timetable"])
async def get_timetable_for_section(
    section_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can view the timetable.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    timetable = await AttendanceService(db).get_timetable(section_id)
    return timetable


'''
=======================================================
# Attendance Marking CRUD
=======================================================
'''


@router.post("/mark_attendance")
async def mark_attendance(attendance_data: AttendanceBatchCreate,
                          current_user: dict = Depends(get_current_user),
                          db: AsyncSession = Depends(get_session)):

    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can view the timetable.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    attendance = await AttendanceService(db).mark_attendance(current_user.section_id,attendance_data)
    return attendance

@router.get("/get_attendance")
async def get_section_attendance(current_user = Depends(get_current_user),db : AsyncSession = Depends(get_session)):
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can view the timetable.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")
    
    result = await  AttendanceService(db).get_section_attendance(current_user.section_id)
    return result

@router.get("/get-attendance/{timetable_slot_id}")
async def get_attendance_by_hour(timetable_slot_id: str,
                                current_user = Depends(get_current_user),
                                db : AsyncSession = Depends(get_session)):
    result = await AttendanceService(db).get_attendance_by_subject(timetable_slot_id)
    return result


'''
=======================================================
Batch , Year, Section, Student, Attendance
=======================================================

'''


@router.post("/create_department/", tags=["Admin"])
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create departments.")

    return await AttendanceService(db).create_department(department_data)


@router.post("/create_batch/", tags=["Admin"])
async def create_batch(
    batch_data: BatchCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create batches.")

    return await AttendanceService(db).create_batch(batch_data)


@router.post("/create_year/", tags=["Admin"])
async def create_year(
    year_data: YearCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create years.")

    return await AttendanceService(db).create_year(year_data)


@router.post("/create_section/", tags=["Admin"])
async def create_section(
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create sections.")

    return await AttendanceService(db).create_section(section_data)

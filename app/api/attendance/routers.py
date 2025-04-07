import io
from datetime import date, datetime
from typing import List
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.attendance.schemas import (AttendanceBatchCreate,  BatchCreate, DepartmentCreate,
                                        SectionCreate, StudentCreate,
                                        StudentResponse, TimetableCreate, TimetableResponse,
                                        YearCreate)
from app.api.attendance.services import AdminService, AttendanceService, StudentService, TimetableService
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
            status_code=403, detail="Access Denied: Only faculty can upload student data."
        )

    # Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section."
        )

    # Check if the uploaded file is an Excel file
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload an Excel file."
        )

    # Automatically assign students to the user's section
    result = await StudentService(db).upload_file(file, user.section_id)

    return result


@router.get("/students", tags=["Students"])
async def fetch_students(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    students = await StudentService(db).get_students_by_section(user)
    return students


@router.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
async def fetch_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    student = await StudentService(db).get_student(student_id)
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

    return await StudentService(db).create_student(student_data, user.section_id)


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

    return await StudentService(db).update_student(student_data, student_id)


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

    return await StudentService(db).delete_student(student_id)


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
    # Check for faculty role
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can upload timetable data.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")

    # Assign timetable to the section
    result = await TimetableService(db).assign_timetable(section_id, timetable_data.slots)
    return {"message": "Timetable assigned successfully", "timetable": result}


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

    timetable = await TimetableService(db).get_timetable(section_id)
    return timetable

@router.put("/timetable/{section_id}", tags=["Timetable"])
async def update_timetable_for_section(
    section_id: UUID,
    timetable_data: TimetableCreate,
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

    # Update timetable for the section
    result = await TimetableService(db).update_timetable(section_id, timetable_data.slots)
    return {"message": "Timetable updated successfully", "timetable": result}

@router.delete("/timetable/{section_id}", tags=["Timetable"])
async def delete_timetable_for_section(
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

    # Delete timetable for the section
    result = await TimetableService(db).delete_timetable(section_id)
    return {"message": "Timetable deleted successfully", "timetable": result}


'''
=======================================================
# Attendance Marking CRUD
=======================================================
'''

@router.post("/attendances",tags=["Attendance"])
async def mark_attendance(
    request: Request,
    attendance_data: AttendanceBatchCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Check for faculty role
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can mark attendance."
        )

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section."
        )

    # Call the attendance service to mark attendance
    attendance = await AttendanceService(db).mark_attendance(current_user.section_id,attendance_data)
    return attendance

@router.get("/attendances",tags=["Attendance"])
async def get_section_attendance(current_user = Depends(get_current_user),db : AsyncSession = Depends(get_session)):
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can view the Attendance.")

    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")
    
    result = await  AttendanceService(db).get_section_attendance(current_user.section_id)
    return result

@router.get("/attendances/{section_id}/{date}/{day_of_week}",tags=["Attendance"])
async def get_attendance_by_date(section_id: UUID, date: date, day_of_week: int,
                                current_user = Depends(get_current_user),
                                db : AsyncSession = Depends(get_session)):
    # Check for faculty role
    if not current_user or current_user.role.name != "faculty":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only faculty can view the Attendance.")
    
    # Ensure the faculty is assigned to a section
    if not current_user.section_id:
        raise HTTPException(
            status_code=400, detail="Error: You are not assigned to any section.")
    
    result = await AttendanceService(db).get_attendance_table(section_id, date,day_of_week)
    return result


@router.get("/attendances/{timetable_slot_id}",tags=["Attendance"])
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

@router.get("/departments", tags=["Admin"])
async def get_departments(
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view departments.")

    return await AdminService(db).get_departments()


@router.post("/departments", tags=["Admin"])
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create departments.")

    return await AdminService(db).create_department(department_data)

@router.get("/departments/{department_id}", tags=["Admin"])
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view departments.")

    return await AdminService(db).get_department(department_id)

@router.put("/departments/{department_id}", tags=["Admin"])
async def update_department(
    department_id: UUID,
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can update departments.")

    return await AdminService(db).update_department(department_id, department_data)


@router.delete("/departments/{department_id}", tags=["Admin"])
async def delete_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can delete departments.")

    return await AdminService(db).delete_department(department_id)


@router.post("/batches", tags=["Admin"])
async def create_batch(
    batch_data: BatchCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create batches.")

    return await AdminService(db).create_batch(batch_data)

@router.get("/batches", tags=["Admin"])
async def get_batches(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view batches.")

    return await AdminService(db).get_batches()

@router.get("/batches/{batch_id}", tags=["Admin"])
async def get_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view batches.")

    return await AdminService(db).get_batch(batch_id)


@router.put("/batches/{batch_id}", tags=["Admin"])
async def update_batch(
    batch_id: UUID,
    batch_data: BatchCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can update batches.")

    return await AdminService(db).update_batch(batch_id, batch_data)

@router.delete("/batches/{batch_id}", tags=["Admin"])
async def delete_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can delete batches.")

    return await AdminService(db).delete_batch(batch_id)




@router.post("/years", tags=["Admin"])
async def create_year(
    year_data: YearCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create years.")

    return await AdminService(db).create_year(year_data)

@router.get("/years", tags=["Admin"])
async def get_years(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view years.")

    return await AdminService(db).get_years()

@router.get("/years/{year_id}", tags=["Admin"])
async def get_year(
    year_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view years.")

    return await AdminService(db).get_year(year_id)

@router.put("/years/{year_id}", tags=["Admin"])
async def update_year(
    year_id: UUID,
    year_data: YearCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can update years.")

    return await AdminService(db).update_year(year_id, year_data)

@router.delete("/years/{year_id}", tags=["Admin"])
async def delete_year(
    year_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can delete years.")

    return await AdminService(db).delete_year(year_id)



@router.post("/sections", tags=["Admin"])
async def create_section(
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can create sections.")

    return await AdminService(db).create_section(section_data)

@router.get("/sections", tags=["Admin"])
async def get_sections(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view sections.")

    return await AdminService(db).get_sections()

@router.get("/sections/{section_id}", tags=["Admin"])
async def get_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can view sections.")

    return await AdminService(db).get_section(section_id)

@router.put("/sections/{section_id}", tags=["Admin"])
async def update_section(
    section_id: UUID,
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can update sections.")

    return await AdminService(db).update_section(section_id, section_data)

@router.delete("/sections/{section_id}", tags=["Admin"])
async def delete_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not user or user.role.name != "admin":
        raise HTTPException(
            status_code=403, detail="Access Denied: Only admins can delete sections.")

    return await AdminService(db).delete_section(section_id)
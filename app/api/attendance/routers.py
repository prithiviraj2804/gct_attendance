

from datetime import datetime
import io
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.api.attendance.models import Attendance, Student
from main import templates
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pandas as pd

router = APIRouter()

@router.post("/upload_students/")
async def upload_students(
    section: str = Form(...),  # Accept 'section' from form data
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    # Save the uploaded file temporarily
    contents = await file.read()

    # Wrap the byte content into a BytesIO object
    file_like_object = io.BytesIO(contents)

    # Load the Excel file into pandas DataFrame
    try:
        df = pd.read_excel(file_like_object, engine="openpyxl")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    # Check if required columns exist
    required_columns = ["name"]
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail="Excel file must contain 'name' column")

    # Iterate over the rows in the DataFrame and insert into the database
    for _, row in df.iterrows():
        student = Student(name=row["name"], section=section)
        db.add(student)

    # Commit the changes to the database
    await db.commit()

    return {"message": f"Successfully uploaded {len(df)} students!"}


@router.get("/upload_students/")
async def upload_students(request: Request):
    return templates.TemplateResponse("upload_students.html", {"request": request})

@router.get("/mark_attendance/{section}")
async def mark_attendance(section: str, request: Request, db: AsyncSession = Depends(get_session)):
    # Get the current date
    current_date = datetime.utcnow().date()

    # Fetch the students for the given section
    result = await db.execute(select(Student).filter(Student.section == section))
    students = result.scalars().all()

    # Render the template with student data and the current date
    return templates.TemplateResponse("attendance.html", {
        "request": request,
        "section": section,
        "students": students,
        "current_date": current_date
    })


@router.post("/submit_attendance/{section}")
async def submit_attendance(section: str, attendance_data: List[dict], db: AsyncSession = Depends(get_session)):
    """
    Submit attendance for a specific section. Each attendance record contains a student ID and status ("Present" or "Absent").
    """
    # Fetch the students in the given section
    result = await db.execute(select(Student).filter(Student.section == section))
    students = result.scalars().all()

    # Get today's date for attendance records
    current_date = datetime.utcnow().date()

    # If no students found in the section
    if not students:
        raise HTTPException(status_code=404, detail="No students found for this section")

    # Map incoming attendance data to a dictionary with student_id as key
    student_attendance_map = {str(student.id): student for student in students}
    
    # Check if all student IDs in attendance_data exist
    for attendance in attendance_data:
        student_id = attendance.get('student_id')
        if str(student_id) not in student_attendance_map:
            raise HTTPException(status_code=400, detail=f"Invalid student ID: {student_id}")

    # Process the attendance
    for attendance in attendance_data:
        student_id = attendance.get('student_id')
        status = attendance.get('status')  # "Present" or "Absent"

        # Check if the attendance for this student already exists
        existing_attendance = await db.execute(
            select(Attendance).filter(Attendance.student_id == student_id, Attendance.date == current_date)
        )
        existing_attendance_record = existing_attendance.scalars().first()

        if existing_attendance_record:
            # Update the status of existing attendance
            existing_attendance_record.status = status
        else:
            # Add a new attendance record for the student
            new_attendance = Attendance(student_id=student_id, date=current_date, status=status)
            db.add(new_attendance)

    # Commit the changes to the database
    await db.commit()

    return {"message": "Attendance has been successfully submitted!"}

@router.get("/view_attendance/{section}")
async def view_attendance(section: str, request: Request, db: AsyncSession = Depends(get_session)):
    # Fetch the students in the given section
    result = await db.execute(select(Student).filter(Student.section == section))
    students = result.scalars().all()

    # Get today's date for attendance records
    current_date = datetime.utcnow().date()

    # If no students found in the section
    if not students:
        raise HTTPException(status_code=404, detail="No students found for this section")

    # Fetch the attendance records for the students in the section
    attendance_records = await db.execute(
        select(Attendance).join(Student).filter(Student.section == section, Attendance.date == current_date)
    )
    attendance_data = attendance_records.scalars().all()

    count = len(attendance_data)

    # Map the attendance data to a dictionary with student ID as key
    attendance_map = {attendance.student_id: attendance for attendance in attendance_data}

    # Render the template with attendance data
    return templates.TemplateResponse("view_attendance.html", {
        "request": request,
        "section": section,
        "students": students,
        "current_date": current_date,
        "attendance_map": attendance_map,
        "count": count
    })
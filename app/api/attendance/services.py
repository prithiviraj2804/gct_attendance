from datetime import datetime
import io
from typing import List
from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from main import templates

from app.api.attendance.models import Attendance, Student, Section, Year, Batch


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, file, batch_name: str, year_name: str, section_name: str):
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

        # Fetch the batch, year, and section
        batch = await self.db.execute(select(Batch).filter(Batch.name == batch_name))
        batch = batch.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        year = await self.db.execute(select(Year).filter(Year.name == year_name, Year.batch_id == batch.id))
        year = year.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        section = await self.db.execute(select(Section).filter(Section.name == section_name, Section.year_id == year.id))
        section = section.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Iterate over the rows in the DataFrame and insert students into the database
        for _, row in df.iterrows():
            student = Student(name=row["name"], section_id=section.id)
            self.db.add(student)

        # Commit the changes to the database
        await self.db.commit()

        return {"message": f"Successfully uploaded {len(df)} students to {section_name}!"}

    async def get_students(self, batch_name: str, year_name: str, section_name: str, request):
        # Fetch batch, year, and section
        batch = await self.db.execute(select(Batch).filter(Batch.name == batch_name))
        batch = batch.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        year = await self.db.execute(select(Year).filter(Year.name == year_name, Year.batch_id == batch.id))
        year = year.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        section = await self.db.execute(select(Section).filter(Section.name == section_name, Section.year_id == year.id))
        section = section.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Fetch the students for the given section
        result = await self.db.execute(select(Student).filter(Student.section_id == section.id))
        students = result.scalars().all()

        # Get the current date
        current_date = datetime.utcnow().date()

        # Render the template with student data and the current date
        return templates.TemplateResponse("attendance.html", {
            "request": request,
            "section": section_name,
            "students": students,
            "current_date": current_date
        })

    async def submit_attendance(self, batch_name: str, year_name: str, section_name: str, attendance_data: List[dict]):
        # Fetch batch, year, and section
        batch = await self.db.execute(select(Batch).filter(Batch.name == batch_name))
        batch = batch.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        year = await self.db.execute(select(Year).filter(Year.name == year_name, Year.batch_id == batch.id))
        year = year.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        section = await self.db.execute(select(Section).filter(Section.name == section_name, Section.year_id == year.id))
        section = section.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Fetch the students for the given section
        result = await self.db.execute(select(Student).filter(Student.section_id == section.id))
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
            existing_attendance = await self.db.execute(
                select(Attendance).filter(Attendance.student_id == student_id, Attendance.date == current_date)
            )
            existing_attendance_record = existing_attendance.scalars().first()

            if existing_attendance_record:
                # Update the status of existing attendance
                existing_attendance_record.status = status
            else:
                # Add a new attendance record for the student
                new_attendance = Attendance(student_id=student_id, date=current_date, status=status)
                self.db.add(new_attendance)

        # Commit the changes to the database
        await self.db.commit()

        return {"message": "Attendance has been successfully submitted!"}

    async def view_attendance(self, batch_name: str, year_name: str, section_name: str, request):
        # Fetch batch, year, and section
        batch = await self.db.execute(select(Batch).filter(Batch.name == batch_name))
        batch = batch.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        year = await self.db.execute(select(Year).filter(Year.name == year_name, Year.batch_id == batch.id))
        year = year.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        section = await self.db.execute(select(Section).filter(Section.name == section_name, Section.year_id == year.id))
        section = section.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Fetch the students in the given section
        result = await self.db.execute(select(Student).filter(Student.section_id == section.id))
        students = result.scalars().all()

        # Get today's date for attendance records
        current_date = datetime.utcnow().date()

        # If no students found in the section
        if not students:
            raise HTTPException(status_code=404, detail="No students found for this section")

        # Fetch the attendance records for the students in the section
        attendance_records = await self.db.execute(
            select(Attendance).join(Student).filter(Student.section_id == section.id, Attendance.date == current_date)
        )
        attendance_data = attendance_records.scalars().all()

        count = len(attendance_data)

        # Map the attendance data to a dictionary with student ID as key
        attendance_map = {attendance.student_id: attendance for attendance in attendance_data}

        # Render the template with attendance data
        return templates.TemplateResponse("view_attendance.html", {
            "request": request,
            "section": section_name,
            "students": students,
            "current_date": current_date,
            "attendance_map": attendance_map,
            "count": count
        })

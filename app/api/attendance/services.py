from datetime import datetime
import io
import time
from typing import List
from uuid import UUID
from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.attendance.schemas import StudentUUIDs
from app.api.auth.models import User
from main import templates

from app.api.attendance.models import Attendance, Department, Student, Section, Timetable, TimetableSlot, Year, Batch


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, file, section_id):
        # Read the Excel file
        contents = await file.read()
        excel_data = io.BytesIO(contents)  # ✅ Wrap in BytesIO
        df = pd.read_excel(excel_data, engine="openpyxl")  # ✅ Corrected
        # 🔹 Ensure required columns exist
        required_columns = {"name", "register_number"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Invalid file format. Required columns: {required_columns}")
        # 🔹 Validate if section exists
        query = select(Section).where(Section.id == section_id)
        result = await self.db.execute(query)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found.")
        # 🔹 Insert students into the database
        students = []
        for _, row in df.iterrows():
            student = Student(
                name=row["name"],
                section_id=section_id
            )
            self.db.add(student)
            students.append(student)

        await self.db.commit()
        return {"message": "Students uploaded successfully", "total": len(students)}

    async def get_students_by_section(self, user):
        """
        Fetch all students from the section assigned to the faculty.
        Admins can view all students.
        """
            # 🔹 Ensure the faculty is assigned to a section
        if not user.section_id:
            raise HTTPException(status_code=403, detail="Access Denied: No section assigned.")
            
            # 🔹 Fetch students in the faculty's section
        query = select(Student).where(Student.section_id == user.section_id)

        result = await self.db.execute(query)
        students = result.scalars().all()

        return students
    
    async def get_student(self, student_id):
        """
        Fetch
        """
        query = select(Student).where(Student.id == student_id)
        result = await self.db.execute(query)
        student = result.scalars().first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found.")
        return student
    
    async def create_student(self, student_data,section_id):
        new_student = Student(name=student_data.name, section_id=section_id)
        self.db.add(new_student)
        await self.db.commit()
        return new_student

    async def update_student(self, student_data, student_id):
        # Fetch the student from the database
        query = await self.db.execute(select(Student).where(Student.id == student_id))
        student = query.scalars().first()
        if not student:
            raise HTTPException(
                detail="Student Not Found",
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if student_data.name is not None:
            update_fields["name"] = student_data.name

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                Student.__table__.update().where(Student.id == student_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "Student record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )

    async def delete_student(self, student_id):
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalars().first()
        if not student:
            raise HTTPException(
                detail="Student Not Found",
                status_code=404
            )
        await self.db.delete(student)
        await self.db.commit()
        return {"message": "Student record deleted successfully"}
    

    '''
    ====================================================
    # Mark Attendance CRUD Services
    ====================================================
    '''
    async def mark_attendance(self, section_id, attendance_data):
        # Validate section and date
        query = select(Section).where(Section.id == section_id)
        result = await self.db.execute(query)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Validate all students in the section
        query = select(Student).where(Student.section_id == section_id)
        result = await self.db.execute(query)
        students_in_section = result.scalars().all()
        if len(students_in_section) != len(attendance_data.attendances):
            raise HTTPException(status_code=400, detail="Number of students and attendance data do not match")

        # Validate timetable slot
        for attendance in attendance_data.attendances:
            query = select(TimetableSlot).where(TimetableSlot.id == attendance.timetable_slot_id)
            result = await self.db.execute(query)
            timetable_slot = result.scalars().first()
            if not timetable_slot:
                raise HTTPException(status_code=404, detail="Timetable slot not found")

        # Mark attendance for each student
        attendance_entries = []
        for attendance in attendance_data.attendances:
            new_attendance = Attendance(
                student_id=attendance.student_id,
                timetable_slot_id=attendance.timetable_slot_id,
                date=attendance_data.date,
                is_present=attendance.is_present
            )
            self.db.add(new_attendance)
            attendance_entries.append(new_attendance)

        await self.db.commit()
        return attendance_entries



    '''
    Initial Creation of Batch, Year, Section
    '''


    # 🔹 Create Batch (Only Admins)
    async def create_batch(self, batch_data):

        new_batch = Batch(name=batch_data.name,
                        department_id=batch_data.department_id)
        self.db.add(new_batch)
        await self.db.commit()
        return new_batch


    # 🔹 Create Year (Only Admins)
    async def create_year(self,  year_data):

        new_year = Year(name=year_data.name, batch_id=year_data.batch_id)
        self.db.add(new_year)
        await self.db.commit()
        return new_year


    # 🔹 Create Section (Only Admins)
    async def create_section(self,  section_data):

        new_section = Section(name=section_data.name, year_id=section_data.year_id)
        self.db.add(new_section)
        await self.db.commit()
        return new_section


    async def assign_timetable(self, section_id, timetable_data):
        timetable = Timetable(section_id=section_id)
        self.db.add(timetable)
        await self.db.commit()
        await self.db.refresh(timetable)

        for slot_data in timetable_data:
            timetable_slot = TimetableSlot(
                timetable_id=timetable.id,
                day_of_week=slot_data.day_of_week,
                hour=slot_data.hour,
                subject_name=slot_data.subject_name,
                subject_code=slot_data.subject_code
            )
            self.db.add(timetable_slot)

        await self.db.commit()
        return timetable
            
    async def get_timetable(self, section_id):
        query = select(Timetable).where(Timetable.section_id == section_id)
        result = await self.db.execute(query)
        timetable = result.scalars().first()
        if not timetable:
            raise HTTPException(status_code=404, detail="Timetable not found.")
        
        query = select(TimetableSlot).where(TimetableSlot.timetable_id == timetable.id)
        result = await self.db.execute(query)
        slots = result.scalars().all()
        
        return slots
from datetime import datetime
import io
from typing import List
from uuid import UUID
from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.attendance.schemas import StudentUUIDs
from app.api.auth.models import User
from main import templates

from app.api.attendance.models import Attendance, Department, Student, Section, Year, Batch


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
    
    async def mark_attendance(self, student_uuids, section_id):
        """
        Mark attendance for a list of specified students (using their UUIDs).
        Mark all other students in the section as absent.
        Ensures attendance is marked only once per day for each student.
        """
        # 🔹 Ensure the faculty is assigned to a section
        if not section_id:
            raise HTTPException(status_code=403, detail="Access Denied: No section assigned.")
        
        # 🔹 Access the list of student UUIDs from the StudentUUIDs object
        if isinstance(student_uuids, StudentUUIDs):
            student_uuids = student_uuids.student_uuids  # Access the list attribute directly

        # 🔹 Check if student_uuids are already UUID objects, if not, convert them
        if isinstance(student_uuids[0], str):  # Check if the list contains strings
            student_uuids = [UUID(uuid) for uuid in student_uuids]
        
        # 🔹 Fetch students in the faculty's section and filter by section_id
        query = select(Student).where(Student.section_id == section_id)
        result = await self.db.execute(query)
        students = result.scalars().all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found in the section.")

        # 🔹 Get today's date (in UTC) to check against existing attendance
        today_date = datetime.utcnow().date()
        print(today_date)

        # 🔹 Check if attendance has already been marked for any student in the section today
        attendance_check_query = select(Attendance).where(
            Attendance.date == today_date,
            Attendance.student_id.in_([student.id for student in students])
        )
        attendance_check_result = await self.db.execute(attendance_check_query)
        existing_attendance_records = attendance_check_result.scalars().all()

        if existing_attendance_records:
            raise HTTPException(status_code=400, detail="Attendance has already been marked for today.")

        # 🔹 Create attendance records
        attendance_records = []
        # Set of student UUIDs passed by the frontend
        student_uuid_set = set(student_uuids)

        for student in students:
            # 🔹 If student UUID is in the list, mark as present, else absent
            status = "present" if student.id in student_uuid_set else "absent"
            
            # 🔹 Create a new attendance record
            attendance = Attendance(
                student_id=student.id,
                date=datetime.utcnow(),  # Store the exact time of marking
                status=status
            )
            self.db.add(attendance)
            attendance_records.append(attendance)

        # 🔹 Commit attendance records only if they were added
        if attendance_records:
            await self.db.commit()

        # 🔹 Return a response indicating how many attendance records were added
        return {"message": "Attendance marked successfully", "total": len(attendance_records)}


    async def download_attendance(self, section_id):
        """
        Fetch attendance records for all students in the section.
        """
        # 🔹 Ensure the faculty is assigned to a section
        if not section_id:
            raise HTTPException(status_code=403, detail="Access Denied: No section assigned.")
        
        # 🔹 Fetch students in the faculty's section
        query = select(Student).where(Student.section_id == section_id)
        result = await self.db.execute(query)
        students = result.scalars().all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found in the section.")

        # 🔹 Get today's date (in UTC) to check against existing attendance
        today_date = datetime.utcnow().date()

        # 🔹 Fetch attendance records for the students in the section
        attendance_query = select(Attendance).where(
            Attendance.date == today_date,
            Attendance.student_id.in_([student.id for student in students])
        )
        attendance_result = await self.db.execute(attendance_query)
        attendance_records = attendance_result.scalars().all()

        return attendance_records

    async def create_department(self, department_data):

        new_department = Department(name=department_data.name)
        self.db.add(new_department)
        await self.db.commit()
        return new_department


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

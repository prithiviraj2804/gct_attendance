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

from app.api.attendance.models import Attendance, Department, Student, Section, Timetable, Year, Batch


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
    
    # Use async session and async functions
    async def mark_attendance_for_day(self, section_id , data):
        """
        Function to mark attendance for all students in a section for a particular day.
        It marks attendance for each hour based on the timetable for the section.

        Args:
        - session (AsyncSession): The async database session.
        - section_id (uuid.UUID): The ID of the section for which we need to mark attendance.
        - data (dict): The data for marking attendance. Expects `day_of_week` and `date`.
        """
        # Fetch timetable for the given day of the week
        hour = data["hour"]
        if hour < 1 or hour > 7:
            raise Exception("Invalid hour. It should be between 1 and 7.")

        result = await self.db.execute(
            select(Timetable).filter(
                Timetable.section_id == section_id, 
                Timetable.day_of_week == data["day_of_week"]
            )
        )
        timetables_for_day = result.scalars().all()

        # Ensure that timetables are found for the provided section and day
        if not timetables_for_day:
            raise Exception("No timetable found for the given section and day of the week.")

        
        # Get all students in the section
        result = await self.db.execute(
            select(Student).filter(Student.section_id == section_id)
        )
        students = result.scalars().all()

        # Check if there are any students in the section
        if not students:
            raise Exception(f"No students found for section {section_id}.")


        for student in students:
                    for timetable in timetables_for_day:
                        # Check if there is a subject assigned for the specified hour
                        subject = getattr(timetable, f'hour_{hour}_subject', None)

                        if subject:
                            # Mark attendance for the student for that hour
                            attendance = Attendance(
                                student_id=student.id,
                                timetable_id=timetable.id,
                                hour=hour,
                                status="Present",  # Default status, can be modified if needed
                                date=data["date"]
                            )
                            self.db.add(attendance)

                # Commit the transaction to save all attendance records
        await self.db.commit()

        return {"message": f"Attendance successfully marked for section {section_id} on {data['date']} for hour {hour}"}    
    
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
    
    async def create_timetable(self, timetable_data):
        new_timetable = Timetable(
            day_of_week=timetable_data.day_of_week,
            hour_1_subject=timetable_data.hour_1_subject,
            hour_2_subject=timetable_data.hour_2_subject,
            hour_3_subject=timetable_data.hour_3_subject,
            hour_4_subject=timetable_data.hour_4_subject,
            hour_5_subject=timetable_data.hour_5_subject,
            hour_6_subject=timetable_data.hour_6_subject,
            hour_7_subject=timetable_data.hour_7_subject,
            hour_8_subject=timetable_data.hour_8_subject,
            section_id=timetable_data.section_id
        )
        self.db.add(new_timetable)
        await self.db.commit()
        return new_timetable

    async def get_timetable(self, timetable_id):
        query = select(Timetable).where(Timetable.id == timetable_id)
        result = await self.db.execute(query)
        timetable = result.scalars().first()
        if not timetable:
            raise HTTPException(status_code=404, detail="Timetable not found.")
        return timetable

    async def update_timetable(self, timetable_data, timetable_id):
        query = await self.db.execute(select(Timetable).where(Timetable.id == timetable_id))
        timetable = query.scalars().first()
        if not timetable:
            raise HTTPException(status_code=404, detail="Timetable not found.")

        update_fields = {
            "day_of_week": timetable_data.day_of_week,
            "hour_1_subject": timetable_data.hour_1_subject,
            "hour_2_subject": timetable_data.hour_2_subject,
            "hour_3_subject": timetable_data.hour_3_subject,
            "hour_4_subject": timetable_data.hour_4_subject,
            "hour_5_subject": timetable_data.hour_5_subject,
            "hour_6_subject": timetable_data.hour_6_subject,
            "hour_7_subject": timetable_data.hour_7_subject,
            "hour_8_subject": timetable_data.hour_8_subject,
            "section_id": timetable_data.section_id
        }

        await self.db.execute(
            Timetable.__table__.update().where(Timetable.id == timetable_id).values(update_fields)
        )
        await self.db.commit()
        return {"message": "Timetable updated successfully"}

    async def delete_timetable(self, timetable_id):
        query = await self.db.execute(select(Timetable).where(Timetable.id == timetable_id))
        timetable = query.scalars().first()
        if not timetable:
            raise HTTPException(status_code=404, detail="Timetable not found.")
        await self.db.delete(timetable)
        await self.db.commit()
        return {"message": "Timetable deleted successfully"}

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

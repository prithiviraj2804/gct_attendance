import io
import time
from datetime import datetime
from email import message
from typing import List
from uuid import UUID

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.attendance.models import (Attendance, Batch, Department, Section,
                                       Student, Timetable, TimetableSlot, Year)
from app.api.attendance.schemas import StudentUUIDs
from app.api.auth.models import User
from main import templates

'''
===================================================
# Student Services
===================================================
'''


class StudentService:
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
            raise HTTPException(
                status_code=400, detail=f"Invalid file format. Required columns: {required_columns}")
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
            raise HTTPException(
                status_code=403, detail="Access Denied: No section assigned.")

        # 🔹 Fetch students in the faculty's section along with section name, year, and department
        query = (
            select(
                Student,
                Section.name.label("section_name"),
                Year.name.label("year_name"),
                Department.name.label("department_name")
            )
            .join(Section, Student.section_id == Section.id)
            .join(Year, Section.year_id == Year.id)
            .join(Batch, Year.batch_id == Batch.id)
            .join(Department, Batch.department_id == Department.id)
            .where(Student.section_id == user.section_id)
        )

        result = await self.db.execute(query)

        # Format the response to include section name, year, and department
        formatted_students = [
            {
                "id": student.id,
                "name": student.name,
                "section_id": student.section_id,
                "section_name": section_name,
                "year_name": year_name,
                "department_name": department_name,
            }
            for student, section_name, year_name, department_name in result
        ]

        return formatted_students

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

    async def create_student(self, student_data, section_id):
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
===================================================
# Attendance Services
===================================================
'''


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def mark_attendance(self, attendance_data):
        section_id = attendance_data.section_id

        # Validate the section
        query = select(Section).where(Section.id == section_id)
        result = await self.db.execute(query)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        for record in attendance_data.records:
            day_of_week = record.day_of_week
            hour = record.hour
            students = record.students

            # Check for existing attendance for the given section, date, day, and hour
            query = select(Attendance).where(
                Attendance.section_id == section_id,
                Attendance.date == attendance_data.date,
                Attendance.day_of_week == day_of_week,
                Attendance.hour == hour
            )
            result = await self.db.execute(query)
            existing_attendance = result.scalars().first()

            if existing_attendance:
                # Update existing attendance record
                existing_data = existing_attendance.attendance_data

                # Merge existing data with new data
                for student_id, is_present in students.items():
                    existing_data[str(student_id)] = is_present

                # Update the record in the database
                existing_attendance.attendance_data = existing_data
                await self.db.commit()

            else:
                # Create a new attendance record if not exists
                new_attendance = Attendance(
                    section_id=section_id,
                    date=attendance_data.date,
                    day_of_week=day_of_week,
                    hour=hour,
                    attendance_data=students
                )
                self.db.add(new_attendance)
                await self.db.commit()

        return {"message": "Attendance marked successfully"}

    async def get_section_attendance(self, section_id):
        if not section_id:
            raise HTTPException(status_code=404,
                                detail="Section Not Found")
        query = await self.db.execute(select(Attendance).where(Attendance.section_id == section_id).filter(Attendance.is_present == True))
        result = query.scalars().all()
        return result

    async def get_attendance_by_subject(self, timetable_slot_id):
        if not timetable_slot_id:
            raise HTTPException(status_code=404,
                                detail="Subject Not Found")
        query = await self.db.execute(select(Attendance).where(Attendance.timetable_slot_id == timetable_slot_id))
        result = query.scalars().all()
        return result


'''
===================================================
# Admin Services
===================================================
'''


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(self, department_data):

        new_department = Department(name=department_data.name)
        self.db.add(new_department)
        await self.db.commit()
        return new_department

    async def get_departments(self):
        query = select(Department)
        result = await self.db.execute(query)
        departments = result.scalars().all()
        return departments
    
    async def get_department(self, department_id):
        query = select(Department).where(Department.id == department_id)
        result = await self.db.execute(query)
        department = result.scalars().first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found.")
        return department
    
    async def update_department(self, department_data, department_id):
        # Fetch the department from the database
        query = await self.db.execute(select(Department).where(Department.id == department_id))
        department = query.scalars().first()
        if not department:
            raise HTTPException(
                detail="Department Not Found",
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if department_data.name is not None:
            update_fields["name"] = department_data.name

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                Department.__table__.update().where(Department.id == department_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "Department record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )
    
    async def delete_department(self, department_id):
        result = await self.db.execute(select(Department).where(Department.id == department_id))
        department = result.scalars().first()
        if not department:
            raise HTTPException(
                detail="Department Not Found",
                status_code=404
            )
        await self.db.delete(department)
        await self.db.commit()
        return {"message": "Department record deleted successfully"}

    # 🔹 Create Batch (Only Admins)

    async def create_batch(self, batch_data):

        new_batch = Batch(name=batch_data.name,
                          department_id=batch_data.department_id)
        self.db.add(new_batch)
        await self.db.commit()
        return new_batch

    async def get_batches(self):
        query = select(Batch)
        result = await self.db.execute(query)
        batches = result.scalars().all()
        return batches

    async def get_batch(self, batch_id):
        query = select(Batch).where(Batch.id == batch_id)
        result = await self.db.execute(query)
        batch = result.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found.")
        return batch
    
    async def update_batch(self, batch_data, batch_id):
        # Fetch the batch from the database
        query = await self.db.execute(select(Batch).where(Batch.id == batch_id))
        batch = query.scalars().first()
        if not batch:
            raise HTTPException(
                detail="Batch Not Found",
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if batch_data.name is not None:
            update_fields["name"] = batch_data.name

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                Batch.__table__.update().where(Batch.id == batch_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "Batch record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )

    async def delete_batch(self, batch_id):
        result = await self.db.execute(select(Batch).where(Batch.id == batch_id))
        batch = result.scalars().first()
        if not batch:
            raise HTTPException(
                detail="Batch Not Found",
                status_code=404
            )
        await self.db.delete(batch)
        await self.db.commit()
        return {"message": "Batch record deleted successfully"}

    # 🔹 Create Year (Only Admins)


    async def create_year(self,  year_data):

        new_year = Year(name=year_data.name, batch_id=year_data.batch_id)
        self.db.add(new_year)
        await self.db.commit()
        return new_year

    async def get_years(self):
        query = select(Year)
        result = await self.db.execute(query)
        years = result.scalars().all()
        return years

    async def get_year(self, year_id):
        query = select(Year).where(Year.id == year_id)
        result = await self.db.execute(query)
        year = result.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found.")
        return year

    async def update_year(self, year_data, year_id):
        # Fetch the year from the database
        query = await self.db.execute(select(Year).where(Year.id == year_id))
        year = query.scalars().first()
        if not year:
            raise HTTPException(
                detail="Year Not Found",
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if year_data.name is not None:
            update_fields["name"] = year_data.name

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                Year.__table__.update().where(Year.id == year_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "Year record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )

    
    async def delete_year(self, year_id):
        result = await self.db.execute(select(Year).where(Year.id == year_id))
        year = result.scalars().first()
        if not year:
            raise HTTPException(
                detail="Year Not Found",
                status_code=404
            )
        await self.db.delete(year)
        await self.db.commit()
        return {"message": "Year record deleted successfully"}
    # 🔹 Create Section (Only Admins)

    async def create_section(self,  section_data):

        new_section = Section(name=section_data.name,
                              year_id=section_data.year_id)
        self.db.add(new_section)
        await self.db.commit()
        return new_section

    async def get_sections(self):
        query = select(Section)
        result = await self.db.execute(query)
        sections = result.scalars().all()
        return sections
    
    async def get_section(self, section_id):
        query = select(Section).where(Section.id == section_id)
        result = await self.db.execute(query)
        section = result.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found.")
        return section

    async def update_section(self, section_data, section_id):
        # Fetch the section from the database
        query = await self.db.execute(select(Section).where(Section.id == section_id))
        section = query.scalars().first()
        if not section:
            raise HTTPException(
                detail="Section Not Found",
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if section_data.name is not None:
            update_fields["name"] = section_data.name

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                Section.__table__.update().where(Section.id == section_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "Section record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )
    
    async def delete_section(self, section_id):
        result = await self.db.execute(select(Section).where(Section.id == section_id))
        section = result.scalars().first()
        if not section:
            raise HTTPException(
                detail="Section Not Found",
                status_code=404
            )
        await self.db.delete(section)
        await self.db.commit()
        return {"message": "Section record deleted successfully"}

    async def assign_timetable(self, section_id, slots):
        # Create a new timetable for the section
        timetable = Timetable(section_id=section_id)
        self.db.add(timetable)
        await self.db.commit()
        await self.db.refresh(timetable)

        # Group timetable data by day
        day_wise_schedule = {}
        for slot in slots:
            day = slot.day_of_week
            schedule = slot.schedule  # Extract the entire schedule dictionary

            # Initialize the day if not already present
            if day not in day_wise_schedule:
                day_wise_schedule[day] = {}

            # Iterate over the schedule dictionary to get hours and subjects
            for hour, subject_details in schedule.items():
                subject_name = subject_details.get("subject_name")
                subject_code = subject_details.get("subject_code")

                # Add the slot to the day's schedule
                day_wise_schedule[day][hour] = {
                    "subject_name": subject_name,
                    "subject_code": subject_code,
                }

        # Create timetable slots with compressed day-wise data
        for day, schedule in day_wise_schedule.items():
            timetable_slot = TimetableSlot(
                timetable_id=timetable.id,
                day_of_week=day,
                schedule=schedule  # Store the entire day schedule as a JSON object
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

        query = select(TimetableSlot).where(
            TimetableSlot.timetable_id == timetable.id)
        result = await self.db.execute(query)
        slots = result.scalars().all()

        return slots

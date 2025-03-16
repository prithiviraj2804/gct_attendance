from datetime import datetime
import io
from typing import List
from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth.models import User
from main import templates

from app.api.attendance.models import Attendance, Department, Student, Section, Year, Batch


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, data, file):
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
            raise HTTPException(
                status_code=400, detail="Excel file must contain 'name' column")

        # Fetch the batch, year, and section
        batch = await self.db.execute(select(Batch).filter(Batch.name == data.batch_name))
        batch = batch.scalars().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        year = await self.db.execute(select(Year).filter(Year.name == data.year_name, Year.batch_id == batch.id))
        year = year.scalars().first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        section = await self.db.execute(select(Section).filter(Section.name == data.section_name, Section.year_id == year.id))
        section = section.scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")

        # Iterate over the rows in the DataFrame and insert students into the database
        for _, row in df.iterrows():
            student = Student(name=row["name"], section_id=section.id)
            self.db.add(student)

        # Commit the changes to the database
        await self.db.commit()

        return {"message": f"Successfully uploaded {len(df)} students to {section.name}!"}

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

    # 🔹 Create Department (Only Admins)


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

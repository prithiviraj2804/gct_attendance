import uuid
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.attendance.models import (Attendance, Batch, Department, Section,
                                       Student, Subject, Timetable, Year,
                                       YearSubject)
from core.database import get_session

# Step 1: Create Department
department = Department(name="Computer Science")
get_session.add(department)

# Step 2: Create Batch
batch = Batch(name="Batch A", department_id=department.id)
get_session.add(batch)

# Step 3: Create Year
year = Year(name="First Year", batch_id=batch.id)
get_session.add(year)

# Step 4: Create Section
section = Section(name="Section 1", year_id=year.id)
get_session.add(section)

# Step 5: Create Subjects
subject_math = Subject(name="Mathematics")
subject_cs = Subject(name="Computer Science")
subject_eng = Subject(name="English")
get_session.add(subject_math)
get_session.add(subject_cs)
get_session.add(subject_eng)

# Step 6: Assign Subjects to Year
year_subject_1 = YearSubject(year_id=year.id, subject_id=subject_math.id)
year_subject_2 = YearSubject(year_id=year.id, subject_id=subject_cs.id)
year_subject_3 = YearSubject(year_id=year.id, subject_id=subject_eng.id)
get_session.add(year_subject_1)
get_session.add(year_subject_2)
get_session.add(year_subject_3)

# Step 7: Create Timetable for Section
timetable = Timetable(
    day_of_week="Monday",
    section_id=section.id,
    hour_1_subject_id=subject_math.id,
    hour_2_subject_id=subject_cs.id,
    hour_3_subject_id=subject_eng.id,
    hour_4_subject_id=subject_math.id,
    hour_5_subject_id=subject_cs.id,
    hour_6_subject_id=subject_eng.id,
    hour_7_subject_id=subject_math.id,
    hour_8_subject_id=subject_cs.id
)
get_session.add(timetable)

# Step 8: Create Students
student_1 = Student(name="John Doe", section_id=section.id)
student_2 = Student(name="Jane Doe", section_id=section.id)
get_session.add(student_1)
get_session.add(student_2)

# Step 9: Create Attendance Entries for Students
attendance_1 = Attendance(student_id=student_1.id, timetable_id=timetable.id, hour=1, status="Present", date=str(datetime.today().date()))
attendance_2 = Attendance(student_id=student_1.id, timetable_id=timetable.id, hour=2, status="Absent", date=str(datetime.today().date()))
attendance_3 = Attendance(student_id=student_2.id, timetable_id=timetable.id, hour=1, status="Present", date=str(datetime.today().date()))
attendance_4 = Attendance(student_id=student_2.id, timetable_id=timetable.id, hour=2, status="Present", date=str(datetime.today().date()))
get_session.add(attendance_1)
get_session.add(attendance_2)
get_session.add(attendance_3)
get_session.add(attendance_4)

# Commit all data to the database
get_session.commit()

# Optionally print out the created records for confirmation
print("Department:", department.name)
print("Batch:", batch.name)
print("Year:", year.name)
print("Section:", section.name)
print("Subjects:", [subject.name for subject in [subject_math, subject_cs, subject_eng]])
print(f"Timetable for {timetable.day_of_week}:")
for hour in range(1, 9):
    subject_name = getattr(timetable, f"hour_{hour}_subject").name
    print(f"  Hour {hour}: {subject_name}")
print("Students:", [student.name for student in [student_1, student_2]])
print("Attendance Entries:")
for attendance in [attendance_1, attendance_2, attendance_3, attendance_4]:
    student_name = get_session.query(Student).get(attendance.student_id).name
    subject_name = getattr(timetable, f"hour_{attendance.hour}_subject").name
    print(f"  {student_name} - Hour {attendance.hour}: {subject_name} - {attendance.status}")

# Close the get_session
get_session.close()
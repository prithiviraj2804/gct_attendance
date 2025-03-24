from datetime import datetime
from app.api.attendance.models import (Attendance, Batch, Department, Section,
                                       Student, Subject, Timetable, Year,
                                       YearSubject)
from app.core.database import get_session

# Step 1: Create Department
def create_department(db):
    department = Department(name="Computer Science")
    db.add(department)
    db.commit()
    return department

# Step 2: Create Batch
def create_batch(db, department):
    batch = Batch(name="Batch A", department_id=department.id)
    db.add(batch)
    db.commit()
    return batch

# Step 3: Create Year
def create_year(db, batch):
    year = Year(name="First Year", batch_id=batch.id)
    db.add(year)
    db.commit()
    return year

# Step 4: Create Section
def create_section(db, year):
    section = Section(name="Section 1", year_id=year.id)
    db.add(section)
    db.commit()
    return section

# Step 5: Create Subjects
def create_subjects(db):
    subject_math = Subject(name="Mathematics")
    subject_cs = Subject(name="Computer Science")
    subject_eng = Subject(name="English")
    db.add(subject_math)
    db.add(subject_cs)
    db.add(subject_eng)
    db.commit()
    return subject_math, subject_cs, subject_eng

# Step 6: Assign Subjects to Year
def assign_subjects_to_year(db, year, subjects):
    year_subject_1 = YearSubject(year_id=year.id, subject_id=subjects[0].id)
    year_subject_2 = YearSubject(year_id=year.id, subject_id=subjects[1].id)
    year_subject_3 = YearSubject(year_id=year.id, subject_id=subjects[2].id)
    db.add(year_subject_1)
    db.add(year_subject_2)
    db.add(year_subject_3)
    db.commit()

# Step 7: Create Timetable for Section
def create_timetable(db, section, subjects):
    timetable = Timetable(
        day_of_week="Monday",
        section_id=section.id,
        hour_1_subject_id=subjects[0].id,
        hour_2_subject_id=subjects[1].id,
        hour_3_subject_id=subjects[2].id,
        hour_4_subject_id=subjects[0].id,
        hour_5_subject_id=subjects[1].id,
        hour_6_subject_id=subjects[2].id,
        hour_7_subject_id=subjects[0].id,
        hour_8_subject_id=subjects[1].id
    )
    db.add(timetable)
    db.commit()
    return timetable

# Step 8: Create Students
def create_students(db, section):
    student_1 = Student(name="John Doe", section_id=section.id)
    student_2 = Student(name="Jane Doe", section_id=section.id)
    db.add(student_1)
    db.add(student_2)
    db.commit()
    return student_1, student_2

# Step 9: Create Attendance Entries for Students
def create_attendance(db, timetable, students):
    attendance_1 = Attendance(student_id=students[0].id, timetable_id=timetable.id, hour=1, status="Present", date=str(datetime.today().date()))
    attendance_2 = Attendance(student_id=students[0].id, timetable_id=timetable.id, hour=2, status="Absent", date=str(datetime.today().date()))
    attendance_3 = Attendance(student_id=students[1].id, timetable_id=timetable.id, hour=1, status="Present", date=str(datetime.today().date()))
    attendance_4 = Attendance(student_id=students[1].id, timetable_id=timetable.id, hour=2, status="Present", date=str(datetime.today().date()))
    db.add(attendance_1)
    db.add(attendance_2)
    db.add(attendance_3)
    db.add(attendance_4)
    db.commit()

# Main function to call all steps
def main():
    # Step 1: Start session
    db = next(get_session())
    
    # Create Department
    department = create_department(db)
    
    # Create Batch
    batch = create_batch(db, department)
    
    # Create Year
    year = create_year(db, batch)
    
    # Create Section
    section = create_section(db, year)
    
    # Create Subjects
    subjects = create_subjects(db)
    
    # Assign Subjects to Year
    assign_subjects_to_year(db, year, subjects)
    
    # Create Timetable
    timetable = create_timetable(db, section, subjects)
    
    # Create Students
    students = create_students(db, section)
    
    # Create Attendance Entries
    create_attendance(db, timetable, students)
    
    # Optionally print out the created records for confirmation
    print("Department:", department.name)
    print("Batch:", batch.name)
    print("Year:", year.name)
    print("Section:", section.name)
    print("Subjects:", [subject.name for subject in subjects])
    print(f"Timetable for {timetable.day_of_week}:")
    for hour in range(1, 9):
        subject_name = getattr(timetable, f"hour_{hour}_subject").name
        print(f"  Hour {hour}: {subject_name}")
    print("Students:", [student.name for student in students])
    print("Attendance Entries:")
    for attendance in db.query(Attendance).all():
        student_name = db.query(Student).get(attendance.student_id).name
        subject_name = getattr(timetable, f"hour_{attendance.hour}_subject").name
        print(f"  {student_name} - Hour {attendance.hour}: {subject_name} - {attendance.status}")
    
    db.close()

if __name__ == "__main__":
    main()
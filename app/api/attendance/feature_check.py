
async def mark_attendance(self, user, attendance_data):
    """
    Mark attendance for all students in the faculty's section.
    """
    # 🔹 Only faculty can mark attendance
    if user.role.name != "faculty":
        raise HTTPException(status_code=403, detail="Access Denied: Only faculty can mark attendance.")

    # 🔹 Ensure the faculty is assigned to a section
    if not user.section_id:
        raise HTTPException(status_code=400, detail="You are not assigned to any section.")

    # 🔹 Fetch all students in the faculty's section
    query = select(Student).where(Student.section_id == user.section_id)
    result = await self.db.execute(query)
    students = result.scalars().all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found in your section.")

    student_ids = {student.id for student in students}  # Convert to set for quick lookup

    # 🔹 Prepare attendance records
    attendance_records = []
    for entry in attendance_data:
        student_id = entry.get("student_id")
        status = entry.get("status", "Absent")  # Default to "Absent"
        today = date.today()

        # 🔹 Ensure the student belongs to the faculty's section
        if student_id not in student_ids:
            raise HTTPException(status_code=403, detail=f"Access Denied: You cannot mark attendance for student {student_id}.")

        # 🔹 Check if attendance for this student has already been marked today
        query = select(Attendance).where(Attendance.student_id == student_id, Attendance.date == today)
        result = await self.db.execute(query)
        existing_attendance = result.scalars().first()

        if existing_attendance:
            raise HTTPException(status_code=400, detail=f"Attendance already marked for student {student_id} today.")

        # 🔹 Create attendance record
        attendance = Attendance(
            student_id=student_id,
            date=today,
            status=status
        )
        self.db.add(attendance)
        attendance_records.append(attendance)

    await self.db.commit()
    return {"message": f"Attendance marked successfully for {len(attendance_records)} students"}
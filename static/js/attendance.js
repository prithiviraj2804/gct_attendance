document.addEventListener("DOMContentLoaded", () => {
    // Check if attendance page is in the DOM
    const attendancePage = document.getElementById("attendance")
    if (!attendancePage) return
  
    // DOM Elements
    const markAttendanceBtn = document.getElementById("markAttendanceBtn")
    const batchAttendanceBtn = document.getElementById("batchAttendanceBtn")
    const attendanceDate = document.getElementById("attendanceDate")
    const loadAttendanceBtn = document.getElementById("loadAttendanceBtn")
    const attendanceTableBody = document.getElementById("attendanceTableBody")
    const batchAttendanceModal = document.getElementById("batchAttendanceModal")
    const closeBatchModal = document.getElementById("closeBatchModal")
    const cancelBatchBtn = document.getElementById("cancelBatchBtn")
    const batchAttendanceForm = document.getElementById("batchAttendanceForm")
    const batchDate = document.getElementById("batchDate")
    const batchDepartment = document.getElementById("batchDepartment")
    const batchYear = document.getElementById("batchYear")
    const batchStatus = document.getElementById("batchStatus")
  
    // Set default date to today
    const today = new Date()
    const formattedDate = today.toISOString().split("T")[0]
    attendanceDate.value = formattedDate
    batchDate.value = formattedDate
  
    // Load departments for batch attendance
    loadDepartments()
  
    // Check if we're viewing a specific student from the students page
    const viewStudentId = sessionStorage.getItem("viewStudentId")
    if (viewStudentId) {
      // We'll load attendance for this student
      loadStudentAttendance(viewStudentId)
      // Clear the session storage
      sessionStorage.removeItem("viewStudentId")
    } else {
      // Load attendance for today
      loadAttendanceForDate(formattedDate)
    }
  
    // Event Listeners
    markAttendanceBtn.addEventListener("click", () => {
      // This would typically open a modal or form to mark attendance
      // For simplicity, we'll just reload the current date's attendance
      loadAttendanceForDate(attendanceDate.value)
    })
  
    batchAttendanceBtn.addEventListener("click", () => {
      batchAttendanceModal.classList.add("active")
    })
  
    closeBatchModal.addEventListener("click", () => {
      batchAttendanceModal.classList.remove("active")
    })
  
    cancelBatchBtn.addEventListener("click", () => {
      batchAttendanceModal.classList.remove("active")
    })
  
    loadAttendanceBtn.addEventListener("click", () => {
      loadAttendanceForDate(attendanceDate.value)
    })
  
    batchAttendanceForm.addEventListener("submit", (e) => {
      e.preventDefault()
      saveBatchAttendance()
    })
  
    // Functions
    function loadDepartments() {
      const token = localStorage.getItem("authToken")
  
      fetch("/api/departments", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Populate department select in batch form
            batchDepartment.innerHTML = '<option value="">Select Department</option>'
            data.departments.forEach((dept) => {
              const option = document.createElement("option")
              option.value = dept.id
              option.textContent = dept.name
              batchDepartment.appendChild(option)
            })
          } else {
            console.error("Failed to load departments:", data.message)
          }
        })
        .catch((error) => {
          console.error("Error loading departments:", error)
        })
    }
  
    function loadAttendanceForDate(date) {
      const token = localStorage.getItem("authToken")
      attendanceTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">Loading attendance data...</td></tr>'
  
      fetch(`/api/attendance?date=${date}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            renderAttendanceTable(data.attendance)
          } else {
            console.error("Failed to load attendance:", data.message)
            attendanceTableBody.innerHTML =
              '<tr><td colspan="6" class="loading-text">Failed to load attendance data</td></tr>'
          }
        })
        .catch((error) => {
          console.error("Error loading attendance:", error)
          attendanceTableBody.innerHTML =
            '<tr><td colspan="6" class="loading-text">Error loading attendance data</td></tr>'
        })
    }
  
    function loadStudentAttendance(studentId) {
      const token = localStorage.getItem("authToken")
      attendanceTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">Loading student attendance...</td></tr>'
  
      fetch(`/api/attendance/student/${studentId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            renderAttendanceTable(data.attendance)
          } else {
            console.error("Failed to load student attendance:", data.message)
            attendanceTableBody.innerHTML =
              '<tr><td colspan="6" class="loading-text">Failed to load student attendance</td></tr>'
          }
        })
        .catch((error) => {
          console.error("Error loading student attendance:", error)
          attendanceTableBody.innerHTML =
            '<tr><td colspan="6" class="loading-text">Error loading student attendance</td></tr>'
        })
    }
  
    function renderAttendanceTable(attendanceData) {
      if (attendanceData.length === 0) {
        attendanceTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">No attendance records found</td></tr>'
        return
      }
  
      attendanceTableBody.innerHTML = ""
  
      attendanceData.forEach((record) => {
        const tr = document.createElement("tr")
  
        tr.innerHTML = `
                  <td>${record.student.rollNo}</td>
                  <td>${record.student.name}</td>
                  <td>${record.student.department}</td>
                  <td>
                      <span class="status-badge ${record.status === "present" ? "present" : "absent"}">
                          ${record.status === "present" ? "Present" : "Absent"}
                      </span>
                  </td>
                  <td>${formatTime(record.timestamp)}</td>
                  <td>
                      <div class="table-actions">
                          <button class="edit-action" data-id="${record.id}" title="Change Status">
                              <i class="fas fa-exchange-alt"></i>
                          </button>
                      </div>
                  </td>
              `
  
        // Add event listener to toggle status
        tr.querySelector(".edit-action").addEventListener("click", function () {
          const recordId = this.getAttribute("data-id")
          toggleAttendanceStatus(recordId)
        })
  
        attendanceTableBody.appendChild(tr)
      })
  
      // Add some CSS for status badges
      if (!document.getElementById("status-badge-styles")) {
        const style = document.createElement("style")
        style.id = "status-badge-styles"
        style.textContent = `
                  .status-badge {
                      padding: 4px 8px;
                      border-radius: 4px;
                      font-size: 0.8rem;
                      font-weight: 500;
                  }
                  .status-badge.present {
                      background-color: rgba(46, 204, 113, 0.2);
                      color: #27ae60;
                  }
                  .status-badge.absent {
                      background-color: rgba(231, 76, 60, 0.2);
                      color: #c0392b;
                  }
              `
        document.head.appendChild(style)
      }
    }
  
    function toggleAttendanceStatus(recordId) {
      const token = localStorage.getItem("authToken")
  
      fetch(`/api/attendance/${recordId}/toggle`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Reload attendance for the current date
            loadAttendanceForDate(attendanceDate.value)
          } else {
            alert(data.message || "Failed to update attendance status")
          }
        })
        .catch((error) => {
          console.error("Error updating attendance status:", error)
          alert("An error occurred. Please try again.")
        })
    }
  
    function saveBatchAttendance() {
      const token = localStorage.getItem("authToken")
      const date = batchDate.value
      const departmentId = batchDepartment.value
      const year = batchYear.value
      const status = batchStatus.value
  
      if (!date || !departmentId || !year || !status) {
        alert("Please fill in all required fields")
        return
      }
  
      const batchData = {
        date,
        departmentId,
        year: Number.parseInt(year),
        status,
      }
  
      fetch("/api/attendance/batch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(batchData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            batchAttendanceModal.classList.remove("active")
            // Update the date input to match the batch date
            attendanceDate.value = date
            // Load attendance for the batch date
            loadAttendanceForDate(date)
          } else {
            alert(data.message || "Failed to save batch attendance")
          }
        })
        .catch((error) => {
          console.error("Error saving batch attendance:", error)
          alert("An error occurred. Please try again.")
        })
    }
  
    function formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      })
    }
  })
  
  
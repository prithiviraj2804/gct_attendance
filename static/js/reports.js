import { Chart } from "@/components/ui/chart"
document.addEventListener("DOMContentLoaded", () => {
  // Check if reports page is in the DOM
  const reportsPage = document.getElementById("reports")
  if (!reportsPage) return

  // DOM Elements
  const reportType = document.getElementById("reportType")
  const singleDateFilter = document.getElementById("singleDateFilter")
  const dateRangeFilter = document.getElementById("dateRangeFilter")
  const reportDate = document.getElementById("reportDate")
  const startDate = document.getElementById("startDate")
  const endDate = document.getElementById("endDate")
  const reportDepartment = document.getElementById("reportDepartment")
  const generateReportBtn = document.getElementById("generateReportBtn")
  const exportReportBtn = document.getElementById("exportReportBtn")
  const reportTotalStudents = document.getElementById("reportTotalStudents")
  const reportPresent = document.getElementById("reportPresent")
  const reportAbsent = document.getElementById("reportAbsent")
  const reportAttendanceRate = document.getElementById("reportAttendanceRate")
  const reportTableBody = document.getElementById("reportTableBody")
  const attendanceChart = document.getElementById("attendanceChart")

  // Set default dates
  const today = new Date()
  const formattedDate = today.toISOString().split("T")[0]
  reportDate.value = formattedDate
  endDate.value = formattedDate

  // Set start date to 7 days ago for weekly report
  const weekAgo = new Date()
  weekAgo.setDate(today.getDate() - 7)
  startDate.value = weekAgo.toISOString().split("T")[0]

  // Load departments for report filter
  loadDepartments()

  // Initialize chart
  let attendanceChartInstance = null

  // Event Listeners
  reportType.addEventListener("change", () => {
    toggleDateFilters()
  })

  generateReportBtn.addEventListener("click", () => {
    generateReport()
  })

  exportReportBtn.addEventListener("click", () => {
    exportReport()
  })

  // Initial setup
  toggleDateFilters()

  // Functions
  function toggleDateFilters() {
    const selectedType = reportType.value

    if (selectedType === "daily") {
      singleDateFilter.classList.remove("hidden")
      dateRangeFilter.classList.add("hidden")
    } else {
      singleDateFilter.classList.add("hidden")
      dateRangeFilter.classList.remove("hidden")

      // Set appropriate date ranges based on report type
      const today = new Date()
      const endFormatted = today.toISOString().split("T")[0]
      endDate.value = endFormatted

      if (selectedType === "weekly") {
        const weekAgo = new Date()
        weekAgo.setDate(today.getDate() - 7)
        startDate.value = weekAgo.toISOString().split("T")[0]
      } else if (selectedType === "monthly") {
        const monthAgo = new Date()
        monthAgo.setMonth(today.getMonth() - 1)
        startDate.value = monthAgo.toISOString().split("T")[0]
      }
    }
  }

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
          // Populate department select in report filter
          reportDepartment.innerHTML = '<option value="">All Departments</option>'
          data.departments.forEach((dept) => {
            const option = document.createElement("option")
            option.value = dept.id
            option.textContent = dept.name
            reportDepartment.appendChild(option)
          })
        } else {
          console.error("Failed to load departments:", data.message)
        }
      })
      .catch((error) => {
        console.error("Error loading departments:", error)
      })
  }

  function generateReport() {
    const token = localStorage.getItem("authToken")
    const selectedType = reportType.value
    const departmentId = reportDepartment.value

    const params = new URLSearchParams()
    params.append("type", selectedType)
    if (departmentId) params.append("departmentId", departmentId)

    if (selectedType === "daily") {
      params.append("date", reportDate.value)
    } else {
      params.append("startDate", startDate.value)
      params.append("endDate", endDate.value)
    }

    reportTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">Generating report...</td></tr>'

    fetch(`/api/reports/attendance?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          renderReportData(data.report)
        } else {
          console.error("Failed to generate report:", data.message)
          reportTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">Failed to generate report</td></tr>'
          resetReportSummary()
        }
      })
      .catch((error) => {
        console.error("Error generating report:", error)
        reportTableBody.innerHTML = '<tr><td colspan="6" class="loading-text">Error generating report</td></tr>'
        resetReportSummary()
      })
  }

  function renderReportData(reportData) {
    // Update summary stats
    reportTotalStudents.textContent = reportData.totalStudents
    reportPresent.textContent = reportData.totalPresent
    reportAbsent.textContent = reportData.totalAbsent
    reportAttendanceRate.textContent = reportData.attendanceRate + "%"

    // Render table
    if (reportData.students.length === 0) {
      reportTableBody.innerHTML =
        '<tr><td colspan="6" class="loading-text">No data available for the selected criteria</td></tr>'
      return
    }

    reportTableBody.innerHTML = ""

    reportData.students.forEach((student) => {
      const tr = document.createElement("tr")

      tr.innerHTML = `
                <td>${student.rollNo}</td>
                <td>${student.name}</td>
                <td>${student.department}</td>
                <td>${student.presentDays}</td>
                <td>${student.absentDays}</td>
                <td>${student.attendancePercentage}%</td>
            `

      reportTableBody.appendChild(tr)
    })

    // Render chart
    renderAttendanceChart(reportData)
  }

  function renderAttendanceChart(reportData) {
    // Destroy previous chart if it exists
    if (attendanceChartInstance) {
      attendanceChartInstance.destroy()
    }

    // Prepare data for chart
    let labels, presentData, absentData

    if (reportType.value === "daily") {
      // For daily report, show department-wise breakdown
      labels = reportData.departmentStats.map((dept) => dept.name)
      presentData = reportData.departmentStats.map((dept) => dept.presentCount)
      absentData = reportData.departmentStats.map((dept) => dept.absentCount)
    } else {
      // For weekly/monthly/custom, show day-wise breakdown
      labels = reportData.dateStats.map((date) => formatDate(date.date))
      presentData = reportData.dateStats.map((date) => date.presentCount)
      absentData = reportData.dateStats.map((date) => date.absentCount)
    }

    // Create chart
    const ctx = attendanceChart.getContext("2d")
    attendanceChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Present",
            data: presentData,
            backgroundColor: "#2ecc71",
            borderColor: "#27ae60",
            borderWidth: 1,
          },
          {
            label: "Absent",
            data: absentData,
            backgroundColor: "#e74c3c",
            borderColor: "#c0392b",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Number of Students",
            },
          },
          x: {
            title: {
              display: true,
              text: reportType.value === "daily" ? "Departments" : "Dates",
            },
          },
        },
      },
    })
  }

  function resetReportSummary() {
    reportTotalStudents.textContent = "-"
    reportPresent.textContent = "-"
    reportAbsent.textContent = "-"
    reportAttendanceRate.textContent = "-"

    // Destroy chart if it exists
    if (attendanceChartInstance) {
      attendanceChartInstance.destroy()
      attendanceChartInstance = null
    }
  }

  function exportReport() {
    const token = localStorage.getItem("authToken")
    const selectedType = reportType.value
    const departmentId = reportDepartment.value

    const params = new URLSearchParams()
    params.append("type", selectedType)
    if (departmentId) params.append("departmentId", departmentId)

    if (selectedType === "daily") {
      params.append("date", reportDate.value)
    } else {
      params.append("startDate", startDate.value)
      params.append("endDate", endDate.value)
    }

    // Create a download link
    const downloadLink = document.createElement("a")
    downloadLink.href = `/api/reports/export?${params.toString()}`
    downloadLink.setAttribute("download", `attendance_report_${Date.now()}.csv`)
    downloadLink.setAttribute("target", "_blank")

    // Add auth token as a header (this is a simplified approach)
    // In a real app, you might need to handle this differently
    downloadLink.setAttribute("data-token", token)

    // Trigger download
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
  }

  function formatDate(dateString) {
    const options = { month: "short", day: "numeric" }
    return new Date(dateString).toLocaleDateString("en-US", options)
  }
})

// Compare this snippet from static/js/dashboard.js:
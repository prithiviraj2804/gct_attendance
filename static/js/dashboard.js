document.addEventListener("DOMContentLoaded", () => {
  // Check authentication
  const token = localStorage.getItem("authToken")
  if (!token) {
    window.location.href = "index.html"
    return
  }

  // DOM Elements
  const sidebar = document.querySelector(".sidebar")
  const menuToggle = document.getElementById("menuToggle")
  const navLinks = document.querySelectorAll(".nav-links li")
  const pages = document.querySelectorAll(".page")
  const pageTitle = document.getElementById("pageTitle")
  const logoutBtn = document.getElementById("logoutBtn")
  const currentUser = document.getElementById("currentUser")

  // Set current user
  const user = JSON.parse(localStorage.getItem("user"))
  if (user) {
    currentUser.textContent = user.username
  }

  // Toggle sidebar on mobile
  menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("active")
  })

  // Navigation
  navLinks.forEach((link) => {
    link.addEventListener("click", function () {
      const pageName = this.getAttribute("data-page")

      // Skip if it's the logout button
      if (!pageName) return

      // Update active link
      navLinks.forEach((item) => item.classList.remove("active"))
      this.classList.add("active")

      // Show active page
      pages.forEach((page) => {
        if (page.id === pageName) {
          page.classList.add("active")
          pageTitle.textContent = this.querySelector("span").textContent
        } else {
          page.classList.remove("active")
        }
      })

      // Close sidebar on mobile after navigation
      if (window.innerWidth <= 768) {
        sidebar.classList.remove("active")
      }
    })
  })

  // Logout functionality
  logoutBtn.addEventListener("click", () => {
    // Clear local storage
    localStorage.removeItem("authToken")
    localStorage.removeItem("user")

    // Redirect to login page
    window.location.href = "/static/index.html"
  })

  // Load dashboard data
  loadDashboardData()

  // Handle window resize
  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
      sidebar.classList.remove("active")
    }
  })
})

// Load dashboard overview data
function loadDashboardData() {
  const token = localStorage.getItem("authToken")
  const totalStudents = document.getElementById("totalStudents")
  const presentToday = document.getElementById("presentToday")
  const absentToday = document.getElementById("absentToday")
  const attendanceRate = document.getElementById("attendanceRate")
  const recentActivityList = document.getElementById("recentActivityList")

  // Fetch dashboard stats
  fetch("/api/students", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data && Array.isArray(data)) {
        console.log(data)
        totalStudents.textContent = data.length
        // Assuming stats are calculated separately
        const stats = {
          presentToday: 2, // Example value
          absentToday: 1,  // Example value
          attendanceRate: ((2 / data.length) * 100).toFixed(2), // Example calculation
        }
        presentToday.textContent = stats.presentToday
        absentToday.textContent = stats.absentToday
        attendanceRate.textContent = stats.attendanceRate + "%"
      } else {
        console.error("Failed to load dashboard stats:", data.message)
      }
    })
    .catch((error) => {
      console.error("Error loading dashboard stats:", error)
    })
  // Fetch recent activities
  fetch("/api/dashboard/activities", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.activities.length > 0) {
        recentActivityList.innerHTML = ""

        data.activities.forEach((activity) => {
          const activityItem = document.createElement("div")
          activityItem.className = "activity-item"

          let iconClass = "login"
          if (activity.type === "add") iconClass = "add"
          if (activity.type === "edit") iconClass = "edit"
          if (activity.type === "delete") iconClass = "delete"

          activityItem.innerHTML = `
                    <div class="activity-icon ${iconClass}">
                        <i class="fas fa-${
                          activity.type === "login"
                            ? "sign-in-alt"
                            : activity.type === "add"
                              ? "plus"
                              : activity.type === "edit"
                                ? "edit"
                                : "trash"
                        }"></i>
                    </div>
                    <div class="activity-details">
                        <h4>${activity.description}</h4>
                        <p>${formatDate(activity.timestamp)}</p>
                    </div>
                `

          recentActivityList.appendChild(activityItem)
        })
      } else {
        recentActivityList.innerHTML = '<p class="loading-text">No recent activities</p>'
      }
    })
    .catch((error) => {
      console.error("Error loading recent activities:", error)
      recentActivityList.innerHTML = '<p class="loading-text">Failed to load activities</p>'
    })
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) {
    return "Just now"
  } else if (diffMin < 60) {
    return `${diffMin} minute${diffMin > 1 ? "s" : ""} ago`
  } else if (diffHour < 24) {
    return `${diffHour} hour${diffHour > 1 ? "s" : ""} ago`
  } else if (diffDay < 7) {
    return `${diffDay} day${diffDay > 1 ? "s" : ""} ago`
  } else {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }
}


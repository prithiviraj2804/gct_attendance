document.addEventListener("DOMContentLoaded", () => {
  // Check if settings page is in the DOM
  const settingsPage = document.getElementById("settings");
  if (!settingsPage) return;

  // DOM Elements
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");
  const systemName = document.getElementById("systemName");
  const academicYear = document.getElementById("academicYear");
  const departmentList = document.getElementById("departmentList");
  const addDepartmentBtn = document.getElementById("addDepartmentBtn");
  const currentUsername = document.getElementById("currentUsername");
  const newPassword = document.getElementById("newPassword");
  const confirmPassword = document.getElementById("confirmPassword");
  const changePasswordBtn = document.getElementById("changePasswordBtn");

  // Load settings data
  loadSettings();

  // Create and append the Add Department Modal to the body
  createAddDepartmentModal();

  // Open the modal when clicking the "Add Department" button
  addDepartmentBtn.addEventListener("click", () => {
    const addDepartmentModal = document.getElementById("addDepartmentModal");
    addDepartmentModal.style.display = "block";
  });

  // Close the modal when clicking outside or on the close button
  window.addEventListener("click", (event) => {
    const addDepartmentModal = document.getElementById("addDepartmentModal");
    if (event.target === addDepartmentModal) {
      closeAddDepartmentModal();
    }
  });

  // Load settings and departments
  function loadSettings() {
    const token = localStorage.getItem("authToken");

    fetch("/api/settings", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          systemName.value = data.settings.systemName || "GCT Attendance System";
          academicYear.value = data.settings.academicYear || "2023-2024";
        } else {
          alert("Failed to load settings: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error loading settings:", error);
        alert("An error occurred while loading settings.");
      });

    loadDepartments();
  }

  // Load departments
  function loadDepartments() {
    const token = localStorage.getItem("authToken");

    fetch("/api/get_departments", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          renderDepartmentList(data);
        } else {
          alert("Failed to load departments.");
        }
      })
      .catch((error) => {
        console.error("Error loading departments:", error);
        alert("Error loading departments.");
      });
  }

  // Create the Add Department Modal
  function createAddDepartmentModal() {
    const modal = document.createElement("div");
    modal.id = "addDepartmentModal";
    modal.className = "modal";
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close-btn" id="closeAddDepartmentModal">&times;</span>
        <h2>Add New Department</h2>
        <form id="addDepartmentForm">
          <div class="input-group">
            <label for="newDepartmentName">Department Name:</label>
            <input type="text" id="newDepartmentName" placeholder="Enter department name" required>
          </div>
          <button type="submit" class="submit-btn">Add Department</button>
        </form>
      </div>
    `;
    document.body.appendChild(modal);

    const closeBtn = modal.querySelector("#closeAddDepartmentModal");
    const addDepartmentForm = modal.querySelector("#addDepartmentForm");

    closeBtn.addEventListener("click", closeAddDepartmentModal);
    addDepartmentForm.addEventListener("submit", handleAddDepartment);
  }

  // Close the Add Department Modal
  function closeAddDepartmentModal() {
    const addDepartmentModal = document.getElementById("addDepartmentModal");
    addDepartmentModal.style.display = "none";
    document.getElementById("newDepartmentName").value = "";
  }

  // Handle Add Department Form Submission
  function handleAddDepartment(event) {
    event.preventDefault();
    const newDeptName = document.getElementById("newDepartmentName").value.trim();
    if (!newDeptName) {
      alert("Department name cannot be empty.");
      return;
    }

    const token = localStorage.getItem("authToken");

    fetch("/api/create_department/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: newDeptName }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          const newDept = { id: data.id, name: newDeptName };
          addDepartmentToUI(newDept);
          alert("Department added successfully!");
          closeAddDepartmentModal();
        } else {
          alert("Failed to add department: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error adding department:", error);
        alert("An error occurred while adding the department.");
      });
  }

  // Render department list
  function renderDepartmentList(departments) {
    departmentList.innerHTML = "";
    departments.forEach((dept) => {
      addDepartmentToUI(dept);
    });
  }

  // Add department to UI
  function addDepartmentToUI(dept) {
    const departmentItem = document.createElement("div");
    departmentItem.className = "department-item";
    departmentItem.innerHTML = `
      <input type="text" value="${dept.name}" readonly>
      <button class="edit-btn"><i class="fas fa-edit"></i></button>
      <button class="delete-btn"><i class="fas fa-trash"></i></button>
    `;

    const editBtn = departmentItem.querySelector(".edit-btn");
    const deleteBtn = departmentItem.querySelector(".delete-btn");

    editBtn.addEventListener("click", () => toggleEditDepartment(dept.id, departmentItem));
    deleteBtn.addEventListener("click", () => deleteDepartment(dept.id));

    departmentList.appendChild(departmentItem);
  }

  // Toggle Edit Department
  function toggleEditDepartment(deptId, departmentItem) {
    const input = departmentItem.querySelector("input");
    input.readOnly = !input.readOnly;
  }

  // Delete department
  function deleteDepartment(deptId) {
    const token = localStorage.getItem("authToken");
    fetch(`/api/departments/${deptId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(() => loadDepartments())
      .catch((error) => {
        alert("Failed to delete department.");
        console.error("Error deleting department:", error);
      });
  }
});

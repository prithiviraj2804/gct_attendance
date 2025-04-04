document.addEventListener("DOMContentLoaded", () => {
  // Check if settings page is in the DOM
  const settingsPage = document.getElementById("settings");
  if (!settingsPage) return;

  // DOM Elements
  const addDepartmentBtn = document.getElementById("addDepartmentBtn");
  const departmentList = document.getElementById("departmentList");

  // Load settings data
  loadDepartments();

  // Create and append the Add Department Modal
  createAddDepartmentModal();

  // Event Listener for Adding Department
  addDepartmentBtn.addEventListener("click", () => {
    const addDepartmentModal = document.getElementById("addDepartmentModal");
    addDepartmentModal.style.display = "block";
  });

  // Load Departments
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

  // Render Department List
  function renderDepartmentList(departments) {
    departmentList.innerHTML = "";
    departments.forEach((dept) => {
      addDepartmentToUI(dept);
    });
  }

  // Add Department to UI
  function addDepartmentToUI(dept) {
    const departmentItem = document.createElement("div");
    departmentItem.className = "department-item";
    departmentItem.innerHTML = `
      <input type="text" value="${dept.name}" readonly>
      <button class="edit-btn"><i class="fas fa-edit"></i></button>
      <button class="delete-btn"><i class="fas fa-trash"></i></button>
      <button class="batch-btn" data-id="${dept.id}"><i class="fas fa-layer-group"></i> Manage Batches</button>
    `;

    const batchBtn = departmentItem.querySelector(".batch-btn");
    batchBtn.addEventListener("click", () => manageBatches(dept.id, dept.name));

    departmentList.appendChild(departmentItem);
  }

  // Manage Batches (Display batch management modal)
  function manageBatches(deptId, deptName) {
    const batchModal = document.createElement("div");
    batchModal.className = "modal";
    batchModal.innerHTML = `
      <div class="modal-content">
        <span class="close-btn">&times;</span>
        <h2>Batches for ${deptName}</h2>
        <input type="text" id="newBatchName" placeholder="Enter batch name">
        <button id="addBatchBtn">Add Batch</button>
        <div id="batchList"></div>
      </div>
    `;
    document.body.appendChild(batchModal);

    const addBatchBtn = batchModal.querySelector("#addBatchBtn");
    addBatchBtn.addEventListener("click", () => {
      const newBatchName = batchModal.querySelector("#newBatchName").value.trim();
      if (newBatchName) {
        addBatch(deptId, newBatchName);
        batchModal.querySelector("#newBatchName").value = "";
      } else {
        alert("Batch name cannot be empty.");
      }
    });

    // Close the modal
    batchModal.querySelector(".close-btn").addEventListener("click", () => {
      document.body.removeChild(batchModal);
    });
  }

  // Add Batch to a Department
  function addBatch(deptId, batchName) {
    const token = localStorage.getItem("authToken");
    fetch(`/api/departments/${deptId}/batches`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: batchName }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert("Batch added successfully!");
      })
      .catch((error) => {
        console.error("Error adding batch:", error);
        alert("An error occurred while adding the batch.");
      });
  }
});

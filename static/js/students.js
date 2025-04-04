document.addEventListener("DOMContentLoaded", () => {
  // Check if students page is in the DOM
  const studentsPage = document.getElementById("students");
  if (!studentsPage) return;

  // DOM Elements
  const addStudentBtn = document.getElementById("addStudentBtn");
  const studentsTableBody = document.getElementById("studentsTableBody");
  const uploadStudentsBtn = document.createElement("button");

  // Add "Upload Students" button dynamically
  uploadStudentsBtn.id = "uploadStudentsBtn";
  uploadStudentsBtn.textContent = "Upload Students";
  uploadStudentsBtn.className = "primary-btn";
  studentsPage.appendChild(uploadStudentsBtn);

  // Create Upload Modal dynamically
  const uploadStudentsModal = document.createElement("div");
  uploadStudentsModal.id = "uploadStudentsModal";
  uploadStudentsModal.className = "modal";
  uploadStudentsModal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h2>Upload Students</h2>
        <button class="close-btn" id="closeUploadModal">&times;</button>
      </div>
      <div class="modal-body">
        <form id="uploadStudentsForm">
          <div class="form-group">
            <label for="studentsFile">Select Excel File:</label>
            <input type="file" id="studentsFile" accept=".xlsx, .xls" required>
          </div>
          <div class="form-actions">
            <button type="submit" class="primary-btn">Upload</button>
            <button type="button" class="secondary-btn" id="cancelUploadBtn">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  `;
  document.body.appendChild(uploadStudentsModal);

  // Modal DOM Elements
  const closeUploadModal = document.getElementById("closeUploadModal");
  const cancelUploadBtn = document.getElementById("cancelUploadBtn");
  const uploadStudentsForm = document.getElementById("uploadStudentsForm");
  const studentsFile = document.getElementById("studentsFile");

  // Open Upload Modal
  uploadStudentsBtn.addEventListener("click", () => {
    uploadStudentsModal.classList.add("active");
  });

  // Close Upload Modal
  closeUploadModal.addEventListener("click", () => {
    uploadStudentsModal.classList.remove("active");
  });

  cancelUploadBtn.addEventListener("click", () => {
    uploadStudentsModal.classList.remove("active");
  });

  // Handle File Upload
  uploadStudentsForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const file = studentsFile.files[0];
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const token = localStorage.getItem("authToken");

    fetch("/api/upload_students/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Students uploaded successfully!");
          uploadStudentsModal.classList.remove("active");
          loadStudents(); // Reload the students table
        } else {
          alert(data.message || "Failed to upload students.");
        }
      })
      .catch((error) => {
        console.error("Error uploading students:", error);
        alert("An error occurred while uploading the students.");
      });
  });

  // Load initial students data
  loadStudents();

  // Function to load students
  function loadStudents() {
    const token = localStorage.getItem("authToken");
    studentsTableBody.innerHTML = '<tr><td colspan="3" class="loading-text">Loading students...</td></tr>';

    fetch("/api/students", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          renderStudentsTable(data);
        } else {
          console.error("Failed to load students:", data.message);
          studentsTableBody.innerHTML = '<tr><td colspan="3" class="loading-text">Failed to load students</td></tr>';
        }
      })
      .catch((error) => {
        console.error("Error loading students:", error);
        studentsTableBody.innerHTML = '<tr><td colspan="3" class="loading-text">Error loading students</td></tr>';
      });
  }

  // Function to render students table
  function renderStudentsTable(students) {
    studentsTableBody.innerHTML = "";
    students.forEach((student) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${student.id}</td>
        <td>${student.name}</td>
        <td>${student.section_id}</td>
      `;
      studentsTableBody.appendChild(tr);
    });
  }
});
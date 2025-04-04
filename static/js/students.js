document.addEventListener("DOMContentLoaded", () => {
  // Check if students page is in the DOM
  const studentsPage = document.getElementById("students");
  if (!studentsPage) return;

  // DOM Elements
  const addStudentBtn = document.getElementById("addStudentBtn");
  const studentsTableBody = document.getElementById("studentsTableBody");

  // Create Add Student Modal dynamically
  function createAddStudentModal() {
    const addStudentModal = document.createElement("div");
    addStudentModal.id = "addStudentModal";
    addStudentModal.className = "modal";
    addStudentModal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2>Add New Student</h2>
          <button class="close-btn" id="closeAddStudentModal">&times;</button>
        </div>
        <div class="modal-body">
          <form id="addStudentForm">
            <div class="form-group">
              <label for="studentName">Student Name:</label>
              <input type="text" id="studentName" name="studentName" placeholder="Enter student name" required>
            </div>
            <div class="form-actions">
              <button type="submit" class="primary-btn">Add Student</button>
              <button type="button" class="secondary-btn" id="cancelAddStudentBtn">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    `;
    document.body.appendChild(addStudentModal);
  }

  // Initialize modal
  createAddStudentModal();

  // Modal DOM Elements (after creation)
  const addStudentModal = document.getElementById("addStudentModal");
  const closeAddStudentModal = document.getElementById("closeAddStudentModal");
  const cancelAddStudentBtn = document.getElementById("cancelAddStudentBtn");
  const addStudentForm = document.getElementById("addStudentForm");

  // Open Add Student Modal
  addStudentBtn.addEventListener("click", () => {
    addStudentModal.classList.add("active");
    addStudentForm.reset(); // Clear the form when opened
  });

  // Close Add Student Modal
  function closeModal() {
    addStudentModal.classList.remove("active");
    addStudentForm.reset();
  }

  closeAddStudentModal.addEventListener("click", closeModal);
  cancelAddStudentBtn.addEventListener("click", closeModal);

  // Handle Add Student Form Submission
  addStudentForm.addEventListener("submit", (e) => {
    e.preventDefault();

    // Accessing the student name from the form input correctly
    const studentName = addStudentForm.studentName.value.trim();
    console.log("Student Name:", studentName); // For debugging
    if (!studentName) {
      alert("Student name cannot be empty.");
      return;
    }

    const token = localStorage.getItem("authToken");

    fetch("/api/students/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: studentName }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.id) {
          alert("Student added successfully!");
          closeModal();
          loadStudents(); // Reload the students table
        } else {
          alert(data.message || "Failed to add student.");
        }
      })
      .catch((error) => {
        console.error("Error adding student:", error);
        alert("An error occurred while adding the student.");
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
        <td>${student.section_name}</td>
        <td>${student.name}</td>
        <td>${student.section_id || "N/A"}</td>
        <td>${student.year}</td>
        <td>
          <button class="delete-btn" data-id="${student.id}"><i class="fas fa-trash"></i></button>
        </td>
      `;
      studentsTableBody.appendChild(tr);

      // Add event listener for delete button
      const deleteBtn = tr.querySelector(".delete-btn");
      deleteBtn.addEventListener("click", () => deleteStudent(student.id));
    });
  }

  // Function to delete a student
  function deleteStudent(studentId) {
    const token = localStorage.getItem("authToken");

    if (!confirm("Are you sure you want to delete this student?")) return;

    fetch(`/api/students/${studentId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          alert("Student deleted successfully!");
          loadStudents(); // Reload the students table
        } else {
          alert(data.message || "Failed to delete student.");
        }
      })
      .catch((error) => {
        console.error("Error deleting student:", error);
        alert("An error occurred while deleting the student.");
      });
  }
});

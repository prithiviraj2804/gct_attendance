document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm")
    const loginMessage = document.getElementById("loginMessage")
  
    // Check if user is already logged in
    const token = localStorage.getItem("authToken")
    if (token) {
      window.location.href = "/static/dashboard.html"
    }
  
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault()
  
      const username = document.getElementById("username").value
      const password = document.getElementById("password").value
  
      // Show loading state
      const loginBtn = loginForm.querySelector("button")
      const originalBtnText = loginBtn.textContent
      loginBtn.textContent = "Logging in..."
      loginBtn.disabled = true
  
      // Make API request to login
      fetch("/api/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.access_token) { // Check for the token instead of `success`
                // Store auth token and user info
                localStorage.setItem("authToken", data.access_token)
                localStorage.setItem("tokenType", data.token_type || "bearer")
    
                // Redirect to dashboard
                window.location.href = "dashboard.html"
            } else {
                // Show error message
                loginMessage.textContent = data.message || "Invalid username or password"
    
                // Reset form button
                loginBtn.textContent = originalBtnText
                loginBtn.disabled = false
            }
        })
        .catch((error) => {
            console.error("Login error:", error)
            loginMessage.textContent = "An error occurred. Please try again."
    
            // Reset form button
            loginBtn.textContent = originalBtnText
            loginBtn.disabled = false
        })
        .catch((error) => {
          console.error("Login error:", error)
          loginMessage.textContent = "An error occurred. Please try again."
  
          // Reset form button
          loginBtn.textContent = originalBtnText
          loginBtn.disabled = false
        })
    })
  })
  
  
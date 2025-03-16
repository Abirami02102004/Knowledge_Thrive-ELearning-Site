document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".container");
    const registerBtn = document.querySelector(".register-btn");
    const loginBtn = document.querySelector(".login-btn");

    if (registerBtn && loginBtn) {
        registerBtn.addEventListener("click", () => container.classList.add("active"));
        loginBtn.addEventListener("click", () => container.classList.remove("active"));
    }

    // Function to handle form submission
    async function handleFormSubmit(event, url) {
        event.preventDefault(); // Prevent default form submission

        // Get form data
        const formData = new FormData(event.target);
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value.trim();
        });

        // Validate required fields
        if (Object.values(formObject).some(value => value === "")) {
            alert("All fields are required!");
            return;
        }

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formObject)
            });

            const data = await response.json();
            alert(data.message);

            if (response.ok && data.redirect) {
                window.location.href = data.redirect;
            }
        } catch (error) {
            alert("An error occurred. Please try again.");
            console.error("Error:", error);
        }
    }

    // Attach event listeners to forms
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    if (loginForm) {
        loginForm.addEventListener("submit", (event) => handleFormSubmit(event, "/login"));
    }

    if (registerForm) {
        registerForm.addEventListener("submit", (event) => handleFormSubmit(event, "/register"));
    }
});

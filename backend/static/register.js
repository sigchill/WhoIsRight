const registerForm = document.getElementById("registerForm");
const message = document.getElementById("message");


registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const email = document.getElementById("email").value.trim();

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: email
            })
        });

        const data = await response.json();

        if (!response.ok) {
            message.textContent = "Error: " + data.detail;
            message.style.color = "red";
            return;
        }

        message.textContent = "Registration successful! You can now log in.";
        message.style.color = "green";

        document.getElementById("username").value = "";
        document.getElementById("password").value = "";
        document.getElementById("email").value = "";
    } catch (error) {
        message.textContent = "An error occurred. Please try again.";
        message.style.color = "red";
    }
}); 
    
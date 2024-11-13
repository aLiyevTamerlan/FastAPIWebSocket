async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");

    try {
        const response = await fetch("/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            window.location.href = "/home";
        } else {
            errorMessage.textContent = "Invalid username or password.";
        }
    } catch (error) {
        errorMessage.textContent = "Error logging in. Please try again later.";
        console.error("Login error:", error);
    }
}
console.log("h")

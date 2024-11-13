async function populateUserDropdown() {
    try {
        const response = await fetch('/users');  // Endpoint to get all users
        const users = await response.json();
        
        const userSelect = document.getElementById("user-select");
        console.log(userSelect)
        // Populate the dropdown with user data
        users.forEach(user => {
            const option = document.createElement("option");
            option.value = user.id;  // Assuming 'id' is the unique identifier for each user
            option.textContent = user.username;  // Assuming 'name' is a display name for the user
            userSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching users:", error);
    }
}
async function sendMessage(message) {
    const userId = document.getElementById("user-select").value;

    await fetch("/message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: userId, message: message })
    });
}
async function getUserInfo() {
    try {
        // Get the JWT token from localStorage
        const token = localStorage.getItem("access_token");
        if (!token) {
            window.location.href = "/";  // Redirect to login page if no token
            return;
        }

        // Make the API call to get the user info
        const response = await fetch("/user", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Redirect to login page if token is invalid or expired
                window.location.href = "/";
            } else {
                throw new Error("Failed to fetch user info");
            }
        }

        const data = await response.json();

        // Display user information on the page
        document.getElementById("navbar-username").textContent = `Username: ${data.username}`;
        document.getElementById("navbar-role").textContent = `Role: ${data.role}`;
        const socket = new WebSocket(`ws://localhost:8000/ws/notifications/${data.id}`);
                
        socket.onmessage = function(event) {
            var messages = document.getElementById('messages')
            var message = document.createElement('li')
            var content = document.createTextNode(event.data)
            message.appendChild(content)
            messages.appendChild(message)
    };

        if (data.role === "manager") {
            await populateUserDropdown()
 // Proceed if a valid ID is selected


            const commentSection = document.getElementById("manager-comment-section");
            // Create an input field for adding a comment
            const commentInput = document.createElement("input");
            commentInput.type = "text";
            commentInput.id = "comment-input";
            commentInput.placeholder = "Add a comment";
            
            // Optionally, create a button to submit the comment
            const submitButton = document.createElement("button");
            submitButton.id = "submit-comment";
            submitButton.textContent = "Submit";

            // Add event listener for the submit button to handle the comment submission
            submitButton.addEventListener("click", function() {
                const comment = commentInput.value;
                if (comment) {
                    // Here, you can handle the comment submission logic
                    console.log("Comment submitted:", comment);
                    sendMessage(message=comment)
                    // Clear the input after submission

            socket.onclose = function() {
                console.log("WebSocket connection closed.");
            };
                    commentInput.value = "";
                } else {
                    alert("Please enter a comment before submitting.");
                }

            });

            commentSection.append(commentInput);
            commentSection.append(submitButton);
            } 
        }
    catch (error) {
        console.error(error);
        alert("An error occurred while fetching user data.");
        // window.location.href = "/";  // Redirect to login page on error
    }
}
function logout() {
    // Clear the access token from localStorage
    localStorage.removeItem("access_token");
    
    // Redirect the user to the login page
    window.location.href = "/";
}

// Call the function to fetch user info when the page loads
window.onload = function() {
    getUserInfo();
};
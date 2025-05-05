let currentUser = null;
let currentReceiverUsername = null;

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    try {
        const response = await fetch("http://localhost:5000/auth/profile", {
            method: "GET",
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`Unexpected error: ${response.status}`);
        }
        
        const data = await response.json();
        currentUser = data.username;

        console.log("Logged in as:", currentUser);

        // Update "Welcome {username}" in the top-right section
        document.getElementById("logged-in-user").innerText = currentUser;

        initializeChat();

    } catch (error) {
        console.error("Session check failed:", error);
        localStorage.removeItem("token");
        window.location.href = "../auth/login.html";
    }
});

function initializeChat() {
    setupEventListeners();
    refreshOnlineUsers();
    loadPublicMessages();
    setupPolling();
}

function setupEventListeners() {
    document.getElementById("sendMessageBtn").addEventListener("click", sendMessage);
    document.getElementById("logoutBtn").addEventListener("click", logout);
    document.getElementById("back-to-public").addEventListener("click", switchToPublicChat); // New Button
}

// Sending a Message
async function sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const message = messageInput.value.trim();

    if (!message) return;

    const endpoint = currentReceiverUsername
        ? "/chat/send_private_message"
        : "/chat/send_public_message";

    let bodyData = { message };
    if (currentReceiverUsername) {
        bodyData.receiver = currentReceiverUsername; 
    }

    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://localhost:5000${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(bodyData),
        });

        if (!response.ok) {
            throw new Error(`Message send failed: ${response.status}`);
        }

        messageInput.value = "";
        currentReceiverUsername ? loadPrivateMessages() : loadPublicMessages();
    } catch (error) {
        console.error("Message send error:", error);
    }
}

// Polling for Updates
function setupPolling() {
    setInterval(() => {
        currentReceiverUsername ? loadPrivateMessages() : loadPublicMessages();
        refreshOnlineUsers();
    }, 5000);
}

// Load Public Messages
async function loadPublicMessages() {
    try {
        const response = await fetch("http://localhost:5000/chat/get_public_messages");
        const data = await response.json();

        const messagesContainer = document.getElementById("messages");
        messagesContainer.innerHTML = "";

        if (data.messages && Array.isArray(data.messages)) {
            data.messages.forEach((msg) => {
                const msgElement = document.createElement("p");
                msgElement.textContent = msg;
                messagesContainer.appendChild(msgElement);
            });
        }
    } catch (error) {
        console.error("Error fetching public messages:", error);
    }
}

// Load Online Users
async function refreshOnlineUsers() {
    try {
        const token = localStorage.getItem("token");

        const response = await fetch("http://localhost:5000/auth/get_online_users", {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${token}`, 
                "Content-Type": "application/json" 
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch users: ${response.status}`);
        }

        const data = await response.json();
        console.log("Online Users Response:", data);

        const usersContainer = document.getElementById("online-users");
        usersContainer.innerHTML = ""; // Clear before adding new users

        if (data.users && Array.isArray(data.users)) {
            data.users.forEach((username) => {
                const userElement = document.createElement("li");
                userElement.classList.add("online-user");

                // Create a small green dot
                const statusDot = document.createElement("span");
                statusDot.classList.add("status-dot");

                // Append dot and username
                userElement.appendChild(statusDot);
                userElement.appendChild(document.createTextNode(" " + username));

                // Clicking a user starts private chat
                userElement.addEventListener("click", () => startPrivateChat(username));
                
                usersContainer.appendChild(userElement);
            });
        } else {
            console.warn("No online users found");
        }
    } catch (error) {
        console.error("Error fetching online users:", error);
    }
}

// Start Private Chat 
function startPrivateChat(username) {
    currentReceiverUsername = username;  // Store receiver's username
    document.getElementById("chat-title").textContent = `Chat with ${username}`;
    document.getElementById("back-to-public").style.display = "block";
    loadPrivateMessages();
}

// Load Private Messages 
async function loadPrivateMessages() {
    if (!currentReceiverUsername) return;

    try {
        const token = localStorage.getItem("token");
        const response = await fetch(
            `http://localhost:5000/chat/get_private_messages?receiver=${currentReceiverUsername}`,
            { headers: { Authorization: `Bearer ${token}` } }
        );

        if (!response.ok) {
            throw new Error(`Failed to load messages: ${response.status}`);
        }

        const data = await response.json();
        const messagesContainer = document.getElementById("messages");

        // Clear and refresh the chat window
        messagesContainer.innerHTML = "";

        if (data.messages.length === 0) {
            messagesContainer.innerHTML = "<p>No messages yet.</p>";
            return;
        }

        // Append messages properly
        data.messages.forEach((msg) => {
            const msgElement = document.createElement("div");
            msgElement.classList.add("message");

            msgElement.innerHTML = `<strong>${msg.sender}:</strong> ${msg.message} 
                <br><small>${new Date(msg.timestamp).toLocaleString()}</small>`;

            messagesContainer.appendChild(msgElement);
        });

    } catch (error) {
        console.error("Error fetching private messages:", error);
    }
}

// Switch Back to Public Chat 
function switchToPublicChat() {
    currentReceiverUsername = null; 
    document.getElementById("chat-title").textContent = "General Chat";
    document.getElementById("back-to-public").style.display = "none";
    
    // Ensure profile picture is properly loaded
    const profilePic = document.getElementById("profile-pic");
    if (profilePic) {
        profilePic.src = "../assets/images/logo.jpg";
    }
    
    loadPublicMessages();
}

function redirectToProfile() {
    window.location.href = "profile.html";
}

// Logout User Broadcast Message
async function logout() {
    try {
        let token = localStorage.getItem("token");

        // Notify all users that this user left
        await fetch("http://localhost:5000/chat/send_public_message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ message: `${currentUser} left the chat.` }),
        });

        // Call backend logout
        await fetch("http://localhost:5000/auth/logout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
        });

        localStorage.removeItem("token");
        window.location.href = "../auth/login.html";
    } catch (error) {
        console.error("Logout failed:", error);
    }
}

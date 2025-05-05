document.addEventListener("DOMContentLoaded", function () {
    const usernameEl = document.getElementById("username");
    async function fetchUserProfile() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('No token found! Please log in.');
            }

            const response = await fetch('http://localhost:5000/auth/profile', {
                method: 'GET',
                headers: { 'Authorization': 'Bearer ' + token }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user profile');
            }

            const data = await response.json();
            usernameEl.textContent = data.username;
        } catch (error) {
            console.error("Error fetching user profile:", error);
            usernameEl.textContent = "Error loading profile";
        }
    }

    fetchUserProfile();
});

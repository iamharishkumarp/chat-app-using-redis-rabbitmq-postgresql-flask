// Signup Function
async function handleSignup() {
    const signupForm = document.getElementById('signupForm');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('signupUsername').value.trim();
            const password = document.getElementById('signupPassword').value.trim();
            const confirmPassword = document.getElementById('confirmPassword').value.trim();
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');

            if (errorMessage) errorMessage.style.display = 'none';
            if (successMessage) successMessage.style.display = 'none';

            if (!username || !password || !confirmPassword) {
                errorMessage.textContent = 'All fields are required';
                errorMessage.style.display = 'block';
                return;
            }

            if (password !== confirmPassword) {
                errorMessage.textContent = 'Passwords do not match';
                errorMessage.style.display = 'block';
                return;
            }

            if (password.length < 6) {
                errorMessage.textContent = 'Password must be at least 6 characters';
                errorMessage.style.display = 'block';
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/auth/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    successMessage.textContent = 'Signup successful! Redirecting to login...';
                    successMessage.style.display = 'block';
                    setTimeout(() => window.location.href = '../auth/login.html', 2000);
                } else {
                    errorMessage.textContent = data.message || 'Signup failed. Please try again.';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                console.error('Signup error:', error);
                errorMessage.textContent = 'Network error. Please try again.';
                errorMessage.style.display = 'block';
            }
        });
    }
}

// Login Function
async function handleLogin() {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorMessage = document.getElementById('errorMessage');

            if (errorMessage) errorMessage.style.display = 'none';

            if (!username || !password) {
                errorMessage.textContent = 'Username and password are required';
                errorMessage.style.display = 'block';
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                console.log("Login Response", data); // debugging output

                if (response.ok) {
                    localStorage.setItem('token', data.access_token); // Store JWT Token
                    window.location.href = '../chat/index.html';
                } else {
                    errorMessage.textContent = data.message || 'Login failed. Please check your credentials.';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                console.error('Login error:', error);
                errorMessage.textContent = 'Network error. Please try again.';
                errorMessage.style.display = 'block';
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    handleSignup();
    handleLogin();
});



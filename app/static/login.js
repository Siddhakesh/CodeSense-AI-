// State
let isLoginMode = true;

// DOM Elements
const authForm = document.getElementById('authForm');
const authTitle = document.getElementById('authTitle');
const authSubmitText = document.getElementById('authSubmitText');
const authSwitchText = document.getElementById('authSwitchText');
const authSwitchLink = document.getElementById('authSwitchLink');
const emailGroup = document.getElementById('emailGroup');
const emailInput = document.getElementById('email');
const errorMsg = document.getElementById('errorMsg');

// Event Listeners
authForm.addEventListener('submit', handleAuth);
authSwitchLink.addEventListener('click', (e) => {
    e.preventDefault();
    toggleAuthMode();
});

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    errorMsg.style.display = 'none';

    if (isLoginMode) {
        authTitle.textContent = 'Login';
        authSubmitText.textContent = 'Login';
        authSwitchText.textContent = "Don't have an account?";
        authSwitchLink.textContent = 'Sign Up';
        emailGroup.style.display = 'none';
        emailInput.required = false;
    } else {
        authTitle.textContent = 'Sign Up';
        authSubmitText.textContent = 'Sign Up';
        authSwitchText.textContent = "Already have an account?";
        authSwitchLink.textContent = 'Login';
        emailGroup.style.display = 'flex';
        emailInput.required = true;
    }
}

async function handleAuth(e) {
    e.preventDefault();

    // Clear error
    errorMsg.style.display = 'none';
    errorMsg.textContent = '';

    const formData = new FormData(authForm);
    const data = Object.fromEntries(formData.entries());

    // Validate inputs
    if (!data.username || !data.password) {
        showError("Username and password are required");
        return;
    }

    if (!isLoginMode && !data.email) {
        showError("Email is required for signup");
        return;
    }

    const originalBtnText = authSubmitText.textContent;
    authSubmitText.textContent = 'Please wait...';
    const submitBtn = authForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    try {
        if (isLoginMode) {
            // Login
            const loginData = new URLSearchParams();
            loginData.append('username', data.username);
            loginData.append('password', data.password);

            const response = await fetch('/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: loginData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const result = await response.json();

            // Save token and user
            localStorage.setItem('token', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));

            // Redirect to home
            window.location.href = '/';

        } else {
            // Signup
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: data.username,
                    email: data.email,
                    password: data.password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Signup failed');
            }

            // Auto login after signup
            // Re-use logic or just switch to login mode and fill fields?
            // Let's just try to login automatically
            const loginData = new URLSearchParams();
            loginData.append('username', data.username);
            loginData.append('password', data.password);

            const loginResp = await fetch('/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: loginData
            });

            if (loginResp.ok) {
                const result = await loginResp.json();
                localStorage.setItem('token', result.access_token);
                localStorage.setItem('user', JSON.stringify(result.user));
                window.location.href = '/';
            } else {
                // Should not happen if signup worked, but fallback to login screen
                isLoginMode = true;
                toggleAuthMode();
                showError("Account created! Please log in.");
            }
        }
    } catch (error) {
        showError(error.message);
    } finally {
        authSubmitText.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}

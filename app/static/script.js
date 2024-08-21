// Navigation
document.getElementById('home-nav').addEventListener('click', () => showSection('home'));
document.getElementById('dashboard-nav').addEventListener('click', () => showSection('dashboard'));
document.getElementById('login-nav').addEventListener('click', () => showSection('auth'));
document.getElementById('register-nav').addEventListener('click', () => showSection('auth'));
document.getElementById('logout-nav').addEventListener('click', logout);
document.getElementById('pricing-nav').addEventListener('click', () => showSection('pricing'));
document.getElementById('research-nav').addEventListener('click', () => showSection('research'));
document.getElementById('philosophy-nav').addEventListener('click', () => showSection('philosophy'));

// Auth forms
document.getElementById('login').addEventListener('submit', login);
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            alert('Registration successful! Please log in.');
            document.getElementById('register-form').reset();
            document.getElementById('login').style.display = 'block';
            document.getElementById('register').style.display = 'none';
        } else {
            alert(data.message || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('An error occurred during registration. Please try again.');
    }
});

// API form
document.getElementById('api-form').addEventListener('submit', setApiCredentials);


function showSection(sectionId) {
    document.querySelectorAll('main > section').forEach(section => section.style.display = 'none');
    document.getElementById(sectionId).style.display = 'block';
    if (sectionId === 'auth') {
        document.getElementById('login').style.display = 'block';
        document.getElementById('register').style.display = 'none';
    }
}

document.getElementById('login-nav').addEventListener('click', () => {
    showSection('auth');
    document.getElementById('login').style.display = 'block';
    document.getElementById('register').style.display = 'none';
});

document.getElementById('register-nav').addEventListener('click', () => {
    showSection('auth');
    document.getElementById('login').style.display = 'none';
    document.getElementById('register').style.display = 'block';
});

async function register(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();
        if (data.success) {
            showMessage('Registration successful! Please log in.', 'success');
            document.getElementById('register').reset();
            showSection('login');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('An error occurred during registration', 'error');
    }
}

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 5000);
}

async function login(e) {
    e.preventDefault();
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: document.getElementById('login-username').value,
                password: document.getElementById('login-password').value
            })
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            await showDashboard();
        } else {
            console.error('Login failed:', data.message);
            alert('Login failed: ' + data.message);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login');
    }
}

function logout() {
    localStorage.removeItem('token');
    document.getElementById('logout-nav').style.display = 'none';
    document.getElementById('dashboard-nav').style.display = 'none';
    document.getElementById('login-nav').style.display = 'inline';
    document.getElementById('register-nav').style.display = 'inline';
    showSection('home');
}

async function showDashboard() {
    document.getElementById('auth').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('logout-nav').style.display = 'inline';
    document.getElementById('login-nav').style.display = 'none';
    document.getElementById('register-nav').style.display = 'none';
    document.getElementById('dashboard-nav').style.display = 'inline';
    
    const response = await fetch('/auth/check_subscription', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await response.json();
    
    if (data.subscription_active) {
        document.getElementById('trading').style.display = 'block';
        document.getElementById('api-credentials').style.display = 'block';
        document.getElementById('daily-trades-toggle').style.display = 'block';
        document.getElementById('daily-trades-switch').checked = data.daily_trades_enabled;
        document.getElementById('daily-trades-switch').addEventListener('change', toggleDailyTrades);
    } else {
        document.getElementById('trading').style.display = 'none';
        document.getElementById('api-credentials').style.display = 'none';
        document.getElementById('subscription-message').style.display = 'block';
        document.getElementById('subscription-message').textContent = 'Your subscription is not active. Please contact support to activate your account.';
    }

    // Check if API credentials exist
    const apiCredentialsResponse = await fetch('/auth/check_api_credentials', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const apiCredentialsData = await apiCredentialsResponse.json();
    console.log('API Credentials Exist:', apiCredentialsData.credentials_exist); // Debugging line
    updateApiCredentialsUI(apiCredentialsData.credentials_exist);
}

async function setApiCredentials(e) {
    e.preventDefault();
    try {
        const response = await fetch('/auth/set_api_credentials', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                api_key: document.getElementById('api-key').value,
                api_secret: document.getElementById('api-secret').value
            })
        });
        const data = await response.json();
        alert(data.message);
        updateApiCredentialsUI(true);
    } catch (error) {
        console.error('Set API credentials error:', error);
        alert('An error occurred while setting API credentials');
    }
}

function updateApiCredentialsUI(credentialsExist) {
    const title = document.getElementById('api-credentials-title');
    const button = document.getElementById('api-submit-button');
    
    console.log('Updating UI:', credentialsExist); // Debugging line
    if (credentialsExist) {
        title.textContent = 'Update API Credentials';
        button.textContent = 'Update Credentials';
    } else {
        title.textContent = 'Set API Credentials';
        button.textContent = 'Set Credentials';
    }
}


async function toggleDailyTrades() {
    try {
        const response = await fetch('/trading/toggle_daily_trades', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ enabled: document.getElementById('daily-trades-switch').checked })
        });
        const data = await response.json();
        alert(data.message);
    } catch (error) {
        console.error('Toggle daily trades error:', error);
        alert('An error occurred while toggling daily trades');
    }
}
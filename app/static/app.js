// DOM Elements
const form = document.getElementById('ingestForm');
const repoUrlInput = document.getElementById('repoUrl');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnLoader = analyzeBtn.querySelector('.btn-loader');
const resultsDiv = document.getElementById('results');
const profileResultsDiv = document.getElementById('profileResults');
const errorDiv = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');
const chatMessages = document.getElementById('chatMessages');
const closeResultsBtn = document.getElementById('closeResults');
const closeProfileResultsBtn = document.getElementById('closeProfileResults');
const modeBtns = document.querySelectorAll('button.nav-item');
const welcomeState = document.getElementById('welcomeState');
const historyResults = document.getElementById('historyResults');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

// Auth DOM
const authModal = document.getElementById('authModal');
const closeModalBtn = document.querySelector('.close-modal');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const profileNavBtn = document.getElementById('profileNavBtn');
const authForm = document.getElementById('authForm');
const authTitle = document.getElementById('authTitle');
const authSubmitText = document.getElementById('authSubmitText');
const authSwitchText = document.getElementById('authSwitchText');
const authSwitchLink = document.getElementById('authSwitchLink');
const emailGroup = document.getElementById('emailGroup');

// State
let currentRepoData = null;
let currentMode = 'repo'; // 'repo' or 'profile'
let isLoginMode = true;
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let token = localStorage.getItem('token') || null;

// Event Listeners
form.addEventListener('submit', handleSubmit);
closeResultsBtn.addEventListener('click', hideResults);
closeProfileResultsBtn.addEventListener('click', hideResults);
clearHistoryBtn.addEventListener('click', clearHistory);
sendMessageBtn.addEventListener('click', handleSendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        setMode(btn.dataset.mode);
    });
});

// Configure Marked.js
marked.setOptions({
    highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

function setMode(mode) {
    currentMode = mode;

    // Update UI
    modeBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Update Form
    if (mode === 'repo') {
        repoUrlInput.placeholder = 'https://github.com/username/repository';
        btnText.textContent = 'Analyze Repository';
        repoUrlInput.value = '';
    } else if (mode === 'profile') {
        repoUrlInput.placeholder = 'GitHub Username (e.g. tiangolo)';
        btnText.textContent = 'Analyze Profile';
        repoUrlInput.value = '';
    } else if (mode === 'history') {
        repoUrlInput.placeholder = 'Select an item from history...';
        btnText.textContent = 'Analyze';
        repoUrlInput.value = '';
    }

    // Hide all results
    hideResults();

    if (mode === 'history') {
        welcomeState.style.display = 'none';
        historyResults.style.display = 'block';
        renderHistory();
    } else {
        historyResults.style.display = 'none';
    }

    hideError();
}

async function handleSubmit(e) {
    e.preventDefault();

    const input = repoUrlInput.value.trim();

    if (!input) {
        showError('Please enter a value');
        return;
    }

    // Show loading state
    setLoading(true);
    hideError();
    hideResults();

    try {
        if (currentMode === 'repo') {
            await handleRepoAnalysis(input);
        } else {
            await handleProfileAnalysis(input);
        }

    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

async function handleRepoAnalysis(repoUrl) {
    const response = await fetch('/api/ingest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze repository');
    }

    const data = await response.json();
    currentRepoData = data; // Store data for chat context
    displayResults(data);
}

async function handleProfileAnalysis(username) {
    // Clean username if url is provided
    if (username.includes('github.com')) {
        username = username.split('/').pop();
    }

    const response = await fetch(`/api/profile/${username}`);

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze profile');
    }

    const data = await response.json();
    displayProfileResults(data);
}

async function handleSendMessage() {
    const question = chatInput.value.trim();
    if (!question || !currentRepoData) return;

    // Add user message
    addMessage(question, 'user');
    chatInput.value = '';

    // Disable input while loading
    chatInput.disabled = true;
    sendMessageBtn.disabled = true;

    // Add temporary loading message
    const loadingId = addMessage('Thinking...', 'ai', true);

    try {
        const context = buildContextFromData(currentRepoData);

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repo_id: currentRepoData.repo_url.split('/').pop(),
                question: question,
                context: context
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get response');
        }

        const data = await response.json();

        // Remove loading message and add real response
        removeMessage(loadingId);
        addMessage(data.answer, 'ai');

    } catch (error) {
        removeMessage(loadingId);
        addMessage('Sorry, I encountered an error while processing your request.', 'ai');
        console.error(error);
    } finally {
        chatInput.disabled = false;
        sendMessageBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(text, sender, isLoading = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = `message-content ${sender === 'ai' ? 'markdown-body' : ''}`;

    if (isLoading) {
        contentDiv.innerHTML = '<div class="spinner" style="border-width: 2px;"></div> Thinking...';
    } else if (sender === 'ai') {
        contentDiv.innerHTML = marked.parse(text);
        // Highlight code blocks
        contentDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    } else {
        contentDiv.textContent = text;
    }

    messageDiv.appendChild(contentDiv);

    // Generate simple ID
    const id = Date.now().toString();
    messageDiv.id = id;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function buildContextFromData(data) {
    let context = `Repository: ${data.repo_url}\n`;
    context += `Framework: ${data.framework}\n`;
    context += `Total Files: ${data.total_files}\n\n`;

    context += `File Structure:\n`;
    // List up to 50 files to avoid context limit overflow
    const files = data.files.slice(0, 50);
    files.forEach(f => {
        context += `- ${f.path} (${f.language})\n`;
    });

    if (data.files.length > 50) {
        context += `... and ${data.files.length - 50} more files.\n`;
    }

    context += `\nDependency Graph (Files with dependencies):\n`;
    Object.entries(data.dependency_graph).forEach(([file, deps]) => {
        if (deps.length > 0) {
            context += `${file} depends on: ${deps.join(', ')}\n`;
        }
    });

    return context;
}

function setLoading(loading) {
    analyzeBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoader.style.display = loading ? 'flex' : 'none';
    if (loading) {
        btnLoader.style.alignItems = 'center';
        btnLoader.style.justifyContent = 'center';
        btnLoader.style.gap = '10px';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorDiv.style.display = 'block';

    // Auto hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function hideError() {
    errorDiv.style.display = 'none';
}

function hideResults() {
    resultsDiv.style.display = 'none';
    profileResultsDiv.style.display = 'none';
    welcomeState.style.display = 'flex';
}

function displayResults(data) {
    // Extract repo name from URL
    const repoName = data.repo_url.split('/').slice(-2).join('/');
    document.getElementById('repoName').textContent = repoName;

    // Framework
    document.getElementById('framework').textContent = data.framework || 'Unknown';

    // Total files
    document.getElementById('totalFiles').textContent = data.total_files.toLocaleString();

    // Indexed timestamp
    const indexedDate = new Date(data.indexed_at);
    document.getElementById('indexedAt').textContent = indexedDate.toLocaleString();

    // Show results to ensure canvas has dimensions
    welcomeState.style.display = 'none';
    resultsDiv.style.display = 'block';

    // Display files list
    addToHistory({
        type: 'repo',
        value: data.repo_url,
        meta: {
            stars: data.stars,
            lang: data.files.length > 0 ? data.files[0].language : 'Unknown'
        }
    });
    displayFiles(data.files);

    // Display dependency graph
    displayDependencyGraph(data.dependency_graph);

    // Display language chart with a slight delay to ensure layout is ready
    setTimeout(() => {
        displayLanguageChart(data.files);
    }, 100);

    // Scroll to results
    // resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayProfileResults(data) {
    document.getElementById('profileAvatar').src = data.avatar_url;
    document.getElementById('profileName').textContent = data.name || data.username;
    document.getElementById('profileUsername').textContent = `@${data.username}`;
    document.getElementById('profileBio').textContent = data.bio || 'No bio available';

    document.getElementById('profileRepos').textContent = data.public_repos;
    document.getElementById('profileFollowers').textContent = data.followers;
    document.getElementById('profileFollowing').textContent = data.following;

    // Summary
    const summaryDiv = document.getElementById('profileSummary');
    const summarySection = document.getElementById('profileSummarySection');

    if (data.summary) {
        summaryDiv.innerHTML = marked.parse(data.summary);
        summarySection.style.display = 'block';
    } else {
        summarySection.style.display = 'none';
    }

    welcomeState.style.display = 'none';
    profileResultsDiv.style.display = 'block';

    addToHistory({
        type: 'profile',
        value: data.username,
        meta: {
            repos: data.public_repos,
            followers: data.followers,
            avatar: data.avatar_url
        }
    });

    displayTopRepos(data.top_repos);

    setTimeout(() => {
        displayProfileLanguageChart(data.languages);
    }, 100);

    // profileResultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayTopRepos(repos) {
    const list = document.getElementById('topReposList');
    list.innerHTML = '';

    if (!repos || repos.length === 0) {
        list.innerHTML = '<div style="text-align:center; padding: 2rem; color: var(--text-secondary);">No public repositories found</div>';
        return;
    }

    repos.forEach(repo => {
        const item = document.createElement('div');
        item.className = 'repo-item';
        item.style.cursor = 'pointer';

        item.onclick = () => {
            setMode('repo');
            repoUrlInput.value = repo.url;
            handleSubmit({ preventDefault: () => { } });
        };

        item.innerHTML = `
            <div class="repo-header">
                <span class="repo-name">${repo.name}</span>
                <span class="repo-meta">⭐ ${repo.stars}</span>
            </div>
            <div class="repo-desc">${repo.description || 'No description'}</div>
            <div class="repo-meta">
                <span class="file-lang">${repo.language || 'Unknown'}</span>
                <span class="repo-stat">🔌 ${repo.forks} forks</span>
            </div>
        `;
        list.appendChild(item);
    });
}

function displayProfileLanguageChart(languages) {
    const canvas = document.getElementById('profileLangChart');
    const ctx = canvas.getContext('2d');

    // Clear previous chart if any (though we are recreating canvas context, Chart.js handles it)
    if (window.profileChartInstance) {
        window.profileChartInstance.destroy();
    }

    const sortedLangs = Object.entries(languages)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    if (sortedLangs.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No language data', canvas.width / 2, canvas.height / 2);
        return;
    }

    const labels = sortedLangs.map(l => l[0]);
    const values = sortedLangs.map(l => l[1]);

    window.profileChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe',
                    '#10b981', '#34d399', '#6ee7b7', '#a7f3d0',
                    '#f59e0b', '#fbbf24'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94a3b8',
                        font: { family: "'Outfit', sans-serif" }
                    }
                }
            }
        }
    });
}

function displayFiles(files) {
    const filesList = document.getElementById('filesList');
    filesList.innerHTML = '';

    if (!files || files.length === 0) {
        filesList.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No files found</p>';
        return;
    }

    // Sort files by path
    const sortedFiles = [...files].sort((a, b) => a.path.localeCompare(b.path));

    sortedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const filePath = document.createElement('div');
        filePath.className = 'file-path';
        filePath.textContent = file.path;
        filePath.title = file.path; // Tooltip

        const fileMeta = document.createElement('div');
        fileMeta.className = 'file-meta';

        const fileLang = document.createElement('span');
        fileLang.className = 'file-lang';
        fileLang.textContent = file.language;

        const fileSize = document.createElement('span');
        fileSize.className = 'file-size';
        fileSize.textContent = formatBytes(file.size);

        fileMeta.appendChild(fileLang);
        fileMeta.appendChild(fileSize);

        fileItem.appendChild(filePath);
        fileItem.appendChild(fileMeta);

        filesList.appendChild(fileItem);
    });
}

function displayDependencyGraph(graph) {
    const depGraph = document.getElementById('depGraph');
    depGraph.innerHTML = '';

    if (!graph || Object.keys(graph).length === 0) {
        depGraph.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No dependencies found</p>';
        return;
    }

    const filesWithDeps = Object.entries(graph).filter(([_, deps]) => deps && deps.length > 0);

    if (filesWithDeps.length === 0) {
        depGraph.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No dependencies found</p>';
        return;
    }

    filesWithDeps.sort((a, b) => a[0].localeCompare(b[0]));

    filesWithDeps.forEach(([file, deps]) => {
        const treeNode = renderDependencyTreeNode(file, deps, graph, new Set([file]), 0);
        depGraph.appendChild(treeNode);
    });
}

function renderDependencyTreeNode(fileName, dependencies, fullGraph, visited, depth) {
    const container = document.createElement('div');
    container.className = 'tree-node';

    // Stop recursion if too deep or no dependencies
    if (depth > 5 || !dependencies || dependencies.length === 0) {
        const leaf = document.createElement('div');
        leaf.className = 'tree-leaf';
        leaf.innerHTML = `<span class="file-icon">📄</span> <span class="file-name">${fileName}</span>`;
        container.appendChild(leaf);
        return container;
    }

    const details = document.createElement('details');

    const summary = document.createElement('summary');
    summary.className = 'tree-summary';
    summary.innerHTML = `<span class="file-icon">📁</span> <span class="file-name">${fileName}</span> <span class="dep-count">(${dependencies.length})</span>`;

    const content = document.createElement('div');
    content.className = 'tree-content';

    dependencies.forEach(depPath => {
        // Avoid cycles
        if (visited.has(depPath)) {
            const cycleNode = document.createElement('div');
            cycleNode.className = 'tree-leaf cycle';
            cycleNode.innerHTML = `<span class="file-icon">🔄</span> <span class="file-name">${depPath}</span>`;
            content.appendChild(cycleNode);
            return;
        }

        const newVisited = new Set(visited);
        newVisited.add(depPath);

        const childDeps = fullGraph[depPath] || [];
        const childNode = renderDependencyTreeNode(depPath, childDeps, fullGraph, newVisited, depth + 1);
        content.appendChild(childNode);
    });

    details.appendChild(summary);
    details.appendChild(content);
    container.appendChild(details);

    return container;
}

function displayLanguageChart(files) {
    const canvas = document.getElementById('langChart');
    const ctx = canvas.getContext('2d');

    if (window.repoChartInstance) {
        window.repoChartInstance.destroy();
    }

    // Count languages
    const langCounts = {};
    files.forEach(file => {
        const lang = file.language;
        langCounts[lang] = (langCounts[lang] || 0) + 1;
    });

    // Sort by count
    const sortedLangs = Object.entries(langCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Top 10 languages

    if (sortedLangs.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No data', canvas.width / 2, canvas.height / 2);
        return;
    }

    const labels = sortedLangs.map(l => l[0]);
    const values = sortedLangs.map(l => l[1]);

    window.repoChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe',
                    '#10b981', '#34d399', '#6ee7b7', '#a7f3d0',
                    '#f59e0b', '#fbbf24', '#f43f5e', '#ec4899'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94a3b8',
                        font: { family: "'Outfit', sans-serif" }
                    }
                }
            }
        }
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// History Management
function addToHistory(item) {
    let history = JSON.parse(localStorage.getItem('app_history') || '[]');

    // Remove duplicates
    history = history.filter(h => h.value !== item.value);

    // Add new item to top
    item.timestamp = Date.now();
    history.unshift(item);

    // Limit to 20 items
    if (history.length > 20) history.pop();

    localStorage.setItem('app_history', JSON.stringify(history));
}

function renderHistory() {
    const history = JSON.parse(localStorage.getItem('app_history') || '[]');
    historyList.innerHTML = '';

    if (history.length === 0) {
        historyList.innerHTML = '<div style="text-align:center; padding: 2rem; color: var(--text-secondary);">No history found</div>';
        return;
    }

    history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'repo-item'; // Reuse repo-item style
        div.style.cursor = 'pointer';

        const date = new Date(item.timestamp).toLocaleString();
        const icon = item.type === 'repo' ? '📦' : '👤';
        const typeLabel = item.type === 'repo' ? 'Repository' : 'Profile';

        div.onclick = () => {
            setMode(item.type);
            repoUrlInput.value = item.value;
            handleSubmit({ preventDefault: () => { } });
        };

        div.innerHTML = `
            <div class="repo-header">
                <span class="repo-name">${icon} ${item.value}</span>
                <span class="repo-meta">${date}</span>
            </div>
            <div class="repo-desc">${typeLabel} Analysis</div>
        `;

        historyList.appendChild(div);
    });
}

function clearHistory() {
    localStorage.removeItem('app_history');
    renderHistory();
}

// Auth Logic
function updateAuthUI() {
    if (currentUser) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'flex';

        if (currentUser.role === 'hr') {
            profileNavBtn.style.display = 'flex';
        } else {
            profileNavBtn.style.display = 'none';
        }
    } else {
        loginBtn.style.display = 'flex';
        logoutBtn.style.display = 'none';
        profileNavBtn.style.display = 'none';

        // If current mode is profile, switch to repo
        if (currentMode === 'profile') {
            setMode('repo');
        }
    }
}

function showAuthModal() {
    authModal.style.display = 'flex';
    setAuthMode(true);
}

function closeAuthModal() {
    authModal.style.display = 'none';
    authForm.reset();
}

function setAuthMode(isLogin) {
    isLoginMode = isLogin;
    if (isLogin) {
        authTitle.textContent = 'Login';
        authSubmitText.textContent = 'Login';
        authSwitchText.textContent = "Don't have an account?";
        authSwitchLink.textContent = 'Sign Up';
        emailGroup.style.display = 'none';
        document.getElementById('email').required = false;
    } else {
        authTitle.textContent = 'Sign Up';
        authSubmitText.textContent = 'Sign Up';
        authSwitchText.textContent = "Already have an account?";
        authSwitchLink.textContent = 'Login';
        emailGroup.style.display = 'flex';
        document.getElementById('email').required = true;
    }
}

async function handleAuth(e) {
    e.preventDefault();

    const formData = new FormData(authForm);
    const data = Object.fromEntries(formData.entries());

    authSubmitText.textContent = 'Please wait...';

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
                const err = await response.json();
                throw new Error(err.detail || 'Login failed');
            }

            const result = await response.json();
            token = result.access_token;
            currentUser = result.user;

            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(currentUser));

            closeAuthModal();
            updateAuthUI();

        } else {
            // Signup
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Signup failed');
            }

            alert('Account created! Please login.');
            setAuthMode(true);
        }
    } catch (error) {
        alert(error.message);
    } finally {
        authSubmitText.textContent = isLoginMode ? 'Login' : 'Sign Up';
    }
}

function handleLogout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
}

// Intercept fetch to add token
const originalFetch = window.fetch;
window.fetch = async function (url, options = {}) {
    // Add token if available
    if (token) {
        options.headers = options.headers || {};
        if (options.headers instanceof Headers) {
            options.headers.append('Authorization', `Bearer ${token}`);
        } else {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    const response = await originalFetch(url, options);

    // Handle 401
    if (response.status === 401) {
        handleLogout();
        // showAuthModal();
        window.location.href = '/login';
    }

    return response;
};

// Initialize
updateAuthUI();

// Auth Listeners
// loginBtn.addEventListener('click', showAuthModal);
logoutBtn.addEventListener('click', handleLogout);
closeModalBtn.addEventListener('click', closeAuthModal);
authSwitchLink.addEventListener('click', (e) => {
    e.preventDefault();
    setAuthMode(!isLoginMode);
});
authForm.addEventListener('submit', handleAuth);
authModal.addEventListener('click', (e) => {
    if (e.target === authModal) closeAuthModal();
});

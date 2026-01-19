document.addEventListener('DOMContentLoaded', () => {
    const settingsView = document.getElementById('settings-view');
    const messagesView = document.getElementById('messages-view');

    const urlInput = document.getElementById('url');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const apiTokenInput = document.getElementById('api-token');
    const loginButton = document.getElementById('login-btn');
    const saveButton = document.getElementById('save-btn');
    const settingsError = document.getElementById('settings-error');

    const messageList = document.getElementById('message-list');
    const visitButton = document.getElementById('visit-btn');
    const settingsButton = document.getElementById('settings-btn');
    const refreshButton = document.getElementById('refresh-btn');

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    let activeTab = 'creds';

    let messages = []; // In-memory cache for messages

    // Replace chrome.storage with localStorage
    const storage = {
        get: (keys, callback) => {
            const result = {};
            keys.forEach(key => {
                const value = localStorage.getItem(key);
                try {
                    result[key] = value ? JSON.parse(value) : undefined;
                } catch (e) {
                    result[key] = value;
                }
            });
            callback(result);
        },
        set: (obj, callback) => {
            Object.keys(obj).forEach(key => {
                localStorage.setItem(key, JSON.stringify(obj[key]));
            });
            if (callback) callback();
        }
    };

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            activeTab = btn.dataset.tab;
            document.getElementById(`tab-${activeTab}`).classList.add('active');
        });
    });

    function showView(viewId) {
        settingsView.classList.remove('active');
        messagesView.classList.remove('active');
        document.getElementById(viewId).classList.add('active');
    }

    function initializeView() {
        storage.get(['serverUrl', 'authToken', 'loggedIn', 'username'], (result) => {
            if (result.serverUrl) urlInput.value = result.serverUrl;
            if (result.username && result.username !== 'API User') usernameInput.value = result.username;
            if (result.authToken) apiTokenInput.value = result.authToken;

            if (result.loggedIn && result.serverUrl && result.authToken) {
                showView('messages-view');
                loadMessages();
            } else {
                showView('settings-view');
            }
        });
    }

    initializeView();

    function getLoginPayload() {
        const serverUrl = urlInput.value.replace(/\/$/, "");
        if (!serverUrl) {
            settingsError.textContent = 'Server URL is required';
            return null;
        }

        let payload = { url: serverUrl };
        let isValid = false;

        if (activeTab === 'creds') {
            const username = usernameInput.value;
            const password = passwordInput.value;
            if (username && password) {
                payload.username = username;
                payload.password = password;
                isValid = true;
            } else {
                settingsError.textContent = 'Username and Password are required';
            }
        } else {
            const token = apiTokenInput.value;
            if (token) {
                payload.token = token;
                isValid = true;
            } else {
                settingsError.textContent = 'API Token is required';
            }
        }
        return isValid ? payload : null;
    }

    async function apiLogin(payload) {
        try {
            const response = await fetch(`${payload.url}/api/token/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: payload.username,
                    password: payload.password
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }
            const data = await response.json();
            return { token: data.token, username: payload.username };
        } catch (error) {
            throw new Error(error.message);
        }
    }

    loginButton.addEventListener('click', async () => {
        const payload = getLoginPayload();
        if (payload) {
            settingsError.textContent = 'Logging in...';
            loginButton.disabled = true;
            saveButton.disabled = true;

            try {
                let token, username;
                if (payload.token) { // API Token login
                    token = payload.token;
                    username = 'API User';
                } else { // Credentials login
                    const result = await apiLogin(payload);
                    token = result.token;
                    username = result.username;
                }

                storage.set({
                    serverUrl: payload.url,
                    authToken: token,
                    username: username,
                    loggedIn: true
                }, () => {
                    showView('messages-view');
                    loadMessages();
                    settingsError.textContent = '';
                    passwordInput.value = '';
                });

            } catch (error) {
                settingsError.textContent = error.message;
            } finally {
                loginButton.disabled = false;
                saveButton.disabled = false;
            }
        }
    });

    saveButton.addEventListener('click', () => {
        const payload = getLoginPayload();
        if (payload) {
            if (activeTab === 'creds') {
                settingsError.textContent = "Cannot save credentials without logging in. Use 'Login & Test'.";
                return;
            }

            // For Token, we can save directly.
            storage.set({
                serverUrl: payload.url,
                authToken: payload.token,
                username: 'API User',
                loggedIn: true
            }, () => {
                showView('messages-view');
                loadMessages();
                settingsError.textContent = '';
            });
        }
    });

    settingsButton.addEventListener('click', () => {
        showView('settings-view');
        passwordInput.value = '';
    });

    refreshButton.addEventListener('click', () => {
        loadMessages();
    });

    visitButton.addEventListener('click', () => {
        storage.get(['serverUrl'], (result) => {
            if (result.serverUrl) {
                window.open(`${result.serverUrl}/console/`, '_blank');
            }
        });
    });

    async function checkMessages() {
        return new Promise((resolve, reject) => {
            storage.get(['serverUrl', 'authToken', 'loggedIn'], async (result) => {
                if (!result.loggedIn || !result.serverUrl || !result.authToken) {
                    return reject(new Error('Not logged in.'));
                }

                try {
                    const response = await fetch(`${result.serverUrl}/api/messages/`, {
                        headers: { 'Authorization': `Token ${result.authToken}` }
                    });

                    if (response.status === 401) {
                         storage.set({ loggedIn: false });
                         showView('settings-view');
                         settingsError.textContent = 'Authentication failed. Please login again.';
                         return reject(new Error('Unauthorized'));
                    }
                    if (!response.ok) throw new Error('Failed to fetch messages.');

                    const fetchedMessages = await response.json();
                    messages = fetchedMessages.results; // Assuming pagination
                    renderMessages(messages);
                    resolve({ success: true });

                } catch (error) {
                    renderError(error.message);
                    reject({ success: false, error: error.message });
                }
            });
        });
    }

    async function loadMessages() {
        refreshButton.disabled = true;
        refreshButton.textContent = '...';
        try {
            await checkMessages();
        } catch (e) {
            // Error is rendered by checkMessages
        } finally {
            refreshButton.disabled = false;
            refreshButton.textContent = 'Refresh';
        }
    }

    function renderError(error) {
        messageList.innerHTML = `<li style="justify-content: center; color: red;">${error}</li>`;
    }

    function renderMessages(msgs) {
        messageList.innerHTML = '';
        if (!msgs || msgs.length === 0) {
            messageList.innerHTML = '<li style="justify-content: center; color: #888;">No messages</li>';
            return;
        }

        msgs.sort((a, b) => {
            if (a.read === b.read) { return new Date(b.created) - new Date(a.created); }
            return a.read ? 1 : -1;
        });

        storage.get(['serverUrl'], (result) => {
            const serverUrl = result.serverUrl;
            msgs.forEach(msg => {
                const li = document.createElement('li');
                li.className = msg.read ? '' : 'unread';
                li.style.cursor = 'pointer';

                li.addEventListener('click', () => {
                    if (serverUrl) {
                        window.open(`${serverUrl}/console/${msg.id}`, '_blank');
                        if (!msg.read) {
                            markAsRead([msg.id]);
                            msg.read = true; // Optimistic update
                            renderMessages(messages);
                        }
                    }
                });

                const contentDiv = document.createElement('div');
                contentDiv.style.flex = '1';
                const subjectDiv = document.createElement('div');
                subjectDiv.style.fontWeight = msg.read ? 'normal' : 'bold';
                subjectDiv.textContent = msg.subject || '(No Subject)';
                contentDiv.appendChild(subjectDiv);
                li.appendChild(contentDiv);
                messageList.appendChild(li);
            });
        });
    }

    function markAsRead(messageIds) {
        storage.get(['serverUrl', 'authToken'], async (result) => {
            if (!result.serverUrl || !result.authToken) return;
            try {
                await fetch(`${result.serverUrl}/api/messages/read/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Token ${result.authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ids: messageIds })
                });
            } catch (e) {
                console.error("Failed to mark as read:", e);
            }
        });
    }

    // Initial load
    initializeView();
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/pwa/sw.js').then(registration => {
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, err => {
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}

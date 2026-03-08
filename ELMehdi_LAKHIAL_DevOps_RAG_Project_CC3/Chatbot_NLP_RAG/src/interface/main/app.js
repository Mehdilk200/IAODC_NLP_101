
const API_BASE   = 'http://0.0.0.0:8000';
const LOGIN_PAGE = 'login.html';

const Auth = {
    getSession() { try { return JSON.parse(localStorage.getItem('ragiso_session')); } catch { return null; } },
    getToken()   { return localStorage.getItem('ragiso_token') || ''; },
    getRole()    { return this.getSession()?.role || 'admin'; },
    getEmail()   { return this.getSession()?.email || 'User'; },
    headers()    { return { 'Authorization': `Bearer ${this.getToken()}`, 'Content-Type': 'application/json' }; },
    logout()     { localStorage.removeItem('ragiso_session'); localStorage.removeItem('ragiso_token'); window.location.href = LOGIN_PAGE; },
    guard()      {
        const s = this.getSession();
        if (!s?.token) { window.location.href = LOGIN_PAGE; return false; }
        return true;
    }
};

let conversations    = [];
let activeConvId     = null;
let activeConvTitle  = '';
let idLoad           = Auth.getRole(); 


function showToast(msg, type = 'info') {
    const t  = document.getElementById('toast');
    const ic = document.getElementById('toastIcon');
    document.getElementById('toastMsg').textContent = msg;
    t.className = `toast ${type} show`;
    ic.className = type === 'success' ? 'fa-solid fa-circle-check'
                 : type === 'error'   ? 'fa-solid fa-circle-exclamation'
                 :                      'fa-solid fa-circle-info';
    clearTimeout(t._t);
    t._t = setTimeout(() => t.classList.remove('show'), 3500);
}

function fmtDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    const now = new Date();
    const diff = (now - d) / 1000;
    if (diff < 60)    return 'just now';
    if (diff < 3600)  return Math.floor(diff/60) + 'm ago';
    if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
    return d.toLocaleDateString();
}

function formatContent(text = "") {
    if (!text) return "";
    text = text.replace(
        /(Source Evidence\s*\n)([\s\S]*?)(?=\n\n|$)/gi,
        (_, __, body) => {
            const items = body
                .split("\n")
                .filter(Boolean)
                .map(l => `<div class="src-item">${l.replace(/^\*\s*/, "")}</div>`)
                .join("");

            return `<div class="src-block">
                <span class="src-title">📎 Source Evidence</span>
                ${items}
            </div>`;
        }
    );

    return marked.parse(text);
}
async function apiGet(path) {
    const r = await fetch(API_BASE + path, { headers: Auth.headers() });
    if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
    return r.json();
}

async function apiPost(path, body) {
    const r = await fetch(API_BASE + path, {
        method: 'POST',
        headers: Auth.headers(),
        body: JSON.stringify(body)
    });
    if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail || `POST ${path} → ${r.status}`);
    }
    return r.json();
}

async function loadConversations() {
    try {
        const data = await apiGet('/conversations');
        conversations = data.items || [];
        renderConvList(conversations);
    } catch (err) {
        console.error(err);
        showToast('Could not load conversations', 'error');
    }
}

function renderConvList(list) {
    const wrap  = document.getElementById('convListWrap');
    const empty = document.getElementById('convEmpty');

    wrap.querySelectorAll('.conv-item, .conv-group-label').forEach(el => el.remove());

    if (!list.length) { empty.style.display = 'block'; return; }
    empty.style.display = 'none';

    const today = new Date().toDateString();
    const groups = { Today: [], Earlier: [] };
    list.forEach(c => {
        const d = new Date(c.updated_at || c.created_at);
        (d.toDateString() === today ? groups.Today : groups.Earlier).push(c);
    });

    Object.entries(groups).forEach(([label, items]) => {
        if (!items.length) return;
        const gl = document.createElement('div');
        gl.className = 'conv-group-label';
        gl.textContent = label;
        wrap.appendChild(gl);

        items.forEach(c => {
            const el = document.createElement('div');
            el.className = 'conv-item' + (c.id === activeConvId ? ' active' : '');
            el.dataset.id = c.id;
            el.innerHTML = `
                <div class="conv-item-icon"><i class="fa-regular fa-comment"></i></div>
                <div class="conv-item-info">
                    <div class="conv-item-title">${escHtml(c.title)}</div>
                    <div class="conv-item-date">${fmtDate(c.updated_at || c.created_at)}</div>
                </div>
                <button class="conv-delete" title="Delete" data-id="${c.id}">
                    <i class="fa-solid fa-xmark"></i>
                </button>`;
            el.addEventListener('click', (e) => {
                if (e.target.closest('.conv-delete')) return;
                selectConversation(c.id, c.title);
            });
            el.querySelector('.conv-delete').addEventListener('click', async (e) => {
            e.stopPropagation();
            
            const btn = e.currentTarget;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            btn.disabled = true;

            try {
                const r = await fetch(`${API_BASE}/conversations/${c.id}`, {
                    method: 'DELETE',
                    headers: Auth.headers()
                });
                
                // debug — chuf wach kayrja3
                console.log('DELETE status:', r.status);
                const body = await r.json().catch(() => ({}));
                console.log('DELETE response:', body);

                if (!r.ok) throw new Error(body.detail || `Error ${r.status}`);

                conversations = conversations.filter(x => x.id !== c.id);
                if (activeConvId === c.id) {
                    activeConvId = null;
                    showWelcome();
                }
                renderConvList(conversations);
                showToast('Conversation deleted ', 'success');

            } catch(err) {
                console.error('Delete failed:', err);
                btn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
                btn.disabled = false;
                showToast('Could not delete: ' + err.message, 'error');
            }
        });
            wrap.appendChild(el);
        });
    });
}

async function selectConversation(id, title) {
    activeConvId    = id;
    activeConvTitle = title;
    document.querySelectorAll('.conv-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === id);
    });

    const titleEl = document.getElementById('convTitleDisplay');
    titleEl.textContent = title;
    titleEl.classList.remove('placeholder');

    showChatView();
    clearMessages();
    showTyping(true);

    try {
        const data = await apiGet(`/conversations/${id}/messages`);
        showTyping(false);
        const msgs = data.items || [];
        if (!msgs.length) {
            appendSystemMsg('No messages yet. Ask your first question!');
        } else {
            msgs.forEach(m => {
                const isUser = m.role !== 'assent' && m.role !== 'assistant';
                appendMessage(isUser ? 'user' : 'assistant', m.content, false);
            });
        }
        scrollBottom();
    } catch (err) {
        showTyping(false);
        showToast('Could not load messages: ' + err.message, 'error');
    }
}
async function sendMessage() {
    const input = document.getElementById('msgInput');
    const text  = input.value.trim();
    if (!text || !activeConvId) return;

    const sendBtn = document.getElementById('sendBtn');
    sendBtn.classList.add('loading');
    sendBtn.disabled = true;

    appendMessage('user', text, true);
    input.value = '';
    document.getElementById('charCount').textContent = '0/3000';
    input.style.height = 'auto';
    showTyping(true);
    scrollBottom();

    try {
        // POST /conversations/{id}/messages/
        const data = await apiPost(`/conversations/${activeConvId}/messages/`, { content: text });
        showTyping(false);
        const answer = data.answer || data.content || 'No response received.';
        appendMessage('assistant', answer, true);
        scrollBottom();

        const conv = conversations.find(c => c.id === activeConvId);
        if (conv) {
            conv.updated_at = new Date().toISOString();
            renderConvList(conversations);
        }
    } catch (err) {
        showTyping(false);
        appendMessage('assistant', '⚠️ Error: ' + err.message, true);
        showToast(err.message, 'error');
    } finally {
        sendBtn.classList.remove('loading');
        sendBtn.disabled = false;
        input.focus();
    }
}

async function createConversation(title) {
    try {
        const data = await apiPost('/conversations', { title });
        const newConv = { id: data.id, title: data.title, created_at: new Date().toISOString(), updated_at: new Date().toISOString() };
        conversations.unshift(newConv);
        renderConvList(conversations);
        selectConversation(newConv.id, newConv.title);
        showToast('Conversation created!', 'success');
    } catch (err) {
        showToast('Could not create conversation: ' + err.message, 'error');
    }
}

function showWelcome() {
    document.getElementById('welcomeSection').style.display = '';
    document.getElementById('chatView').classList.remove('visible');
    const t = document.getElementById('convTitleDisplay');
    t.textContent = 'Select or create a conversation';
    t.classList.add('placeholder');
}

function showChatView() {
    document.getElementById('welcomeSection').style.display = 'none';
    document.getElementById('chatView').classList.add('visible');
}

function clearMessages() {
    const area = document.getElementById('messagesArea');
    area.querySelectorAll('.msg, .sys-msg').forEach(el => el.remove());
}

function appendMessage(role, content, animate = true) {
    const area   = document.getElementById('messagesArea');
    const typing = document.getElementById('typingIndicator');

    const wrap = document.createElement('div');
    wrap.className = `msg ${role}`;
    if (animate) wrap.style.animation = 'slideDown .3s ease';

    const initials = role === 'user'
        ? (Auth.getEmail()[0] || 'U').toUpperCase()
        : 'AI';

    wrap.innerHTML = `
        <div class="msg-avatar">${initials}</div>
        <div class="msg-content">
            <div class="msg-bubble">${formatContent(content)}</div>
            <div class="msg-time">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>
        </div>`;

    area.insertBefore(wrap, typing);
}

function appendSystemMsg(text) {
    const area  = document.getElementById('messagesArea');
    const el    = document.createElement('div');
    el.className = 'sys-msg';
    el.style.cssText = 'text-align:center;color:var(--text-light);font-size:12px;padding:12px 0;';
    el.textContent = text;
    area.insertBefore(el, document.getElementById('typingIndicator'));
}

function showTyping(show) {
    document.getElementById('typingIndicator').classList.toggle('show', show);
}

function scrollBottom() {
    const area = document.getElementById('messagesArea');
    area.scrollTop = area.scrollHeight;
}

function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

document.getElementById('convSearch').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    const filtered = conversations.filter(c => c.title.toLowerCase().includes(q));
    renderConvList(filtered);
});

const modal      = document.getElementById('newConvModal');
const modalInput = document.getElementById('newConvTitle');

document.getElementById('newConvBtn').addEventListener('click', () => {
    modalInput.value = '';
    modal.classList.add('show');
    setTimeout(() => modalInput.focus(), 100);
});
document.getElementById('modalCancel').addEventListener('click', () => modal.classList.remove('show'));
modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('show'); });
document.getElementById('modalConfirm').addEventListener('click', () => {
    const title = modalInput.value.trim();
    if (!title) { modalInput.style.borderColor = '#ef4444'; return; }
    modal.classList.remove('show');
    createConversation(title);
});
modalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('modalConfirm').click();
});

document.getElementById('sendBtn').addEventListener('click', sendMessage);

document.getElementById('msgInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

document.getElementById('msgInput').addEventListener('input', function() {
    document.getElementById('charCount').textContent = `${this.value.length}/3000`;
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 180) + 'px';
});

const textarea = document.getElementById('msgInput');
const glow     = document.getElementById('chatGlow');
textarea.addEventListener('focus', () => glow.classList.add('focused'));
textarea.addEventListener('blur',  () => glow.classList.remove('focused'));

document.getElementById('clearBtn').addEventListener('click', () => {
    if (!activeConvId) return;
    clearMessages();
    appendSystemMsg('Chat cleared locally. Messages still saved on server.');
});

let isDark = localStorage.getItem('theme') === 'dark';
function applyTheme() {
    document.body.classList.toggle('dark-mode', isDark);
    document.getElementById('themeToggleIcon').className =
        isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}
document.getElementById('themeToggleIcon').addEventListener('click', () => {
    isDark = !isDark;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    applyTheme();
});

document.getElementById('logoutBtn').addEventListener('click', () => Auth.logout());

function renderUserInfo() {
    const session = Auth.getSession();
    if (!session) return;
    document.getElementById('userNameDisplay').textContent = session.email || 'User';
    document.getElementById('userRoleDisplay').textContent = session.role  || 'user';
    idLoad = session.role || 'admin';
    document.getElementById('idLoadLabel').textContent = idLoad;
}

document.addEventListener('DOMContentLoaded', () => {
    if (!Auth.guard()) return;  

    applyTheme();
    renderUserInfo();
    loadConversations();

    if (typeof lucide !== 'undefined') lucide.createIcons();
});
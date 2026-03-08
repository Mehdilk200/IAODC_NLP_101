
const API_BASE   = 'http://0.0.0.0:8000';
const LOGIN_PAGE = 'login.html';

const Auth = {
    getSession() { try { return JSON.parse(localStorage.getItem('ragiso_session')); } catch { return null; } },
    getToken()   { return localStorage.getItem('ragiso_token') || ''; },
    getRole()    { return this.getSession()?.role || 'user'; },
    getEmail()   { return this.getSession()?.email || ''; },
    getUserId()  { return this.getSession()?.userId || ''; },
    headers()    { return { 'Authorization': `Bearer ${this.getToken()}`, 'Content-Type': 'application/json' }; },
    guard()      { if (!this.getSession()?.token) { window.location.href = LOGIN_PAGE; return false; } return true; }
};

let allFiles  = [];
let allUsers  = [];
let currentFilter    = 'mine';
let currentView      = 'grid';
let uploadedFileName = null;   
let uploadedIdLoad   = null;   
let isDark = localStorage.getItem('theme') === 'dark';

const Store = {
    filesKey()  { return 'ragiso_files_'  + (Auth.getSession()?.userId || 'anon'); },
    usersKey()  { return 'ragiso_users_'  + (Auth.getSession()?.userId || 'anon'); },

    saveFiles(files)  { try { localStorage.setItem(this.filesKey(),  JSON.stringify(files));  } catch{} },
    loadFiles()       { try { return JSON.parse(localStorage.getItem(this.filesKey()))  || []; } catch { return []; } },

    saveUsers(users)  { try { localStorage.setItem(this.usersKey(),  JSON.stringify(users));  } catch{} },
    loadUsers()       { try { return JSON.parse(localStorage.getItem(this.usersKey()))  || []; } catch { return []; } },
};

function showToast(msg, type='info') {
    const t = document.getElementById('toast');
    document.getElementById('toastMsg').textContent = msg;
    t.className = `toast ${type} show`;
    document.getElementById('toastIcon').className =
        type==='success' ? 'fa-solid fa-circle-check' :
        type==='error'   ? 'fa-solid fa-circle-exclamation' :
                           'fa-solid fa-circle-info';
    clearTimeout(t._t);
    t._t = setTimeout(() => t.classList.remove('show'), 3500);
}

function fmtDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('en-GB', {day:'2-digit',month:'short',year:'numeric'}) +
           ' · ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}

function fmtSize(bytes) {
    if (!bytes) return '—';
    if (bytes < 1024)      return bytes + ' B';
    if (bytes < 1048576)   return (bytes/1024).toFixed(1) + ' KB';
    return (bytes/1048576).toFixed(2) + ' MB';
}

function fileColor(name) {
    if (!name) return { bg:'#f1f5f9', color:'#64748b', icon:'fa-regular fa-file' };
    const ext = name.split('.').pop().toLowerCase();
    if (['pdf'].includes(ext))               return { bg:'#fee2e2', color:'#ef4444', icon:'fa-regular fa-file-pdf' };
    if (['xls','xlsx','csv'].includes(ext))  return { bg:'#dcfce7', color:'#22c55e', icon:'fa-regular fa-file-excel' };
    if (['doc','docx'].includes(ext))        return { bg:'#dbeafe', color:'#3b82f6', icon:'fa-regular fa-file-word' };
    if (['pptx','ppt'].includes(ext))        return { bg:'#ffedd5', color:'#f97316', icon:'fa-regular fa-file-powerpoint' };
    if (['txt','md'].includes(ext))          return { bg:'#f1f5f9', color:'#64748b', icon:'fa-regular fa-file-lines' };
    return { bg:'#f1f5f9', color:'#94a3b8', icon:'fa-regular fa-file' };
}

function fileType(name) {
    if (!name) return 'other';
    const ext = name.split('.').pop().toLowerCase();
    if (['pdf'].includes(ext)) return 'pdf';
    if (['xls','xlsx','csv'].includes(ext)) return 'excel';
    if (['doc','docx'].includes(ext)) return 'word';
    return 'other';
}

async function apiGet(path) {
    const r = await fetch(API_BASE + path, { headers: Auth.headers() });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
}

async function apiPost(path, body) {
    const r = await fetch(API_BASE + path, {
        method:'POST', headers: Auth.headers(), body: JSON.stringify(body)
    });
    if (!r.ok) { const e = await r.json().catch(()=>({})); throw new Error(e.detail || r.status); }
    return r.json();
}

async function apiPostForm(path, formData) {
    const r = await fetch(API_BASE + path, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${Auth.getToken()}` },
        body: formData
    });
    if (!r.ok) { const e = await r.json().catch(()=>({})); throw new Error(e.detail || r.status); }
    return r.json();
}

async function loadFiles() {

    allFiles = Store.loadFiles();
    updateCounts();
    renderFiles();

    try {
        const data = await apiGet('/files-metadata');
        allFiles = data.items || [];
        Store.saveFiles(allFiles);  
        updateCounts();
        renderFiles();
    } catch(e) {
        console.error('loadFiles:', e);
        showToast('Could not load files from server', 'error');
    }
}

async function loadUsers() {
    
    allUsers = Store.loadUsers();
    updateUserCounts();
    renderUsers();

    try {
        const data = await apiGet('/users');          
        allUsers = data.items || [];
        Store.saveUsers(allUsers);
        updateUserCounts();
        renderUsers();
    } catch(e) {
        console.error('loadUsers:', e);
        showToast('Could not load users: ' + e.message, 'error');
    }
}

function getFilteredFiles() {
    const role   = Auth.getRole();
    let files = [...allFiles];

    if (currentFilter === 'mine') {
        files = files.filter(f => f.id_load === role);
    }
    if (['pdf','excel','word','other'].includes(currentFilter)) {
        files = files.filter(f => fileType(f.file_name) === currentFilter);
    }
    if (currentFilter === 'ready')   files = files.filter(f => isReady(f));
    if (currentFilter === 'pending') files = files.filter(f => !isReady(f));

    const sort = document.getElementById('sortSelect').value;
    files.sort((a,b) => {
        if (sort === 'date_desc') return new Date(b.created_at||0) - new Date(a.created_at||0);
        if (sort === 'date_asc')  return new Date(a.created_at||0) - new Date(b.created_at||0);
        if (sort === 'name_asc')  return (a.file_name||'').localeCompare(b.file_name||'');
        if (sort === 'name_desc') return (b.file_name||'').localeCompare(a.file_name||'');
        if (sort === 'size_desc') return (b.size||0) - (a.size||0);
        return 0;
    });

    const q = document.getElementById('globalSearch').value.toLowerCase();
    if (q) files = files.filter(f => (f.file_name||'').toLowerCase().includes(q));

    return files;
}

function updateCounts() {
    const role = Auth.getRole();
    const isReady   = f => f.processed === true || f.processed === 1 || f.processed === 'true';
    const isPending = f => !isReady(f);

    document.getElementById('cntMine').textContent    = allFiles.filter(f => f.id_load === role).length;
    document.getElementById('cntAll').textContent     = allFiles.length;
    document.getElementById('cntPdf').textContent     = allFiles.filter(f=>fileType(f.file_name)==='pdf').length;
    document.getElementById('cntXls').textContent     = allFiles.filter(f=>fileType(f.file_name)==='excel').length;
    document.getElementById('cntDoc').textContent     = allFiles.filter(f=>fileType(f.file_name)==='word').length;
    document.getElementById('cntOther').textContent   = allFiles.filter(f=>fileType(f.file_name)==='other').length;
    document.getElementById('cntReady').textContent   = allFiles.filter(isReady).length;
    document.getElementById('cntPending').textContent = allFiles.filter(isPending).length;
    document.getElementById('tabCntFiles').textContent= allFiles.length;

    const totalBytes = allFiles.reduce((s,f)=>s+(f.size||0),0);
    document.getElementById('storageText').textContent = fmtSize(totalBytes) + ' used';
}

function updateUserCounts() {
    document.getElementById('tabCntUsers').textContent = allUsers.length;
}

function renderFiles() {
    const files = getFilteredFiles();
    const grid  = document.getElementById('mainGrid');
    const list  = document.getElementById('listRows');
    const empty = document.getElementById('emptyFiles');
    const qs    = document.getElementById('quickAccessSection');

    const qg = document.getElementById('quickGrid');
    const recent4 = [...allFiles].slice(0,4);
    qg.innerHTML = recent4.map(f => fileCardHtml(f, true)).join('');
    qs.style.display = recent4.length ? '' : 'none';

    document.getElementById('tabCntFiles').textContent = files.length;
    document.getElementById('recentLabel').textContent =
        currentFilter === 'mine' ? 'My Documents' :
        currentFilter === 'all'  ? 'All Documents' : 'Filtered Results';

    if (!files.length) {
        grid.innerHTML = ''; list.innerHTML = '';
        empty.style.display = ''; return;
    }
    empty.style.display = 'none';

    grid.innerHTML = files.map(f => fileCardHtml(f, false)).join('');
    list.innerHTML = files.map(f => listRowHtml(f)).join('');

    document.querySelectorAll('[data-process]').forEach(btn => {
        btn.addEventListener('click', () => openProcessModal(btn.dataset.process, btn.dataset.idload));
    });
}

const isReady = f => f.processed === true || f.processed === 1 || f.processed === 'true';

function fileCardHtml(f, small) {
    const fc    = fileColor(f.file_name);
    const name  = f.file_name || 'Unnamed';
    const ready = isReady(f);
    const badge = ready
        ? '<span class="proc-badge ready">Ready</span>'
        : '<span class="proc-badge pending">Pending</span>';
    return `
    <div class="file-card" title="${name}">
        ${badge}
        <button class="file-card-menu"><i class="fa-solid fa-ellipsis-vertical"></i></button>
        <div class="file-card-icon" style="background:${fc.bg}">
            <i class="${fc.icon}" style="color:${fc.color}"></i>
        </div>
        <div class="file-card-name">${escHtml(shortName(name))}</div>
        <div class="file-card-meta">${fmtDate(f.created_at).split('·')[0].trim()}</div>
    </div>`;
}

function listRowHtml(f) {
    const fc    = fileColor(f.file_name);
    const name  = f.file_name || 'Unnamed';
    const ready = isReady(f);
    const status = ready
        ? '<span class="proc-badge ready" style="position:static">Ready</span>'
        : '<span class="proc-badge pending" style="position:static">Pending</span>';
    return `
    <div class="list-row">
        <div class="list-name">
            <div class="list-icon" style="background:${fc.bg}">
                <i class="${fc.icon}" style="color:${fc.color}"></i>
            </div>
            <div>
                <div style="font-weight:600;font-size:13px">${escHtml(shortName(name,40))}</div>
                <div style="font-size:11px;color:var(--text-light)">${status}</div>
            </div>
        </div>
        <div style="font-size:12px;color:var(--text-light)">${escHtml(f.id_load||'—')}</div>
        <div style="font-size:12px;color:var(--text-light)">${fmtDate(f.created_at).split('·')[0].trim()}</div>
        <div style="font-size:12px">${fmtSize(f.size)}</div>
        <div class="list-row-actions">
            ${!ready
                ? `<button class="row-btn" data-process="${f.file_name||''}" data-idload="${f.id_load||''}"><i class="fa-solid fa-gears"></i> Process</button>`
                : '<span style="font-size:11px;color:#16a34a"><i class="fa-solid fa-circle-check"></i> RAG Ready</span>'
            }
        </div>
    </div>`;
}

function shortName(n, max=22) {
    if (n.length <= max) return n;
    const ext = n.includes('.') ? '.' + n.split('.').pop() : '';
    return n.substring(0, max - ext.length - 1) + '…' + ext;
}

function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderUsers() {
    const tbody = document.getElementById('usersTbody');
    const empty = document.getElementById('emptyUsers');
    const role  = Auth.getRole();

    let visible = allUsers;
    if (role === 'manager') visible = allUsers.filter(u => u.role === 'user' || u.id === Auth.getUserId());

    if (!visible.length) {
        tbody.innerHTML = ''; empty.style.display = ''; return;
    }
    empty.style.display = 'none';

    tbody.innerHTML = visible.map(u => {
        const init  = (u.email||'U')[0].toUpperCase();
        const rp    = `<span class="role-pill ${u.role||'user'}">${u.role||'user'}</span>`;
        const active= u.is_active !== false;
        return `<tr>
            <td>
                <div class="u-name">
                    <div class="u-avatar">${init}</div>
                    <div>
                        <div style="font-weight:600">${escHtml(u.email||'—')}</div>
                        <div class="u-email">${u.id ? u.id.substring(0,18)+'…' : '—'}</div>
                    </div>
                </div>
            </td>
            <td>${rp}</td>
            <td style="font-size:12px;color:var(--text-light)">${u.created_by ? u.created_by.substring(0,16)+'…' : 'System'}</td>
            <td>
                <span class="status-dot ${active?'on':'off'}"></span>
                <span style="font-size:12px">${active?'Active':'Inactive'}</span>
            </td>
            <td>
                <div class="list-row-actions">
                    <button class="row-btn danger" onclick="alert('Delete not yet supported by API')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>`;
    }).join('');
}

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const t = tab.dataset.tab;
        document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
        tab.classList.add('active');

        if (t === 'files') {
            document.getElementById('filesPanel').style.display = '';
            document.getElementById('usersPanel').classList.remove('active');
        } else {
            document.getElementById('filesPanel').style.display = 'none';
            document.getElementById('usersPanel').classList.add('active');
            loadUsers();
        }
    });
});

let usersFilterActive = 'all';

async function filterUsers(type, btn) {
    usersFilterActive = type;
    document.querySelectorAll('.user-filter-btn').forEach(b => b.classList.remove('active-filter'));
    btn.classList.add('active-filter');

    try {
        let endpoint = '/users';
        if (type === 'mine')    endpoint = '/users?created_by_me=true';
        else if (type !== 'all') endpoint = `/users?role_filter=${type}`;

        const data = await apiGet(endpoint);
        allUsers = data.items || [];
        updateUserCounts();
        renderUsers();
    } catch(e) {
        showToast('Filter failed: ' + e.message, 'error');
    }
}

function checkPermissions() {
    const role = Auth.getRole();
    if (role === 'user') {
        document.getElementById('usersTab').style.display    = 'none';
        document.getElementById('filterAll').style.display   = 'none';
    }
    if (role === 'manager') {
        
        document.getElementById('userFilterBtns').style.display = 'none';
    }
}

document.querySelectorAll('.filter-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.filter-item').forEach(x => x.classList.remove('active'));
        item.classList.add('active');
        currentFilter = item.dataset.filter;
        renderFiles();
    });
});
function clearFilters() {
    document.querySelectorAll('.filter-item').forEach(x => x.classList.remove('active'));
    document.querySelector('[data-filter="all"]').classList.add('active');
    currentFilter = 'all';
    renderFiles();
}

document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.view-btn').forEach(x => x.classList.remove('active'));
        btn.classList.add('active');
        currentView = btn.dataset.view;
        const grid = document.getElementById('mainGrid');
        const list = document.getElementById('mainList');
        if (currentView === 'grid') { grid.classList.remove('hidden'); list.classList.remove('active'); }
        else { grid.classList.add('hidden'); list.classList.add('active'); }
    });
});

document.getElementById('sortSelect').addEventListener('change', renderFiles);
document.getElementById('globalSearch').addEventListener('input', renderFiles);


function openModal(id)  { document.getElementById(id).classList.add('show'); }
function closeModal(id) {
    document.getElementById(id).classList.remove('show');
    if (id === 'uploadModal') resetUploadModal();
}
document.querySelectorAll('.modal-overlay').forEach(m => {
    m.addEventListener('click', e => { if (e.target === m) closeModal(m.id); });
});

document.getElementById('uploadBtn').addEventListener('click', () => {
    
    document.getElementById('idLoadSelect').value = Auth.getRole();
    openModal('uploadModal');
});

const fileInput = document.getElementById('fileInput');
const dropZone  = document.getElementById('dropZone');

fileInput.addEventListener('change', () => handleFileSelect(fileInput.files[0]));
dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
    e.preventDefault(); dropZone.classList.remove('drag-over');
    handleFileSelect(e.dataTransfer.files[0]);
});

function handleFileSelect(file) {
    if (!file) return;
    const fc = fileColor(file.name);
    document.getElementById('sfIcon').innerHTML = `<i class="${fc.icon}" style="color:${fc.color};font-size:20px"></i>`;
    document.getElementById('sfIcon').style.background = fc.bg;
    document.getElementById('sfName').textContent = file.name;
    document.getElementById('sfSize').textContent = fmtSize(file.size);
    document.getElementById('selectedFile').classList.add('show');
    dropZone.style.display = 'none';
}

function clearFile() {
    fileInput.value = '';
    document.getElementById('selectedFile').classList.remove('show');
    dropZone.style.display = '';
}

function resetUploadModal() {
    clearFile();
    document.getElementById('step1').style.display = '';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('uploadProgress').classList.remove('show');
    document.getElementById('progressLabel').textContent = 'Uploading…';
    document.getElementById('uploadActionLabel').textContent = 'Upload';
    document.getElementById('uploadActionBtn').querySelector('i').className = 'fa-solid fa-cloud-arrow-up';
    document.getElementById('uploadActionBtn').disabled = false;
    uploadedFileName = null;
    uploadedIdLoad   = null;  
}
async function handleUploadAction() {
    if (!uploadedFileName) {
        
        const file = fileInput.files[0];
        if (!file) { showToast('Please select a file first', 'error'); return; }
        const idLoad = document.getElementById('idLoadSelect').value;
        await doUpload(file, idLoad);
    } else {
      
        await doProcess();
    }
}

async function doUpload(file, idLoad) {
    const btn      = document.getElementById('uploadActionBtn');
    const progress = document.getElementById('uploadProgress');
    btn.disabled   = true;
    progress.classList.add('show');
    document.getElementById('progressLabel').textContent = 'Uploading…';
    animateProgress(0, 60, 800);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const data = await apiPostForm(`/data-load/${idLoad}`, formData);

        animateProgress(60, 100, 400);
        setTimeout(async () => {
            uploadedFileName = data.file_name;
            uploadedIdLoad   = idLoad;
            document.getElementById('uploadedFileName').textContent = data.file_name;

            // switch to step 2
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = '';
            document.getElementById('uploadActionLabel').textContent = 'Process';
            document.getElementById('uploadActionBtn').querySelector('i').className = 'fa-solid fa-gears';
            btn.disabled = false;
            progress.classList.remove('show');

            await loadFiles();
            showToast('File uploaded! Now configure processing.', 'success');
        }, 500);

    } catch(e) {
        btn.disabled = false;
        progress.classList.remove('show');
        showToast('Upload failed: ' + e.message, 'error');
    }
}

async function doProcess() {
    const btn = document.getElementById('uploadActionBtn');
    btn.disabled = true;
    document.getElementById('uploadProgress').classList.add('show');
    document.getElementById('progressLabel').textContent = 'Processing chunks…';
    animateProgress(0, 80, 1200);

    const idLoadForProcess = uploadedIdLoad || document.getElementById('idLoadSelect').value;

    try {
        const data = await apiPost(`/proccese/${idLoadForProcess}`, {
            file_name:    uploadedFileName,
            chunk_size:   parseInt(document.getElementById('chunkSize').value),
            overlap_size: parseInt(document.getElementById('overlapSize').value),
            re_set:       parseInt(document.getElementById('resetChunks').value)
        });

        animateProgress(80, 100, 400);
        setTimeout(async () => {
            closeModal('uploadModal');
            showToast(data.status || 'Processing complete! RAG ready ✅', 'success');
            await loadFiles();
        }, 500);

    } catch(e) {
        btn.disabled = false;
        showToast('Processing failed: ' + e.message, 'error');
    }
}
function openProcessModal(fileName, idLoad) {
    uploadedFileName = fileName;
    uploadedIdLoad   = idLoad || Auth.getRole();   
    document.getElementById('step1').style.display = 'none';
    document.getElementById('step2').style.display = '';
    document.getElementById('uploadedFileName').textContent = fileName;
    document.getElementById('uploadActionLabel').textContent = 'Process';
    document.getElementById('uploadActionBtn').querySelector('i').className = 'fa-solid fa-gears';
    document.getElementById('idLoadSelect').value = uploadedIdLoad;
    openModal('uploadModal');
}

function animateProgress(from, to, duration) {
    const fill  = document.getElementById('progressFill');
    const pct   = document.getElementById('progressPct');
    const steps = 30;
    const step  = (to - from) / steps;
    let   cur   = from;
    const iv = setInterval(() => {
        cur += step;
        if (cur >= to) { cur = to; clearInterval(iv); }
        fill.style.width = cur + '%';
        pct.textContent  = Math.round(cur) + '%';
    }, duration / steps);
}

document.getElementById('createUserBtn').addEventListener('click', () => {
    const role = Auth.getRole();
    const sel  = document.getElementById('newUserRole');
    sel.innerHTML = '';
    
    if (role === 'admin') {
        sel.innerHTML = '<option value="manager">Manager</option><option value="user">User</option>';
    } else if (role === 'manager') {
        sel.innerHTML = '<option value="user">User</option>';
    } else {
        showToast('You do not have permission to create users', 'error'); return;
    }
    document.getElementById('newUserEmail').value = '';
    document.getElementById('newUserPass').value  = '';
    openModal('userModal');
});

async function doCreateUser() {
    const email = document.getElementById('newUserEmail').value.trim();
    const pass  = document.getElementById('newUserPass').value.trim();
    const role  = document.getElementById('newUserRole').value;

    if (!email || !pass) { showToast('Email and password required', 'error'); return; }

    const btn = document.getElementById('createUserConfirm');
    btn.disabled = true;

    try {
        const data = await apiPost('/users', { email, password: pass, role });
        const newUser = { id: data.id, email: data.email, role: data.role, is_active: true, created_by: data.created_by };

        const exists = allUsers.find(u => u.id === newUser.id);
        if (!exists) allUsers.push(newUser);
        else Object.assign(exists, newUser);

        Store.saveUsers(allUsers);  
        updateUserCounts();
        renderUsers();
        closeModal('userModal');
        showToast(`User ${email} created as ${role}! ✅`, 'success');
    } catch(e) {
        showToast('Could not create user: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
    }
}


function applyTheme() {
    document.body.classList.toggle('dark-mode', isDark);
    document.getElementById('themeBtn').innerHTML =
        isDark ? '<i class="fa-solid fa-sun"></i> Theme' : '<i class="fa-solid fa-moon"></i> Theme';
}
document.getElementById('themeBtn').addEventListener('click', () => {
    isDark = !isDark;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    applyTheme();
});


function renderUserInfo() {
    const s = Auth.getSession();
    if (!s) return;
    const name = s.email ? s.email.split('@')[0] : 'User';
    document.getElementById('chipName').textContent = name;
    document.getElementById('chipRole').textContent = s.role || 'user';
}

document.addEventListener('DOMContentLoaded', () => {
    if (!Auth.guard()) return;
    applyTheme();
    renderUserInfo();
    checkPermissions();
    loadFiles();

    document.addEventListener('keydown', e => {
        if (e.key === 'u' && !e.ctrlKey && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) {
            document.getElementById('uploadBtn').click();
        }
    });
});
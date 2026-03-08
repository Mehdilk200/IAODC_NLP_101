const API_BASE    = 'http://0.0.0.0:8000';
        const REDIRECT_TO = 'chat_t.html';

        const emailEl     = document.getElementById('email');
        const passEl      = document.getElementById('password');
        const loginBtn    = document.getElementById('loginBtn');
        const alertBox    = document.getElementById('alertBox');
        const alertMsg    = document.getElementById('alertMsg');
        const togglePass  = document.getElementById('togglePass');
        const toggleIco   = document.getElementById('toggleIco');
        const emailErr    = document.getElementById('emailErr');
        const passErr     = document.getElementById('passErr');
        const sessionBox  = document.getElementById('sessionBox');
        const redirectBar = document.getElementById('redirectBar');
        const cdEl        = document.getElementById('cd');

        let selectedRole = 'admin';

        document.querySelectorAll('.role-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedRole = btn.dataset.role;
            });
        });

        togglePass.addEventListener('click', () => {
            const show = passEl.type === 'password';
            passEl.type = show ? 'text' : 'password';
            toggleIco.className = show ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
        });

        function showAlert(msg, type = 'error') {
            alertBox.className = `alert ${type}`;
            alertMsg.textContent = msg;
            alertBox.querySelector('i').className =
                type === 'error' ? 'fa-solid fa-circle-exclamation' : 'fa-solid fa-circle-check';
        }
        function hideAlert() { alertBox.className = 'alert hidden'; }

        emailEl.addEventListener('input', () => { emailEl.classList.remove('invalid'); emailErr.classList.remove('show'); hideAlert(); });
        passEl.addEventListener('input',  () => { passEl.classList.remove('invalid');  passErr.classList.remove('show');  hideAlert(); });
        [emailEl, passEl].forEach(el => el.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); }));

        function validate() {
            let ok = true;
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailEl.value.trim())) {
                emailEl.classList.add('invalid'); emailErr.classList.add('show'); ok = false;
            }
            if (!passEl.value.trim()) {
                passEl.classList.add('invalid'); passErr.classList.add('show'); ok = false;
            }
            return ok;
        }

        async function doLogin() {
            if (!validate()) return;
            loginBtn.classList.add('loading');
            loginBtn.disabled = true;
            hideAlert();

            try {
                const loginRes = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailEl.value.trim(), password: passEl.value.trim() })
                });

                if (!loginRes.ok) {
                    const err = await loginRes.json().catch(() => ({}));
                    showAlert(err.detail || `Error ${loginRes.status}: Invalid credentials`);
                    return;
                }

                const data  = await loginRes.json();
                const token = data.access_token || data.token || data.jwt;
                if (!token) { showAlert('Server returned no token.'); return; }

                let userData = {};
                const meRes = await fetch(`${API_BASE}/users/me`, {
                    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
                });
                if (meRes.ok) userData = await meRes.json();

                const session = {
                    token,
                    userId:    userData.id    || '',
                    email:     userData.email || emailEl.value.trim(),
                    role:      userData.role  || selectedRole,
                    isActive:  userData.is_active ?? true,
                    loginTime: new Date().toISOString()
                };
                localStorage.setItem('ragiso_session', JSON.stringify(session));
                localStorage.setItem('ragiso_token', token);

                showAlert('Login successful!', 'success');
                document.getElementById('sId').textContent    = session.userId || '—';
                document.getElementById('sEmail').textContent = session.email;
                document.getElementById('sRole').textContent  = session.role;
                document.getElementById('sToken').textContent = token.substring(0, 28) + '…';
                sessionBox.classList.add('show');
                redirectBar.classList.add('show');

                let t = 3; cdEl.textContent = t;
                const iv = setInterval(() => {
                    t--; cdEl.textContent = t;
                    if (t <= 0) { clearInterval(iv); window.location.href = REDIRECT_TO; }
                }, 1000);

            } catch (err) {
                if (err.name === 'TypeError')
                    showAlert(`Cannot reach API at ${API_BASE}. Is the server running?`);
                else
                    showAlert(err.message || 'Unexpected error.');
            } finally {
                loginBtn.classList.remove('loading');
                loginBtn.disabled = false;
            }
        }

        loginBtn.addEventListener('click', doLogin);

        window.RAGISO = {
            getSession() { try { return JSON.parse(localStorage.getItem('ragiso_session')); } catch { return null; } },
            getToken()   { return localStorage.getItem('ragiso_token'); },
            getRole()    { return this.getSession()?.role || null; },
            authHeaders(){ return { 'Authorization': `Bearer ${this.getToken()}`, 'Content-Type': 'application/json' }; },
            logout()     { localStorage.removeItem('ragiso_session'); localStorage.removeItem('ragiso_token'); window.location.href = 'login.html'; },
            guard(roles=[]){
                const s = this.getSession();
                if (!s?.token) { window.location.href = 'login.html'; return false; }
                if (roles.length && !roles.includes(s.role)) { alert('Access denied: ' + s.role); return false; }
                return true;
            }
        };

        (function(){
            const s = window.RAGISO.getSession();
            if (s?.token) { redirectBar.classList.add('show'); cdEl.textContent='1'; setTimeout(()=>window.location.href=REDIRECT_TO,900); }
        })();

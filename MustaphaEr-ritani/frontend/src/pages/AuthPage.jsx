import { useState } from "react";
import { authAPI } from "../services/api";
import toast from "react-hot-toast";

export default function AuthPage({ onLogin }) {
    const [mode, setMode] = useState("login"); // "login" | "register"
    const [form, setForm] = useState({ username: "", password: "", email: "" });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.username || !form.password) {
            toast.error("Please fill in all required fields");
            return;
        }
        setLoading(true);
        try {
            let res;
            if (mode === "login") {
                res = await authAPI.login(form.username, form.password);
            } else {
                res = await authAPI.register(form.username, form.password, form.email);
            }
            toast.success(mode === "login" ? "Welcome back! 👋" : "Account created! 🎉");
            onLogin(res.data.access_token, res.data.username);
        } catch (err) {
            const msg = err.response?.data?.detail || "Authentication failed";
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    // Demo login shortcut
    const handleDemo = async () => {
        setLoading(true);
        try {
            // Try to register demo user first, then login
            try {
                await authAPI.register("demo", "demo123", "demo@example.com");
            } catch (_) { }
            const res = await authAPI.login("demo", "demo123");
            toast.success("Logged in as demo user 🚀");
            onLogin(res.data.access_token, res.data.username);
        } catch (err) {
            toast.error("Demo login failed. Please register manually.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card fade-in">
                {/* Logo */}
                <div className="auth-logo">
                    <div className="auth-logo-icon">🧠</div>
                    <h1 className="auth-title">AI Resume Screener</h1>
                    <p className="auth-subtitle">NLP-powered candidate matching</p>
                </div>

                {/* Tabs */}
                <div className="tabs">
                    <button
                        className={`tab ${mode === "login" ? "active" : ""}`}
                        onClick={() => setMode("login")}
                    >
                        Sign In
                    </button>
                    <button
                        className={`tab ${mode === "register" ? "active" : ""}`}
                        onClick={() => setMode("register")}
                    >
                        Register
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Username</label>
                        <input
                            className="form-input"
                            type="text"
                            placeholder="Enter username"
                            value={form.username}
                            onChange={(e) => setForm({ ...form, username: e.target.value })}
                            autoComplete="username"
                        />
                    </div>

                    {mode === "register" && (
                        <div className="form-group">
                            <label className="form-label">Email (optional)</label>
                            <input
                                className="form-input"
                                type="email"
                                placeholder="recruiter@company.com"
                                value={form.email}
                                onChange={(e) => setForm({ ...form, email: e.target.value })}
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            className="form-input"
                            type="password"
                            placeholder="Enter password"
                            value={form.password}
                            onChange={(e) => setForm({ ...form, password: e.target.value })}
                            autoComplete="current-password"
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary btn-full btn-lg"
                        disabled={loading}
                        style={{ marginBottom: 12 }}
                    >
                        {loading ? (
                            <><span className="spinner" /> Processing...</>
                        ) : mode === "login" ? (
                            "🔐 Sign In"
                        ) : (
                            "✨ Create Account"
                        )}
                    </button>

                    <button
                        type="button"
                        className="btn btn-secondary btn-full"
                        onClick={handleDemo}
                        disabled={loading}
                    >
                        🚀 Try Demo
                    </button>
                </form>

                <p style={{ textAlign: "center", marginTop: 20, fontSize: 12, color: "var(--text-muted)" }}>
                    Powered by Sentence Transformers & KeyBERT
                </p>
            </div>
        </div>
    );
}

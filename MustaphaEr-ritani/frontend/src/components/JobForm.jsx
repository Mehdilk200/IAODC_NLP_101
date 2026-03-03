import { useState, useEffect } from "react";
import { jobAPI } from "../services/api";
import toast from "react-hot-toast";

const SAMPLE_JD = `We are looking for a Senior Data Scientist to join our AI team.

Requirements:
- 3+ years of experience with Python and machine learning
- Strong knowledge of NLP, deep learning, and transformer models
- Experience with PyTorch or TensorFlow
- Proficiency in SQL and data analysis
- Familiarity with Docker and AWS cloud services
- Experience with scikit-learn, pandas, numpy
- Knowledge of REST APIs and microservices architecture

Nice to have:
- Experience with Hugging Face transformers
- Knowledge of MLOps and CI/CD pipelines
- Agile/Scrum methodology`;

export default function JobForm() {
    const [form, setForm] = useState({
        title: "",
        description: "",
        company: "",
        location: "",
        required_skills: "",
    });
    const [loading, setLoading] = useState(false);
    const [jobs, setJobs] = useState([]);
    const [loadingJobs, setLoadingJobs] = useState(false);
    const [activeTab, setActiveTab] = useState("create");
    const [editingJob, setEditingJob] = useState(null);

    const loadJobs = async () => {
        setLoadingJobs(true);
        try {
            const res = await jobAPI.getJobs();
            setJobs(res.data.jobs);
        } catch {
            toast.error("Failed to load jobs");
        } finally {
            setLoadingJobs(false);
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === "list") loadJobs();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.title.trim() || !form.description.trim()) {
            return toast.error("Title and description are required");
        }

        setLoading(true);
        try {
            const skillsList = form.required_skills
                ? form.required_skills.split(",").map((s) => s.trim()).filter(Boolean)
                : [];

            const payload = {
                title: form.title,
                description: form.description,
                company: form.company,
                location: form.location,
                required_skills: skillsList,
            };

            if (editingJob) {
                await jobAPI.updateJob(editingJob.id, payload);
                toast.success("Job updated successfully!");
                setEditingJob(null);
            } else {
                await jobAPI.createJob(payload);
                toast.success("Job created and indexed! 🎉");
            }

            setForm({ title: "", description: "", company: "", location: "", required_skills: "" });
            handleTabChange("list");
        } catch (err) {
            toast.error(err.response?.data?.detail || "Failed to save job");
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (job) => {
        setEditingJob(job);
        setForm({
            title: job.title,
            description: job.description,
            company: job.company || "",
            location: job.location || "",
            required_skills: (job.required_skills || []).join(", "),
        });
        setActiveTab("create");
    };

    const handleDelete = async (id, title) => {
        if (!confirm(`Delete job: "${title}"?`)) return;
        try {
            await jobAPI.deleteJob(id);
            setJobs((prev) => prev.filter((j) => j.id !== id));
            toast.success("Job deleted");
        } catch {
            toast.error("Delete failed");
        }
    };

    const useSample = () => {
        setForm({
            title: "Senior Data Scientist",
            description: SAMPLE_JD,
            company: "TechCorp AI",
            location: "Remote",
            required_skills: "python, machine learning, nlp, pytorch, sql, docker, aws",
        });
        toast("Sample job description loaded 📋");
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">💼 Job Descriptions</h1>
                <p className="page-subtitle">
                    Create and manage job postings — AI will extract required skills automatically
                </p>
            </div>

            <div className="tabs" style={{ maxWidth: 400 }}>
                <button
                    className={`tab ${activeTab === "create" ? "active" : ""}`}
                    onClick={() => handleTabChange("create")}
                >
                    {editingJob ? "✏️ Edit Job" : "➕ Create Job"}
                </button>
                <button
                    className={`tab ${activeTab === "list" ? "active" : ""}`}
                    onClick={() => handleTabChange("list")}
                >
                    All Jobs
                </button>
            </div>

            {activeTab === "create" && (
                <div className="grid-2">
                    <div className="card">
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                            <h2 className="section-title" style={{ marginBottom: 0 }}>
                                {editingJob ? "✏️ Edit Job" : "📝 New Job Posting"}
                            </h2>
                            <button className="btn btn-secondary btn-sm" onClick={useSample}>
                                📋 Load Sample
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label">Job Title *</label>
                                <input
                                    className="form-input"
                                    type="text"
                                    placeholder="e.g. Senior Data Scientist"
                                    value={form.title}
                                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                                />
                            </div>

                            <div className="grid-2" style={{ gap: 12 }}>
                                <div className="form-group">
                                    <label className="form-label">Company</label>
                                    <input
                                        className="form-input"
                                        type="text"
                                        placeholder="Company name"
                                        value={form.company}
                                        onChange={(e) => setForm({ ...form, company: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Location</label>
                                    <input
                                        className="form-input"
                                        type="text"
                                        placeholder="Remote / City"
                                        value={form.location}
                                        onChange={(e) => setForm({ ...form, location: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Job Description *</label>
                                <textarea
                                    className="form-textarea"
                                    placeholder="Paste the full job description here..."
                                    value={form.description}
                                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                                    rows={8}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Required Skills (comma-separated)</label>
                                <input
                                    className="form-input"
                                    type="text"
                                    placeholder="python, machine learning, docker, aws..."
                                    value={form.required_skills}
                                    onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
                                />
                                <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                                    💡 Leave empty — AI will extract skills automatically
                                </p>
                            </div>

                            <div style={{ display: "flex", gap: 12 }}>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    style={{ flex: 1 }}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <><span className="spinner" /> Saving...</>
                                    ) : editingJob ? (
                                        "💾 Update Job"
                                    ) : (
                                        "🚀 Create Job"
                                    )}
                                </button>
                                {editingJob && (
                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={() => {
                                            setEditingJob(null);
                                            setForm({ title: "", description: "", company: "", location: "", required_skills: "" });
                                        }}
                                    >
                                        Cancel
                                    </button>
                                )}
                            </div>
                        </form>
                    </div>

                    {/* Tips */}
                    <div className="card" style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.08), rgba(6,182,212,0.04))" }}>
                        <h2 className="section-title">💡 Tips for Better Matching</h2>
                        <ul style={{ paddingLeft: 20, color: "var(--text-secondary)", fontSize: 14, lineHeight: 2.2 }}>
                            <li>Include specific technologies and tools</li>
                            <li>Mention years of experience required</li>
                            <li>List both required and nice-to-have skills</li>
                            <li>Include soft skills (leadership, teamwork)</li>
                            <li>Describe the role responsibilities clearly</li>
                        </ul>
                        <div className="divider" />
                        <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 8 }}>
                            🤖 AI Processing
                        </h3>
                        <p style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.7 }}>
                            After saving, the AI will automatically:
                        </p>
                        <ul style={{ paddingLeft: 20, color: "var(--text-muted)", fontSize: 13, lineHeight: 2 }}>
                            <li>Extract key skills using KeyBERT</li>
                            <li>Generate semantic embeddings</li>
                            <li>Index for fast candidate matching</li>
                        </ul>
                    </div>
                </div>
            )}

            {activeTab === "list" && (
                <div className="card">
                    <h2 className="section-title">💼 All Jobs ({jobs.length})</h2>
                    {loadingJobs ? (
                        <div className="loading-overlay">
                            <div className="loading-spinner-lg" />
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📭</div>
                            <div className="empty-state-title">No jobs yet</div>
                            <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                                Create your first job posting
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                            {jobs.map((job) => (
                                <div
                                    key={job.id}
                                    style={{
                                        background: "var(--bg-input)",
                                        borderRadius: "var(--radius-md)",
                                        padding: 16,
                                        border: "1px solid var(--border)",
                                    }}
                                >
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>
                                                {job.title}
                                            </div>
                                            <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 8 }}>
                                                {job.company && `🏢 ${job.company}`}
                                                {job.location && ` • 📍 ${job.location}`}
                                            </div>
                                            <div className="skills-container">
                                                {(job.required_skills || []).slice(0, 8).map((s) => (
                                                    <span key={s} className="skill-tag neutral">{s}</span>
                                                ))}
                                                {(job.required_skills || []).length > 8 && (
                                                    <span className="skill-tag neutral">
                                                        +{job.required_skills.length - 8} more
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        <div style={{ display: "flex", gap: 8, marginLeft: 16 }}>
                                            <button
                                                className="btn btn-secondary btn-sm"
                                                onClick={() => handleEdit(job)}
                                            >
                                                ✏️ Edit
                                            </button>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => handleDelete(job.id, job.title)}
                                            >
                                                🗑
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

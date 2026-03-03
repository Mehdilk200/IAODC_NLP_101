import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadAPI } from "../services/api";
import toast from "react-hot-toast";

export default function UploadCV() {
    const [file, setFile] = useState(null);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [candidates, setCandidates] = useState([]);
    const [loadingCandidates, setLoadingCandidates] = useState(false);
    const [activeTab, setActiveTab] = useState("upload"); // "upload" | "list"

    const onDrop = useCallback((acceptedFiles) => {
        const f = acceptedFiles[0];
        if (f) {
            setFile(f);
            // Auto-fill name from filename
            if (!name) {
                const n = f.name.replace(/\.(pdf|docx|doc)$/i, "").replace(/[-_]/g, " ");
                setName(n);
            }
            toast.success(`File selected: ${f.name}`);
        }
    }, [name]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
            "application/msword": [".doc"],
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    });

    const handleUpload = async () => {
        if (!file) return toast.error("Please select a CV file");
        if (!name.trim()) return toast.error("Please enter the candidate name");

        setLoading(true);
        setResult(null);
        try {
            const res = await uploadAPI.uploadCV(file, name.trim(), email.trim());
            setResult(res.data);
            toast.success("CV uploaded and processed successfully! 🎉");
            setFile(null);
            setName("");
            setEmail("");
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || err.message || "Upload failed. Check backend connection.";
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    const loadCandidates = async () => {
        setLoadingCandidates(true);
        try {
            const res = await uploadAPI.getCandidates();
            setCandidates(res.data.candidates);
        } catch {
            toast.error("Failed to load candidates");
        } finally {
            setLoadingCandidates(false);
        }
    };

    const handleDelete = async (id, candidateName) => {
        if (!confirm(`Delete ${candidateName}?`)) return;
        try {
            await uploadAPI.deleteCandidate(id);
            setCandidates((prev) => prev.filter((c) => c.id !== id));
            toast.success("Candidate deleted");
        } catch {
            toast.error("Delete failed");
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === "list") loadCandidates();
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">📄 Upload CV</h1>
                <p className="page-subtitle">
                    Upload PDF or DOCX files — AI will extract text, detect language, and identify skills
                </p>
            </div>

            {/* Tabs */}
            <div className="tabs" style={{ maxWidth: 400 }}>
                <button
                    className={`tab ${activeTab === "upload" ? "active" : ""}`}
                    onClick={() => handleTabChange("upload")}
                >
                    Upload New CV
                </button>
                <button
                    className={`tab ${activeTab === "list" ? "active" : ""}`}
                    onClick={() => handleTabChange("list")}
                >
                    All Candidates
                </button>
            </div>

            {activeTab === "upload" && (
                <div className="grid-2">
                    {/* Upload Form */}
                    <div className="card">
                        <h2 className="section-title">📎 Select CV File</h2>

                        {/* Dropzone */}
                        <div
                            {...getRootProps()}
                            className={`dropzone ${isDragActive ? "active" : ""}`}
                            style={{ marginBottom: 24 }}
                        >
                            <input {...getInputProps()} />
                            <span className="dropzone-icon">
                                {file ? "✅" : isDragActive ? "📂" : "📁"}
                            </span>
                            {file ? (
                                <>
                                    <div className="dropzone-title" style={{ color: "var(--success)" }}>
                                        {file.name}
                                    </div>
                                    <div className="dropzone-subtitle">
                                        {(file.size / 1024).toFixed(1)} KB — Click to change
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="dropzone-title">
                                        {isDragActive ? "Drop it here!" : "Drag & drop your CV here"}
                                    </div>
                                    <div className="dropzone-subtitle">
                                        Supports PDF, DOCX • Max 10 MB
                                    </div>
                                </>
                            )}
                        </div>

                        {/* Candidate Info */}
                        <div className="form-group">
                            <label className="form-label">Candidate Name *</label>
                            <input
                                className="form-input"
                                type="text"
                                placeholder="John Doe"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email (optional)</label>
                            <input
                                className="form-input"
                                type="email"
                                placeholder="john@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <button
                            className="btn btn-primary btn-full btn-lg"
                            onClick={handleUpload}
                            disabled={loading || !file}
                        >
                            {loading ? (
                                <><span className="spinner" /> Processing CV...</>
                            ) : (
                                "🚀 Upload & Analyze"
                            )}
                        </button>

                        {loading && (
                            <div className="alert alert-info" style={{ marginTop: 16 }}>
                                ⏳ Extracting text, detecting language, and generating embeddings...
                                This may take 10–30 seconds.
                            </div>
                        )}
                    </div>

                    {/* Result */}
                    <div>
                        {result ? (
                            <div className="card fade-in">
                                <h2 className="section-title">✅ Analysis Complete</h2>

                                <div style={{ marginBottom: 20 }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                                        <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>Candidate</span>
                                        <span style={{ fontWeight: 600 }}>{result.name}</span>
                                    </div>
                                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                                        <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>Language</span>
                                        <span className="badge badge-primary">
                                            {result.language?.toUpperCase()}
                                        </span>
                                    </div>
                                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                                        <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>Skills Found</span>
                                        <span className="badge badge-success">{result.skill_count}</span>
                                    </div>
                                </div>

                                <div className="divider" />

                                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: "var(--text-secondary)" }}>
                                    🔍 Extracted Skills
                                </h3>
                                <div className="skills-container">
                                    {result.skills?.length > 0 ? (
                                        result.skills.map((skill) => (
                                            <span key={skill} className="skill-tag neutral">
                                                {skill}
                                            </span>
                                        ))
                                    ) : (
                                        <span style={{ color: "var(--text-muted)", fontSize: 13 }}>
                                            No skills detected
                                        </span>
                                    )}
                                </div>

                                <div className="divider" />

                                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: "var(--text-secondary)" }}>
                                    📝 Text Preview
                                </h3>
                                <div
                                    style={{
                                        background: "var(--bg-input)",
                                        borderRadius: "var(--radius-md)",
                                        padding: 14,
                                        fontSize: 13,
                                        color: "var(--text-secondary)",
                                        lineHeight: 1.7,
                                        maxHeight: 200,
                                        overflowY: "auto",
                                    }}
                                >
                                    {result.text_preview}
                                </div>

                                <div
                                    style={{
                                        marginTop: 12,
                                        padding: "8px 12px",
                                        background: "rgba(16,185,129,0.1)",
                                        borderRadius: "var(--radius-sm)",
                                        fontSize: 12,
                                        color: "var(--success)",
                                    }}
                                >
                                    ✅ ID: {result.candidate_id}
                                </div>
                            </div>
                        ) : (
                            <div className="card" style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" }}>
                                <div className="empty-state">
                                    <div className="empty-state-icon">🤖</div>
                                    <div className="empty-state-title">AI Ready</div>
                                    <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                                        Upload a CV to see extracted skills and analysis
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === "list" && (
                <div className="card">
                    <h2 className="section-title">👥 All Candidates ({candidates.length})</h2>
                    {loadingCandidates ? (
                        <div className="loading-overlay">
                            <div className="loading-spinner-lg" />
                            <p>Loading candidates...</p>
                        </div>
                    ) : candidates.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📭</div>
                            <div className="empty-state-title">No candidates yet</div>
                            <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                                Upload your first CV to get started
                            </p>
                        </div>
                    ) : (
                        <table className="ranking-table">
                            <thead>
                                <tr>
                                    <th>Candidate</th>
                                    <th>Language</th>
                                    <th>Skills</th>
                                    <th>Score</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {candidates.map((c) => (
                                    <tr key={c.id}>
                                        <td>
                                            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                                <div className="candidate-avatar">
                                                    {c.name?.charAt(0)?.toUpperCase()}
                                                </div>
                                                <div>
                                                    <div style={{ fontWeight: 600 }}>{c.name}</div>
                                                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                                                        {c.email || "—"}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className="badge badge-primary">
                                                {(c.language || "en").toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="badge badge-success">
                                                {c.skills?.length || 0} skills
                                            </span>
                                        </td>
                                        <td>
                                            {c.score != null ? (
                                                <span
                                                    style={{
                                                        fontWeight: 700,
                                                        color: c.score >= 70 ? "var(--success)" : c.score >= 40 ? "var(--warning)" : "var(--danger)",
                                                    }}
                                                >
                                                    {c.score.toFixed(1)}%
                                                </span>
                                            ) : (
                                                <span style={{ color: "var(--text-muted)", fontSize: 13 }}>Not matched</span>
                                            )}
                                        </td>
                                        <td>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => handleDelete(c.id, c.name)}
                                            >
                                                🗑 Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}

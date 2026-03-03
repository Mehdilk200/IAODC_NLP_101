import { useState, useEffect } from "react";
import { matchAPI, uploadAPI, jobAPI } from "../services/api";
import toast from "react-hot-toast";

export default function MatchResult() {
    const [candidates, setCandidates] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [selectedCandidate, setSelectedCandidate] = useState("");
    const [selectedJob, setSelectedJob] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [cRes, jRes] = await Promise.all([
                uploadAPI.getCandidates(),
                jobAPI.getJobs(),
            ]);
            setCandidates(cRes.data.candidates);
            setJobs(jRes.data.jobs);
        } catch {
            toast.error("Failed to load data");
        }
    };

    const handleMatch = async () => {
        if (!selectedCandidate) return toast.error("Select a candidate");
        if (!selectedJob) return toast.error("Select a job");

        setLoading(true);
        setResult(null);
        try {
            const res = await matchAPI.matchSingle(selectedCandidate, selectedJob);
            setResult(res.data);
            toast.success("Matching complete! 🎯");
        } catch (err) {
            toast.error(err.response?.data?.detail || "Matching failed");
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReport = async () => {
        if (!result) return;
        setDownloading(true);
        try {
            const res = await matchAPI.downloadReport(result.candidate_id, result.job_id);
            const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
            const link = document.createElement("a");
            link.href = url;
            link.download = `report_${result.candidate_name}_${result.job_title}.pdf`;
            link.click();
            window.URL.revokeObjectURL(url);
            toast.success("Report downloaded! 📄");
        } catch {
            toast.error("Failed to download report");
        } finally {
            setDownloading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 70) return "var(--success)";
        if (score >= 40) return "var(--warning)";
        return "var(--danger)";
    };

    const getScoreClass = (score) => {
        if (score >= 70) return "progress-high";
        if (score >= 40) return "progress-medium";
        return "progress-low";
    };

    const getScoreLabel = (score) => {
        if (score >= 80) return "Excellent Match 🌟";
        if (score >= 65) return "Good Match ✅";
        if (score >= 45) return "Partial Match ⚠️";
        return "Poor Match ❌";
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">🎯 Match CV to Job</h1>
                <p className="page-subtitle">
                    Select a candidate and job to compute semantic similarity and skill matching
                </p>
            </div>

            <div className="grid-2">
                {/* Selection Panel */}
                <div className="card">
                    <h2 className="section-title">⚙️ Configure Match</h2>

                    <div className="form-group">
                        <label className="form-label">Select Candidate</label>
                        <select
                            className="form-select"
                            value={selectedCandidate}
                            onChange={(e) => setSelectedCandidate(e.target.value)}
                        >
                            <option value="">— Choose a candidate —</option>
                            {candidates.map((c) => (
                                <option key={c.id} value={c.id}>
                                    {c.name} {c.language ? `(${c.language.toUpperCase()})` : ""}
                                </option>
                            ))}
                        </select>
                        {candidates.length === 0 && (
                            <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                                ⚠️ No candidates found. Upload CVs first.
                            </p>
                        )}
                    </div>

                    <div className="form-group">
                        <label className="form-label">Select Job</label>
                        <select
                            className="form-select"
                            value={selectedJob}
                            onChange={(e) => setSelectedJob(e.target.value)}
                        >
                            <option value="">— Choose a job —</option>
                            {jobs.map((j) => (
                                <option key={j.id} value={j.id}>
                                    {j.title} {j.company ? `@ ${j.company}` : ""}
                                </option>
                            ))}
                        </select>
                        {jobs.length === 0 && (
                            <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                                ⚠️ No jobs found. Create a job description first.
                            </p>
                        )}
                    </div>

                    <button
                        className="btn btn-primary btn-full btn-lg"
                        onClick={handleMatch}
                        disabled={loading || !selectedCandidate || !selectedJob}
                    >
                        {loading ? (
                            <><span className="spinner" /> Computing Similarity...</>
                        ) : (
                            "🚀 Run AI Match"
                        )}
                    </button>

                    {loading && (
                        <div className="alert alert-info" style={{ marginTop: 16 }}>
                            🤖 Computing cosine similarity between embeddings...
                        </div>
                    )}

                    {/* Info box */}
                    <div
                        style={{
                            marginTop: 24,
                            padding: 16,
                            background: "var(--bg-input)",
                            borderRadius: "var(--radius-md)",
                            fontSize: 13,
                            color: "var(--text-muted)",
                            lineHeight: 1.8,
                        }}
                    >
                        <strong style={{ color: "var(--text-secondary)" }}>How it works:</strong>
                        <br />
                        1. Sentence Transformers encode both texts
                        <br />
                        2. Cosine similarity is computed
                        <br />
                        3. Skills are compared from both sides
                        <br />
                        4. Score is normalized to 0–100%
                    </div>
                </div>

                {/* Result Panel */}
                <div>
                    {result ? (
                        <div className="card fade-in">
                            {/* Score */}
                            <div style={{ textAlign: "center", marginBottom: 24 }}>
                                <div
                                    style={{
                                        width: 140,
                                        height: 140,
                                        borderRadius: "50%",
                                        border: `6px solid ${getScoreColor(result.match_score)}`,
                                        display: "flex",
                                        flexDirection: "column",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        margin: "0 auto 12px",
                                        boxShadow: `0 0 30px ${getScoreColor(result.match_score)}40`,
                                        transition: "all 0.5s ease",
                                    }}
                                >
                                    <span
                                        style={{
                                            fontFamily: "var(--font-display)",
                                            fontSize: 36,
                                            fontWeight: 800,
                                            color: getScoreColor(result.match_score),
                                            lineHeight: 1,
                                        }}
                                    >
                                        {result.match_score.toFixed(0)}%
                                    </span>
                                    <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                                        Match Score
                                    </span>
                                </div>
                                <div
                                    style={{
                                        fontSize: 16,
                                        fontWeight: 600,
                                        color: getScoreColor(result.match_score),
                                    }}
                                >
                                    {getScoreLabel(result.match_score)}
                                </div>
                            </div>

                            {/* Progress Bar */}
                            <div className="progress-container">
                                <div className="progress-track">
                                    <div
                                        className={`progress-fill ${getScoreClass(result.match_score)}`}
                                        style={{ width: `${result.match_score}%` }}
                                    />
                                </div>
                            </div>

                            {/* Meta */}
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    padding: "12px 0",
                                    borderTop: "1px solid var(--border)",
                                    borderBottom: "1px solid var(--border)",
                                    margin: "16px 0",
                                    fontSize: 13,
                                }}
                            >
                                <div>
                                    <div style={{ color: "var(--text-muted)" }}>Candidate</div>
                                    <div style={{ fontWeight: 600 }}>{result.candidate_name}</div>
                                </div>
                                <div style={{ textAlign: "right" }}>
                                    <div style={{ color: "var(--text-muted)" }}>Position</div>
                                    <div style={{ fontWeight: 600 }}>{result.job_title}</div>
                                </div>
                            </div>

                            {/* Matched Skills */}
                            <div style={{ marginBottom: 16 }}>
                                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: "var(--success)" }}>
                                    ✅ Matched Skills ({result.matched_skills.length})
                                </h3>
                                <div className="skills-container">
                                    {result.matched_skills.length > 0 ? (
                                        result.matched_skills.map((s) => (
                                            <span key={s} className="skill-tag matched">✔ {s}</span>
                                        ))
                                    ) : (
                                        <span style={{ color: "var(--text-muted)", fontSize: 13 }}>
                                            No matched skills
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Missing Skills */}
                            <div style={{ marginBottom: 20 }}>
                                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: "var(--danger)" }}>
                                    ❌ Missing Skills ({result.missing_skills.length})
                                </h3>
                                <div className="skills-container">
                                    {result.missing_skills.length > 0 ? (
                                        result.missing_skills.map((s) => (
                                            <span key={s} className="skill-tag missing">✘ {s}</span>
                                        ))
                                    ) : (
                                        <span style={{ color: "var(--success)", fontSize: 13 }}>
                                            🎉 All required skills present!
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Download Report */}
                            <button
                                className="btn btn-success btn-full"
                                onClick={handleDownloadReport}
                                disabled={downloading}
                            >
                                {downloading ? (
                                    <><span className="spinner" /> Generating PDF...</>
                                ) : (
                                    "📄 Download PDF Report"
                                )}
                            </button>
                        </div>
                    ) : (
                        <div className="card" style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" }}>
                            <div className="empty-state">
                                <div className="empty-state-icon">🎯</div>
                                <div className="empty-state-title">Ready to Match</div>
                                <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                                    Select a candidate and job, then click "Run AI Match"
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

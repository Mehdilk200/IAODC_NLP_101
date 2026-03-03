import { useState, useEffect } from "react";
import { matchAPI, jobAPI, uploadAPI } from "../services/api";
import toast from "react-hot-toast";

export default function CandidateRanking() {
    const [jobs, setJobs] = useState([]);
    const [selectedJob, setSelectedJob] = useState("");
    const [rankings, setRankings] = useState([]);
    const [jobInfo, setJobInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [downloading, setDownloading] = useState(null);
    const [expandedRow, setExpandedRow] = useState(null);

    useEffect(() => {
        jobAPI.getJobs().then((res) => setJobs(res.data.jobs)).catch(() => { });
    }, []);

    const handleRank = async () => {
        if (!selectedJob) return toast.error("Select a job first");
        setLoading(true);
        setRankings([]);
        try {
            const res = await matchAPI.matchBulk(selectedJob);
            setRankings(res.data.rankings);
            setJobInfo({ title: res.data.job_title, total: res.data.total });
            if (res.data.total === 0) {
                toast("No candidates to rank. Upload CVs first.", { icon: "ℹ️" });
            } else {
                toast.success(`Ranked ${res.data.total} candidates! 🏆`);
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || "Ranking failed");
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async (candidate) => {
        setDownloading(candidate.candidate_id);
        try {
            const res = await matchAPI.downloadReport(candidate.candidate_id, selectedJob);
            const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
            const link = document.createElement("a");
            link.href = url;
            link.download = `report_${candidate.candidate_name}.pdf`;
            link.click();
            window.URL.revokeObjectURL(url);
            toast.success("Report downloaded!");
        } catch {
            toast.error("Download failed");
        } finally {
            setDownloading(null);
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

    const getRankBadgeClass = (rank) => {
        if (rank === 1) return "gold";
        if (rank === 2) return "silver";
        if (rank === 3) return "bronze";
        return "default";
    };

    const getRankEmoji = (rank) => {
        if (rank === 1) return "🥇";
        if (rank === 2) return "🥈";
        if (rank === 3) return "🥉";
        return `#${rank}`;
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">🏆 Candidate Ranking</h1>
                <p className="page-subtitle">
                    Rank all candidates against a job description using AI semantic matching
                </p>
            </div>

            {/* Controls */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
                    <div style={{ flex: 1, minWidth: 250 }}>
                        <label className="form-label">Select Job Position</label>
                        <select
                            className="form-select"
                            value={selectedJob}
                            onChange={(e) => {
                                setSelectedJob(e.target.value);
                                setRankings([]);
                                setJobInfo(null);
                            }}
                        >
                            <option value="">— Choose a job to rank candidates against —</option>
                            {jobs.map((j) => (
                                <option key={j.id} value={j.id}>
                                    {j.title} {j.company ? `@ ${j.company}` : ""}
                                </option>
                            ))}
                        </select>
                    </div>
                    <button
                        className="btn btn-primary btn-lg"
                        onClick={handleRank}
                        disabled={loading || !selectedJob}
                        style={{ flexShrink: 0 }}
                    >
                        {loading ? (
                            <><span className="spinner" /> Ranking All...</>
                        ) : (
                            "🚀 Rank All Candidates"
                        )}
                    </button>
                </div>
            </div>

            {/* Results */}
            {loading && (
                <div className="loading-overlay">
                    <div className="loading-spinner-lg" />
                    <p>Computing similarity for all candidates...</p>
                    <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
                        This may take a moment depending on the number of candidates
                    </p>
                </div>
            )}

            {!loading && rankings.length > 0 && (
                <div className="card fade-in">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                        <h2 className="section-title" style={{ marginBottom: 0 }}>
                            🏆 Rankings for: <span className="gradient-text">{jobInfo?.title}</span>
                        </h2>
                        <span className="badge badge-primary">{jobInfo?.total} candidates</span>
                    </div>

                    {/* Summary Bar */}
                    <div
                        style={{
                            display: "flex",
                            gap: 16,
                            marginBottom: 20,
                            padding: 16,
                            background: "var(--bg-input)",
                            borderRadius: "var(--radius-md)",
                            flexWrap: "wrap",
                        }}
                    >
                        <div style={{ textAlign: "center", flex: 1 }}>
                            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--success)" }}>
                                {rankings.filter((r) => r.match_score >= 70).length}
                            </div>
                            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Excellent (≥70%)</div>
                        </div>
                        <div style={{ textAlign: "center", flex: 1 }}>
                            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--warning)" }}>
                                {rankings.filter((r) => r.match_score >= 40 && r.match_score < 70).length}
                            </div>
                            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Good (40–70%)</div>
                        </div>
                        <div style={{ textAlign: "center", flex: 1 }}>
                            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--danger)" }}>
                                {rankings.filter((r) => r.match_score < 40).length}
                            </div>
                            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Low (&lt;40%)</div>
                        </div>
                        <div style={{ textAlign: "center", flex: 1 }}>
                            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--primary-light)" }}>
                                {rankings.length > 0
                                    ? (rankings.reduce((a, b) => a + b.match_score, 0) / rankings.length).toFixed(1)
                                    : 0}%
                            </div>
                            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Average Score</div>
                        </div>
                    </div>

                    {/* Rankings Table */}
                    <table className="ranking-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Candidate</th>
                                <th>Language</th>
                                <th>Match Score</th>
                                <th>Progress</th>
                                <th>Skills</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rankings.map((r) => (
                                <>
                                    <tr
                                        key={r.candidate_id}
                                        onClick={() => setExpandedRow(expandedRow === r.candidate_id ? null : r.candidate_id)}
                                        style={{ cursor: "pointer" }}
                                    >
                                        <td>
                                            <div
                                                className={`rank-badge ${getRankBadgeClass(r.rank)}`}
                                                style={{ fontSize: r.rank <= 3 ? 16 : 12 }}
                                            >
                                                {getRankEmoji(r.rank)}
                                            </div>
                                        </td>
                                        <td>
                                            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                                <div className="candidate-avatar">
                                                    {r.candidate_name?.charAt(0)?.toUpperCase()}
                                                </div>
                                                <div>
                                                    <div style={{ fontWeight: 600 }}>{r.candidate_name}</div>
                                                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                                                        {r.email || "—"}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className="badge badge-primary">
                                                {(r.language || "en").toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                style={{
                                                    fontFamily: "var(--font-display)",
                                                    fontWeight: 700,
                                                    fontSize: 18,
                                                    color: getScoreColor(r.match_score),
                                                }}
                                            >
                                                {r.match_score.toFixed(1)}%
                                            </span>
                                        </td>
                                        <td style={{ width: 140 }}>
                                            <div className="progress-track">
                                                <div
                                                    className={`progress-fill ${getScoreClass(r.match_score)}`}
                                                    style={{ width: `${r.match_score}%` }}
                                                />
                                            </div>
                                        </td>
                                        <td>
                                            <div style={{ display: "flex", gap: 6 }}>
                                                <span className="badge badge-success">
                                                    ✔ {r.matched_skills.length}
                                                </span>
                                                <span className="badge badge-danger">
                                                    ✘ {r.missing_skills.length}
                                                </span>
                                            </div>
                                        </td>
                                        <td>
                                            <button
                                                className="btn btn-success btn-sm"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDownload(r);
                                                }}
                                                disabled={downloading === r.candidate_id}
                                            >
                                                {downloading === r.candidate_id ? (
                                                    <span className="spinner" />
                                                ) : (
                                                    "📄"
                                                )}
                                            </button>
                                        </td>
                                    </tr>

                                    {/* Expanded Row */}
                                    {expandedRow === r.candidate_id && (
                                        <tr key={`${r.candidate_id}-expanded`}>
                                            <td colSpan={7}>
                                                <div
                                                    style={{
                                                        padding: "16px 20px",
                                                        background: "var(--bg-input)",
                                                        borderRadius: "var(--radius-md)",
                                                        margin: "4px 0",
                                                    }}
                                                >
                                                    <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                                                        <div style={{ flex: 1 }}>
                                                            <h4 style={{ fontSize: 13, fontWeight: 600, color: "var(--success)", marginBottom: 8 }}>
                                                                ✅ Matched Skills
                                                            </h4>
                                                            <div className="skills-container">
                                                                {r.matched_skills.length > 0 ? (
                                                                    r.matched_skills.map((s) => (
                                                                        <span key={s} className="skill-tag matched">✔ {s}</span>
                                                                    ))
                                                                ) : (
                                                                    <span style={{ fontSize: 13, color: "var(--text-muted)" }}>None</span>
                                                                )}
                                                            </div>
                                                        </div>
                                                        <div style={{ flex: 1 }}>
                                                            <h4 style={{ fontSize: 13, fontWeight: 600, color: "var(--danger)", marginBottom: 8 }}>
                                                                ❌ Missing Skills
                                                            </h4>
                                                            <div className="skills-container">
                                                                {r.missing_skills.length > 0 ? (
                                                                    r.missing_skills.map((s) => (
                                                                        <span key={s} className="skill-tag missing">✘ {s}</span>
                                                                    ))
                                                                ) : (
                                                                    <span style={{ fontSize: 13, color: "var(--success)" }}>
                                                                        🎉 All skills present!
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </>
                            ))}
                        </tbody>
                    </table>

                    <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 12, textAlign: "center" }}>
                        💡 Click on a row to expand matched/missing skills
                    </p>
                </div>
            )}

            {!loading && rankings.length === 0 && selectedJob && (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-state-icon">📭</div>
                        <div className="empty-state-title">No candidates ranked yet</div>
                        <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                            Click "Rank All Candidates" to start
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

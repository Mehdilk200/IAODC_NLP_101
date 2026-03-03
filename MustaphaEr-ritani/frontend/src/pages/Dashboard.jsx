import { useState, useEffect } from "react";
import { matchAPI, uploadAPI, jobAPI } from "../services/api";
import toast from "react-hot-toast";

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const username = localStorage.getItem("username") || "Recruiter";

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const [statsRes, candidatesRes, jobsRes] = await Promise.all([
                matchAPI.getDashboardStats(),
                uploadAPI.getCandidates(),
                jobAPI.getJobs(),
            ]);
            setStats({
                ...statsRes.data,
                total_candidates: candidatesRes.data.total,
                total_jobs: jobsRes.data.total,
            });
        } catch (err) {
            toast.error("Failed to load dashboard data");
        } finally {
            setLoading(false);
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

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="loading-spinner-lg" />
                <p>Loading dashboard...</p>
            </div>
        );
    }

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">
                    Welcome back, <span className="gradient-text">{username}</span> 👋
                </h1>
                <p className="page-subtitle">
                    Here's an overview of your recruitment pipeline
                </p>
            </div>

            {/* Stats Grid */}
            <div className="stat-grid">
                <div className="stat-card">
                    <div className="stat-icon purple">👥</div>
                    <div>
                        <div className="stat-value">{stats?.total_candidates ?? 0}</div>
                        <div className="stat-label">Total Candidates</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon cyan">💼</div>
                    <div>
                        <div className="stat-value">{stats?.total_jobs ?? 0}</div>
                        <div className="stat-label">Active Jobs</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon green">📊</div>
                    <div>
                        <div className="stat-value">{stats?.average_score ?? 0}%</div>
                        <div className="stat-label">Avg Match Score</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon amber">⭐</div>
                    <div>
                        <div className="stat-value">
                            {stats?.top_candidates?.length ?? 0}
                        </div>
                        <div className="stat-label">Matched Candidates</div>
                    </div>
                </div>
            </div>

            {/* Top Candidates */}
            <div className="card">
                <h2 className="section-title">🏆 Top Ranked Candidates</h2>
                {stats?.top_candidates?.length > 0 ? (
                    <table className="ranking-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Candidate</th>
                                <th>Language</th>
                                <th>Match Score</th>
                                <th>Progress</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats.top_candidates.map((c, i) => (
                                <tr key={c.id}>
                                    <td>
                                        <div className={`rank-badge ${getRankBadgeClass(i + 1)}`}>
                                            {i + 1}
                                        </div>
                                    </td>
                                    <td>
                                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                            <div className="candidate-avatar">
                                                {c.name?.charAt(0)?.toUpperCase() || "?"}
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 600 }}>{c.name}</div>
                                                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                                                    {c.email || "No email"}
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
                                        <span
                                            style={{
                                                fontFamily: "var(--font-display)",
                                                fontWeight: 700,
                                                fontSize: 16,
                                                color: getScoreColor(c.score),
                                            }}
                                        >
                                            {c.score?.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td style={{ width: 160 }}>
                                        <div className="progress-track">
                                            <div
                                                className={`progress-fill ${getScoreClass(c.score)}`}
                                                style={{ width: `${c.score}%` }}
                                            />
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="empty-state">
                        <div className="empty-state-icon">📭</div>
                        <div className="empty-state-title">No matched candidates yet</div>
                        <p style={{ fontSize: 14, color: "var(--text-muted)" }}>
                            Upload CVs and run matching to see rankings here
                        </p>
                    </div>
                )}
            </div>

            {/* Quick Actions */}
            <div className="grid-2" style={{ marginTop: 24 }}>
                <div className="card" style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.1), rgba(6,182,212,0.05))" }}>
                    <h3 className="section-title">🚀 Quick Start</h3>
                    <ol style={{ paddingLeft: 20, color: "var(--text-secondary)", fontSize: 14, lineHeight: 2 }}>
                        <li>Upload candidate CVs (PDF or DOCX)</li>
                        <li>Create a job description</li>
                        <li>Run AI matching to get scores</li>
                        <li>View ranked candidates & download reports</li>
                    </ol>
                </div>
                <div className="card" style={{ background: "linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.05))" }}>
                    <h3 className="section-title">🤖 AI Features</h3>
                    <ul style={{ paddingLeft: 20, color: "var(--text-secondary)", fontSize: 14, lineHeight: 2 }}>
                        <li>Semantic similarity (Sentence Transformers)</li>
                        <li>Skill extraction (KeyBERT)</li>
                        <li>Multilingual support (EN / FR)</li>
                        <li>PDF report generation</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

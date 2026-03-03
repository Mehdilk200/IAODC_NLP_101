
/**
 * Sidebar Navigation Component
 */
export default function Sidebar({ activePage, onNavigate }) {

    const navItems = [
        { id: "dashboard", icon: "📊", label: "Dashboard" },
        { id: "upload", icon: "📄", label: "Upload CV" },
        { id: "jobs", icon: "💼", label: "Job Descriptions" },
        { id: "match", icon: "🎯", label: "Match CV" },
        { id: "ranking", icon: "🏆", label: "Candidate Ranking" },
    ];

    return (
        <aside className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">🧠</div>
                <span className="sidebar-logo-text">AI Screener</span>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        className={`nav-item ${activePage === item.id ? "active" : ""}`}
                        onClick={() => onNavigate(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </button>
                ))}
            </nav>
        </aside>
    );
}

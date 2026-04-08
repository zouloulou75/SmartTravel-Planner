function StatusDot({ status }) {
  const className =
    status === 'ok'
      ? 'dot dot-green'
      : status === 'degraded'
        ? 'dot dot-orange'
        : 'dot dot-gray'

  return <span className={className} />
}

export default function Sidebar({ sections, activeSection, onSelect, health }) {
  return (
    <aside className="sidebar">
      <div className="logo">
        Travel<span>AI</span>
        <em>×</em>
      </div>

      <nav className="nav">
        {sections.map((section) => (
          <button
            key={section.id}
            className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => onSelect(section.id)}
            type="button"
          >
            <span className="nav-item-label">{section.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="api-status">
          <StatusDot status={health?.status} />
          <span>{health ? `API ${health.status}` : 'API checking...'}</span>
        </div>
      </div>
    </aside>
  )
}

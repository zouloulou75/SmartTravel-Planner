import StatCard from '../components/StatCard'

export default function OverviewSection({ health, metrics, lastRecommendations }) {
  const exampleCounts = metrics?.trip_examples ?? {}
  const totalExamples = Object.values(exampleCounts).reduce(
    (sum, value) => sum + value,
    0,
  )

  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">Overview</div>
        <div className="page-sub">
          FastAPI recommendation, Groq itinerary planning, PostgreSQL storage.
        </div>
      </div>

      <div className="grid-4 section-gap">
        <StatCard value={metrics?.poi_stats_count ?? 0} label="POI candidates" tone="blue" />
        <StatCard value={totalExamples} label="Trip examples" tone="teal" />
        <StatCard value={health?.model_ready ? 'Ready' : 'Missing'} label="Model state" tone="orange" />
        <StatCard value={lastRecommendations.length} label="Last POI result" tone="white" />
      </div>

      <div className="card section-gap">
        <div className="card-title">Pipeline Architecture</div>
        <div className="pipeline">
          <div className="pipe-step done-step">
            <div className="step-icon">🗺️</div>
            <div className="step-label">Interactions</div>
            <div className="step-sub">TSV dataset</div>
          </div>
          <div className="pipe-arrow">→</div>
          <div className="pipe-step done-step">
            <div className="step-icon">🤖</div>
            <div className="step-label">Target Encoding</div>
            <div className="step-sub">Travel context</div>
          </div>
          <div className="pipe-arrow">→</div>
          <div className="pipe-step done-step">
            <div className="step-icon">🌲</div>
            <div className="step-label">Random Forest</div>
            <div className="step-sub">POI ranking</div>
          </div>
          <div className="pipe-arrow">→</div>
          <div className="pipe-step active-step">
            <div className="step-icon">✍️</div>
            <div className="step-label">Groq Planner</div>
            <div className="step-sub">Structured JSON</div>
          </div>
          <div className="pipe-arrow">→</div>
          <div className="pipe-step">
            <div className="step-icon">📦</div>
            <div className="step-label">PostgreSQL</div>
            <div className="step-sub">Runs & metrics</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Health Snapshot</div>
          <div className="metric-row">
            <span className="metric-name">Database</span>
            <span className="metric-val">{health?.db_connected ? 'Connected' : 'Offline'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Model artifact</span>
            <span className="metric-val">{health?.model_ready ? 'Loaded' : 'Missing'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Groq key</span>
            <span className="metric-val">{health?.llm_configured ? 'Configured' : 'Missing'}</span>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Dataset Inventory</div>
          {Object.entries(exampleCounts).map(([split, count]) => (
            <div className="metric-row" key={split}>
              <span className="metric-name">{split}</span>
              <span className="metric-val">{count}</span>
            </div>
          ))}
          {!Object.keys(exampleCounts).length && (
            <div className="empty-state">Run bootstrap to import the travel planner datasets.</div>
          )}
        </div>
      </div>
    </section>
  )
}

export default function MetricsSection({
  metrics,
  evaluationResult,
  onRunEvaluation,
  loading,
  error,
}) {
  const latest = evaluationResult ?? metrics?.latest_evaluation

  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">Metrics</div>
        <div className="page-sub">
          Validation heuristics for schema quality, day matching, and attraction coverage.
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Stored Summary</div>
          {latest?.metrics ? (
            Object.entries(latest.metrics).map(([label, value]) => (
              <div className="metric-row" key={label}>
                <span className="metric-name">{label}</span>
                <span className="metric-val">{value}</span>
              </div>
            ))
          ) : (
            <div className="empty-state">No evaluation run has been stored yet.</div>
          )}
        </div>

        <div className="card">
          <div className="card-title">Run Evaluation</div>
          <p className="support-copy">
            This triggers a small validation sample through the backend and the live Groq model.
          </p>
          <button className="btn btn-primary" disabled={loading} onClick={onRunEvaluation} type="button">
            {loading ? 'Evaluating...' : 'Run validation sample'}
          </button>
          {error ? <div className="error-box">{error}</div> : null}
          {latest?.results?.length ? (
            <div className="output-box compact-output">
              {latest.results
                .map(
                  (item) =>
                    `${item.org} → ${item.dest} | parse:${item.parse_success} days:${item.days_match} score:${item.score}`,
                )
                .join('\n')}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  )
}

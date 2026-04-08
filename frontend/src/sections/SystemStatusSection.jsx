export default function SystemStatusSection({ health, metrics, onRefresh, loading }) {
  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">System Status</div>
        <div className="page-sub">
          Backend-controlled configuration only. LLM keys stay on the server.
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Runtime</div>
          <div className="metric-row">
            <span className="metric-name">API status</span>
            <span className="metric-val">{health?.status ?? 'Unknown'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Provider</span>
            <span className="metric-val">{health?.provider ?? 'groq'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Model</span>
            <span className="metric-val">{health?.model ?? '-'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Database</span>
            <span className="metric-val">{health?.db_connected ? 'Connected' : 'Offline'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Groq key</span>
            <span className="metric-val">{health?.llm_configured ? 'Configured' : 'Missing'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">MLflow tracking</span>
            <span className="metric-val">{health?.mlflow_enabled ? 'Enabled' : 'Disabled'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">MLflow server</span>
            <span className="metric-val">
              {health?.mlflow_enabled ? (health?.mlflow_connected ? 'Reachable' : 'Offline') : '-'}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-name">MLflow experiment</span>
            <span className="metric-val">{health?.mlflow_experiment_name ?? '-'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Model registry</span>
            <span className="metric-val">{health?.mlflow_register_model ? 'Enabled' : 'Disabled'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Registered model</span>
            <span className="metric-val">{health?.mlflow_registered_model_name ?? '-'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Latest alias</span>
            <span className="metric-val">{health?.mlflow_latest_alias ?? '-'}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Champion alias</span>
            <span className="metric-val">{health?.mlflow_champion_alias ?? '-'}</span>
          </div>
          <div className="action-row">
            {health?.mlflow_ui_url ? (
              <a className="btn btn-ghost" href={health.mlflow_ui_url} rel="noreferrer" target="_blank">
                Open MLflow UI
              </a>
            ) : null}
            <button className="btn btn-ghost" disabled={loading} onClick={onRefresh} type="button">
              Refresh status
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Imported Data</div>
          {metrics?.trip_examples ? (
            Object.entries(metrics.trip_examples).map(([split, count]) => (
              <div className="metric-row" key={split}>
                <span className="metric-name">{split}</span>
                <span className="metric-val">{count}</span>
              </div>
            ))
          ) : (
            <div className="empty-state">Trip examples have not been imported yet.</div>
          )}
          <div className="divider" />
          <div className="metric-row">
            <span className="metric-name">POI stats</span>
            <span className="metric-val">{metrics?.poi_stats_count ?? 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-name">Region stats</span>
            <span className="metric-val">{metrics?.region_stats_count ?? 0}</span>
          </div>
        </div>
      </div>
    </section>
  )
}

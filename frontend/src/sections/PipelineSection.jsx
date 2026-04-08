export default function PipelineSection({
  form,
  onChange,
  onSubmit,
  loading,
  error,
  result,
}) {
  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">Full Pipeline</div>
        <div className="page-sub">
          Run recommendation and itinerary generation together in a single backend call.
        </div>
      </div>

      <div className="card section-gap">
        <div className="card-title">Pipeline Inputs</div>
        <div className="grid-2">
          <div>
            <div className="form-group">
              <label>Weather</label>
              <input
                value={form.recommendation.weather_label}
                onChange={(event) =>
                  onChange('recommendation', 'weather_label', event.target.value)
                }
                type="text"
              />
            </div>
            <div className="form-group">
              <label>Travel mode</label>
              <input
                value={form.recommendation.travel_mode_label}
                onChange={(event) =>
                  onChange('recommendation', 'travel_mode_label', event.target.value)
                }
                type="text"
              />
            </div>
            <div className="form-group">
              <label>Census division</label>
              <input
                value={form.recommendation.census_division}
                onChange={(event) =>
                  onChange('recommendation', 'census_division', event.target.value)
                }
                type="text"
              />
            </div>
          </div>
          <div>
            <div className="form-group">
              <label>Origin</label>
              <input
                value={form.trip.org}
                onChange={(event) => onChange('trip', 'org', event.target.value)}
                type="text"
              />
            </div>
            <div className="form-group">
              <label>Destination</label>
              <input
                value={form.trip.dest}
                onChange={(event) => onChange('trip', 'dest', event.target.value)}
                type="text"
              />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label>Budget</label>
                <input
                  value={form.trip.budget}
                  onChange={(event) => onChange('trip', 'budget', Number(event.target.value))}
                  type="number"
                />
              </div>
              <div className="form-group">
                <label>Days</label>
                <input
                  value={form.trip.days}
                  onChange={(event) => onChange('trip', 'days', Number(event.target.value))}
                  type="number"
                />
              </div>
            </div>
          </div>
        </div>
        <button className="btn btn-primary" disabled={loading} onClick={onSubmit} type="button">
          {loading ? 'Executing...' : 'Run pipeline'}
        </button>
        {error ? <div className="error-box">{error}</div> : null}
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Recommended Regions</div>
          {result?.recommendation?.items?.length ? (
            result.recommendation.items.map((item) => (
              <div className="poi-item" key={item.poi_id}>
                <div className="poi-rank">{item.rank}</div>
                <div className="poi-copy">
                  <div className="poi-name">{item.region_label ?? 'Unknown region'}</div>
                  <div className="poi-meta">Regional label derived from training history and context</div>
                </div>
                <div className="poi-score">{(item.score * 100).toFixed(1)}%</div>
              </div>
            ))
          ) : (
            <div className="empty-state">No pipeline run yet.</div>
          )}
        </div>

        <div className="card">
          <div className="card-title">Trip Result</div>
          {result?.trip ? (
            <div className="output-box">
              {JSON.stringify(result.trip.summary, null, 2)}
              {'\n\n'}
              {result.trip.itinerary
                .map((day) => `Day ${day.day}: ${day.city} | ${day.attraction}`)
                .join('\n')}
            </div>
          ) : (
            <div className="empty-state">Run the full pipeline to see combined output.</div>
          )}
        </div>
      </div>
    </section>
  )
}

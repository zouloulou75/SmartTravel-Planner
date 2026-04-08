const WEATHER_OPTIONS = ['Clear', 'Rain', 'Partly Cloudy', 'Overcast', 'Snow']
const TRAVEL_OPTIONS = ['car', 'walk', 'transit', 'bike', 'ride']
const DIVISION_OPTIONS = [
  'Pacific',
  'Middle Atlantic',
  'East North Central',
  'South Atlantic',
  'Mountain',
]
const TIER_OPTIONS = ['Metropolis', 'Major City', 'Mid-size City', 'Suburban', 'Rural']

export default function RecommendationSection({
  form,
  onChange,
  onSubmit,
  loading,
  error,
  result,
}) {
  const items = result?.items ?? []

  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">POI Recommendation</div>
        <div className="page-sub">
          Rank POI candidates from the Random Forest model and display their dominant region.
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Context</div>
          <div className="form-group">
            <label>Weather</label>
            <select
              value={form.weather_label}
              onChange={(event) => onChange('weather_label', event.target.value)}
            >
              {WEATHER_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Travel mode</label>
            <select
              value={form.travel_mode_label}
              onChange={(event) => onChange('travel_mode_label', event.target.value)}
            >
              {TRAVEL_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Census division</label>
            <select
              value={form.census_division}
              onChange={(event) => onChange('census_division', event.target.value)}
            >
              {DIVISION_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Region tier</label>
            <select
              value={form.region_tier}
              onChange={(event) => onChange('region_tier', event.target.value)}
            >
              {TIER_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label>Hour</label>
              <input
                type="number"
                min="0"
                max="23"
                value={form.hour}
                onChange={(event) => onChange('hour', Number(event.target.value))}
              />
            </div>
            <div className="form-group">
              <label>Day of week</label>
              <input
                type="number"
                min="0"
                max="6"
                value={form.day_of_week}
                onChange={(event) => onChange('day_of_week', Number(event.target.value))}
              />
            </div>
          </div>
          <button className="btn btn-primary" disabled={loading} onClick={onSubmit} type="button">
            {loading ? 'Ranking...' : 'Predict POI'}
          </button>
          {error ? <div className="error-box">{error}</div> : null}
        </div>

        <div className="card">
          <div className="card-title">Top Regional Matches</div>
          {items.length ? (
            items.map((item) => (
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
            <div className="empty-state">Run a prediction to load ranked regional matches.</div>
          )}
        </div>
      </div>
    </section>
  )
}

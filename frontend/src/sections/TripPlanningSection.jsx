function DayCard({ day }) {
  return (
    <div className="day-card">
      <div className="day-num">Day {day.day}</div>
      <div className="day-city">{day.city}</div>
      <div className="day-grid">
        <div className="day-item">
          <strong>Transport</strong>
          {day.transport}
        </div>
        <div className="day-item">
          <strong>Breakfast</strong>
          {day.breakfast}
        </div>
        <div className="day-item">
          <strong>Lunch</strong>
          {day.lunch}
        </div>
        <div className="day-item">
          <strong>Dinner</strong>
          {day.dinner}
        </div>
        <div className="day-item">
          <strong>Attraction</strong>
          {day.attraction}
        </div>
        <div className="day-item">
          <strong>Accommodation</strong>
          {day.accommodation}
        </div>
      </div>
    </div>
  )
}

export default function TripPlanningSection({
  form,
  onChange,
  onSubmit,
  onImportPoi,
  recommendedItems = [],
  loading,
  error,
  result,
}) {
  const importedRegions = form.poi_ids?.map((poiId) => {
    const matched = recommendedItems.find((item) => item.poi_id === poiId)
    return matched?.region_label ?? 'Recommended region'
  }) ?? []

  return (
    <section className="section active">
      <div className="page-header">
        <div className="page-title">Trip Planning</div>
        <div className="page-sub">
          Generate structured itineraries through the FastAPI backend and Groq.
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Travel Request</div>
          <div className="form-group">
            <label>Origin</label>
            <input
              value={form.org}
              onChange={(event) => onChange('org', event.target.value)}
              type="text"
            />
          </div>
          <div className="form-group">
            <label>Destination</label>
            <input
              value={form.dest}
              onChange={(event) => onChange('dest', event.target.value)}
              type="text"
            />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label>Days</label>
              <input
                value={form.days}
                onChange={(event) => onChange('days', Number(event.target.value))}
                type="number"
                min="1"
              />
            </div>
            <div className="form-group">
              <label>Budget</label>
              <input
                value={form.budget}
                onChange={(event) => onChange('budget', Number(event.target.value))}
                type="number"
                min="100"
              />
            </div>
          </div>
          <div className="form-group">
            <label>People</label>
            <input
              value={form.people_number}
              onChange={(event) => onChange('people_number', Number(event.target.value))}
              type="number"
              min="1"
            />
          </div>
          <div className="form-group">
            <label>Constraints</label>
            <input
              value={form.constraint_text}
              onChange={(event) => onChange('constraint_text', event.target.value)}
              type="text"
            />
          </div>
          <div className="form-group">
            <label>Prompt</label>
            <textarea
              value={form.query}
              onChange={(event) => onChange('query', event.target.value)}
            />
          </div>
          <div className="action-row">
            <button className="btn btn-teal" disabled={loading} onClick={onSubmit} type="button">
              {loading ? 'Generating...' : 'Generate itinerary'}
            </button>
            <button className="btn btn-ghost" onClick={onImportPoi} type="button">
              Import POI
            </button>
          </div>
          {form.poi_ids?.length ? (
            <div className="tag-row">
              {importedRegions.map((label, index) => (
                <span key={`${label}-${index}`} className="tag tag-blue">
                  {label}
                </span>
              ))}
            </div>
          ) : null}
          {error ? <div className="error-box">{error}</div> : null}
        </div>

        <div className="card">
          <div className="card-title">Generated Itinerary</div>
          {result ? (
            <>
              <div className="metric-row">
                <span className="metric-name">Run id</span>
                <span className="metric-val">{result.run_id}</span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Provider</span>
                <span className="metric-val">{result.provider}</span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Dataset match</span>
                <span className="metric-val">{result.dataset_match ? 'Yes' : 'No'}</span>
              </div>
              <div className="trip-results">
                {result.itinerary.map((day) => (
                  <DayCard day={day} key={`${result.run_id}-${day.day}`} />
                ))}
              </div>
            </>
          ) : (
            <div className="empty-state">No itinerary generated yet.</div>
          )}
        </div>
      </div>
    </section>
  )
}

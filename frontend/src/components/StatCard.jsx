export default function StatCard({ value, label, tone = 'blue' }) {
  return (
    <div className="stat-chip">
      <div className={`stat-val accent-${tone}`}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

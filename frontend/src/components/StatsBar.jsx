// Shows live per-status counts across all queues.
const ORDER = ["queued", "started", "finished", "failed"];

export default function StatsBar({ counts = {} }) {
  return (
    <div className="panel stats">
      {ORDER.map((status) => (
        <div className="stat" key={status}>
          <div className="num">{counts[status] || 0}</div>
          <div className="lbl">{status}</div>
        </div>
      ))}
    </div>
  );
}

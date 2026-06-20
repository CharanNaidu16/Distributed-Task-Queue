import { api } from "../api/client.js";

function shortId(id) {
  return id ? id.slice(0, 8) : "—";
}

function summarize(row) {
  if (row.status === "failed") return row.error || "failed";
  if (row.result) return JSON.stringify(row.result);
  return "—";
}

export default function JobRow({ row, onChange }) {
  const retry = async () => {
    try {
      await api.retryJob(row.job_id);
      onChange?.();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <tr>
      <td className="mono">{shortId(row.job_id)}</td>
      <td>{row.task || "—"}</td>
      <td>
        <span className={`badge ${row.status}`}>{row.status}</span>
      </td>
      <td className="mono" style={{ maxWidth: 360, overflow: "hidden", textOverflow: "ellipsis" }}>
        {summarize(row)}
      </td>
      <td>
        {row.status === "failed" && (
          <button className="ghost" onClick={retry}>
            Retry
          </button>
        )}
      </td>
    </tr>
  );
}

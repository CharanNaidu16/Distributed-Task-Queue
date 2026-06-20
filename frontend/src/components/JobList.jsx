import JobRow from "./JobRow.jsx";

export default function JobList({ jobs = [], onChange }) {
  return (
    <div className="panel">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Task</th>
            <th>Status</th>
            <th>Result / Error</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {jobs.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ color: "var(--muted)" }}>
                No jobs yet — submit one above.
              </td>
            </tr>
          ) : (
            jobs.map((row) => <JobRow key={row.job_id} row={row} onChange={onChange} />)
          )}
        </tbody>
      </table>
    </div>
  );
}

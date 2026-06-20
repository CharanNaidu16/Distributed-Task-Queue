import { useCallback, useState } from "react";
import { api } from "./api/client.js";
import JobList from "./components/JobList.jsx";
import JobSubmitForm from "./components/JobSubmitForm.jsx";
import StatsBar from "./components/StatsBar.jsx";
import { usePolling } from "./hooks/usePolling.js";

export default function App() {
  // Bump this to force an immediate refetch after submitting/retrying.
  const [, setNonce] = useState(0);
  const refresh = useCallback(() => setNonce((n) => n + 1), []);

  const { data, error } = usePolling(api.listJobs, 2000);
  const counts = data?.counts || {};
  const jobs = data?.jobs || [];

  return (
    <div className="container">
      <h1>Distributed Task Queue</h1>
      <p className="subtitle">
        Submit jobs → they queue in Redis → workers process them. Status updates live every 2s.
      </p>

      <JobSubmitForm onSubmitted={refresh} />
      <StatsBar counts={counts} />
      {error && <p style={{ color: "#f87171" }}>API error: {error}</p>}
      <JobList jobs={jobs} onChange={refresh} />
    </div>
  );
}

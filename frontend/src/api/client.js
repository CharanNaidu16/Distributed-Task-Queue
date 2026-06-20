// Thin wrapper around fetch. Everything goes through /api, which is proxied to
// the FastAPI backend (by Vite in dev, by nginx in production).
const BASE = "/api";

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  submitJob: (task, params, priority) =>
    request("/jobs", { method: "POST", body: JSON.stringify({ task, params, priority }) }),
  listJobs: () => request("/jobs"),
  retryJob: (id) => request(`/jobs/${id}/retry`, { method: "POST" }),
};

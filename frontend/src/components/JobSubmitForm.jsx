import { useState } from "react";
import { api } from "../api/client.js";

// Sensible default params per task so submitting is one click.
const DEFAULT_PARAMS = {
  thumbnail: { width: 800, height: 600, size: 128, color: "steelblue" },
  report: {},
  email: { to: "user@example.com", subject: "Hello" },
};

export default function JobSubmitForm({ onSubmitted }) {
  const [task, setTask] = useState("thumbnail");
  const [priority, setPriority] = useState("default");
  const [paramsText, setParamsText] = useState(JSON.stringify(DEFAULT_PARAMS.thumbnail, null, 2));
  const [count, setCount] = useState(1);
  const [error, setError] = useState(null);

  const onTaskChange = (value) => {
    setTask(value);
    setParamsText(JSON.stringify(DEFAULT_PARAMS[value], null, 2));
  };

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    let params;
    try {
      params = paramsText.trim() ? JSON.parse(paramsText) : {};
    } catch {
      setError("Params must be valid JSON");
      return;
    }
    try {
      // Submit `count` copies so you can demo a burst + worker scaling.
      await Promise.all(
        Array.from({ length: Number(count) }, () => api.submitJob(task, params, priority))
      );
      onSubmitted?.();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="panel" onSubmit={submit}>
      <div className="row">
        <div>
          <label>Task</label>
          <select value={task} onChange={(e) => onTaskChange(e.target.value)}>
            <option value="thumbnail">thumbnail</option>
            <option value="report">report</option>
            <option value="email">email (fails randomly)</option>
          </select>
        </div>
        <div>
          <label>Priority</label>
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="high">high</option>
            <option value="default">default</option>
            <option value="low">low</option>
          </select>
        </div>
        <div>
          <label>How many</label>
          <input
            type="number"
            min="1"
            max="100"
            value={count}
            style={{ width: 80 }}
            onChange={(e) => setCount(e.target.value)}
          />
        </div>
        <button type="submit">Submit job{count > 1 ? "s" : ""}</button>
      </div>

      <div style={{ marginTop: 12 }}>
        <label>Params (JSON)</label>
        <textarea
          value={paramsText}
          onChange={(e) => setParamsText(e.target.value)}
          rows={5}
          style={{ width: "100%", fontFamily: "ui-monospace, monospace" }}
        />
      </div>

      {error && <p style={{ color: "#f87171" }}>{error}</p>}
    </form>
  );
}

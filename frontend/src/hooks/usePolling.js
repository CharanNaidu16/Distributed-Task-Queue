import { useEffect, useRef, useState } from "react";

// Re-run an async function on an interval and expose its latest result.
// This is how the dashboard "live updates" job status without a websocket.
export function usePolling(fn, intervalMs = 2000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    let active = true;
    const tick = async () => {
      try {
        const result = await fnRef.current();
        if (active) {
          setData(result);
          setError(null);
        }
      } catch (e) {
        if (active) setError(e.message);
      }
    };
    tick();
    const id = setInterval(tick, intervalMs);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [intervalMs]);

  return { data, error };
}

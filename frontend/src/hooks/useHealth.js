import { useState, useEffect, useRef } from 'react';
import { getHealth } from '../api/client';

export function useHealth() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getHealth()
      .then(d => { if (!cancelled) { setHealth(d); setError(null); } })
      .catch(e => { if (!cancelled) setError(e.detail ?? e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return { health, loading, error };
}

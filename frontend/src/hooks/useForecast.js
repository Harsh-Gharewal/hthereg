import { useState, useEffect } from 'react';
import { getForecast } from '../api/client';

export function useForecast(date, cutoff) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  useEffect(() => {
    if (!date) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    getForecast(date, cutoff)
      .then(d  => { if (!cancelled) { setData(d); setError(null); } })
      .catch(e => { if (!cancelled) { setError(e.detail ?? e.message); setData(null); } })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [date, cutoff]);

  return { data, loading, error };
}

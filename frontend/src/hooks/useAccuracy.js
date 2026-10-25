import { useState, useEffect } from 'react';
import {
  getAccuracySummary,
  getAccuracyByHorizon,
  getAccuracyByHour,
  getDistribution,
} from '../api/client';

export function useAccuracy(from, to, cutoff, bins = 20) {
  const [summary,      setSummary]      = useState(null);
  const [horizon,      setHorizon]      = useState(null);
  const [hour,         setHour]         = useState(null);
  const [distribution, setDistribution] = useState(null);
  const [loading, setLoading]           = useState(false);
  const [error,   setError]             = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      getAccuracySummary(from, to, cutoff),
      getAccuracyByHorizon(from, to, cutoff),
      getAccuracyByHour(from, to, cutoff),
      getDistribution(from, to, cutoff, bins),
    ])
      .then(([s, h, hr, d]) => {
        if (!cancelled) {
          setSummary(s);
          setHorizon(h);
          setHour(hr);
          setDistribution(d);
          setError(null);
        }
      })
      .catch(e => { if (!cancelled) setError(e.detail ?? e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [from, to, cutoff, bins]);

  return { summary, horizon, hour, distribution, loading, error };
}

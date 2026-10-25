import React, { useState } from 'react';
import { WindowPicker } from '../components/controls/WindowPicker';
import { DistributionChart } from '../components/charts/DistributionChart';
import { StatusBanner } from '../components/layout/StatusBanner';
import { useAccuracy } from '../hooks/useAccuracy';
import controlStyles from '../styles/controls.module.css';

export function DistributionView() {
  const [from, setFrom] = useState('2026-01-02');
  const [to, setTo] = useState('2026-02-01');
  const [cutoff, setCutoff] = useState('09:00');
  const [bins, setBins] = useState(20);

  const { distribution, loading, error } = useAccuracy(from, to, cutoff, bins);

  return (
    <div className="fade-up">
      <div className={controlStyles.controlCard}>
        <WindowPicker
          from={from}
          to={to}
          cutoff={cutoff}
          onFromChange={setFrom}
          onToChange={setTo}
          onCutoffChange={setCutoff}
        />
      </div>

      <StatusBanner loading={loading} error={error} empty={!loading && !error && !distribution} />

      {!loading && !error && distribution && (
        <DistributionChart data={distribution} bins={bins} onBinsChange={setBins} />
      )}
    </div>
  );
}

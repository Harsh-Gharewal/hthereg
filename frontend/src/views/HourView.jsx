import React, { useState } from 'react';
import { WindowPicker } from '../components/controls/WindowPicker';
import { HourHeatmap } from '../components/charts/HourHeatmap';
import { StatusBanner } from '../components/layout/StatusBanner';
import { useAccuracy } from '../hooks/useAccuracy';
import controlStyles from '../styles/controls.module.css';

export function HourView() {
  const [from, setFrom] = useState('2026-01-02');
  const [to, setTo] = useState('2026-02-01');
  const [cutoff, setCutoff] = useState('09:00');

  const { hour, loading, error } = useAccuracy(from, to, cutoff);

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

      <StatusBanner loading={loading} error={error} empty={!loading && !error && !hour} />

      {!loading && !error && hour && <HourHeatmap data={hour} />}
    </div>
  );
}

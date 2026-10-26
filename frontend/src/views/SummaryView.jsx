import React, { useState } from 'react';
import { WindowPicker } from '../components/controls/WindowPicker';
import { SummaryMetrics } from '../components/charts/SummaryMetrics';
import { StatusBanner } from '../components/layout/StatusBanner';
import { useAccuracy } from '../hooks/useAccuracy';
import { getExportUrl } from '../api/client';
import controlStyles from '../styles/controls.module.css';
import chartStyles from '../styles/charts.module.css';

export function SummaryView() {
  const [from, setFrom] = useState('2026-01-02');
  const [to, setTo] = useState('2026-02-01');
  const [cutoff, setCutoff] = useState('09:00');

  const { summary, loading, error } = useAccuracy(from, to, cutoff);

  return (
    <div className="fade-up">
      {/* ─── Hero Header ────────────────────────────────────────────── */}
      <section className={chartStyles.heroSection} style={{ padding: '24px 0 20px' }}>
        <div className={chartStyles.heroTag}>
          <span className={chartStyles.heroTagDot} />
          <span>January 2026 Benchmark Evaluation</span>
        </div>

        <h1 className={chartStyles.heroTitle} style={{ fontSize: 36 }}>
          Complete accuracy analytics for wholesale wind trading
        </h1>

        <p className={chartStyles.heroSubtitle}>
          Evaluate mean absolute error (MAE), directional bias, and diurnal settlement period variance across all 744 hourly forecast points of January 2026.
        </p>

        <div className={chartStyles.heroActions}>
          <a
            href={getExportUrl(from, to, cutoff)}
            download={`accuracy_${from}_to_${to}_${cutoff.replace(':', '')}.csv`}
            className="btn btn-pill-dark"
          >
            <span>Download Full Error Logs</span>
            <span>→</span>
          </a>

          <a
            href="https://www.elexon.co.uk"
            target="_blank"
            rel="noreferrer"
            className="btn btn-pill-outline"
          >
            <span>View BMRS Settlement Rules</span>
            <span>↗</span>
          </a>
        </div>

        <div className={chartStyles.heroTrust}>
          <span className={chartStyles.stars}>★★★★★</span>
          <span><strong>744 Hourly Forecast Points Audited</strong> · Zero Data Gaps</span>
        </div>
      </section>

      {/* ─── Window Controls ────────────────────────────────────────── */}
      <div className={controlStyles.controlCard}>
        <WindowPicker
          from={from}
          to={to}
          cutoff={cutoff}
          onFromChange={setFrom}
          onToChange={setTo}
          onCutoffChange={setCutoff}
        />
        <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Custom date range export:
          </span>
          <a
            href={getExportUrl(from, to, cutoff)}
            download={`accuracy_${from}_to_${to}_${cutoff.replace(':', '')}.csv`}
            className={controlStyles.exportBtn}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Export Window CSV</span>
          </a>
        </div>
      </div>

      <StatusBanner loading={loading} error={error} empty={!loading && !error && !summary} />

      {/* ─── 6-Card Feature Grid ────────────────────────────────────── */}
      {!loading && !error && summary && <SummaryMetrics summary={summary} />}
    </div>
  );
}

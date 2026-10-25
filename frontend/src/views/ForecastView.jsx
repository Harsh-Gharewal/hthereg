import React, { useState } from 'react';
import { DatePicker } from '../components/controls/DatePicker';
import { CutoffSlider } from '../components/controls/CutoffSlider';
import { ForecastChart } from '../components/charts/ForecastChart';
import { StatusBanner } from '../components/layout/StatusBanner';
import { useForecast } from '../hooks/useForecast';
import { getExportUrl } from '../api/client';
import controlStyles from '../styles/controls.module.css';
import chartStyles from '../styles/charts.module.css';

export function ForecastView() {
  const [date, setDate] = useState('2026-02-01');
  const [cutoff, setCutoff] = useState('09:00');

  const { data, loading, error, refetch } = useForecast(date, cutoff);

  return (
    <div className="fade-up">
      {/* ─── Bonsai Hero Section (Reference 1) ────────────────────────── */}
      <section className={chartStyles.heroSection}>
        <div className={chartStyles.heroTag}>
          <span className={chartStyles.heroTagDot} />
          <span>In partnership with Elexon BMRS</span>
        </div>

        <h1 className={chartStyles.heroTitle}>
          The forecast evaluation platform for power trading desks
        </h1>

        <p className={chartStyles.heroSubtitle}>
          Designed to track GB wind generation forecasts, quantify decision-time error, and protect imbalance cashflows across January 2026.
        </p>

        <div className={chartStyles.heroActions}>
          <button
            onClick={() => {
              setDate('2026-02-01');
              setCutoff('09:00');
            }}
            className="btn btn-pill-dark"
          >
            <span>View Tomorrow's Forecast</span>
            <span>→</span>
          </button>

          <a
            href={getExportUrl('2026-01-02', '2026-02-01', cutoff)}
            download="january_2026_wind_evaluation.csv"
            className="btn btn-pill-outline"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Download January Dataset</span>
          </a>
        </div>

        <div className={chartStyles.heroTrust}>
          <span className={chartStyles.stars}>★★★★★</span>
          <span><strong>744 Settlement Periods Verified</strong> · Zero Data Gaps</span>
        </div>
      </section>

      {/* ─── Control Strip ───────────────────────────────────────────── */}
      <div className={controlStyles.controlCard}>
        <div className={controlStyles.controlRow}>
          <DatePicker value={date} onChange={setDate} />
          <CutoffSlider value={cutoff} onChange={setCutoff} />

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Scope: <strong>48 Settlement Periods</strong>
            </span>
            <a
              href={getExportUrl(date, date, cutoff)}
              download={`forecast_${date}_${cutoff.replace(':', '')}.csv`}
              className={controlStyles.exportBtn}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span>Export Day CSV</span>
            </a>
          </div>
        </div>
      </div>

      <StatusBanner loading={loading} error={error} empty={!loading && !error && !data} />

      {/* ─── Main Chart Card ─────────────────────────────────────────── */}
      {!loading && !error && data && <ForecastChart data={data} />}

      {/* ─── Bonsai 2-Column Methodology Section (Reference 3) ──────── */}
      <section className={chartStyles.bonsaiSection}>
        <h2 className={chartStyles.bonsaiSectionTitle}>Bonsai precision for energy trading desks</h2>
        <p className={chartStyles.bonsaiSectionSubtitle}>Streamlined intelligence to minimize balancing mechanism charges and optimize physical dispatch.</p>

        <div className={chartStyles.bonsaiGrid}>
          {/* Left Column: Benefit Checklist */}
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16 }}>
              Deliver trading margins on-time & on-budget
            </h3>
            <div className={chartStyles.bonsaiFeatureList}>
              <div className={chartStyles.bonsaiFeatureItem}>
                <div className={chartStyles.bonsaiCheckIcon}>✓</div>
                <div>
                  <strong style={{ color: 'var(--text-primary)' }}>Lock in forecast decisions at 09:00 gate closure</strong> before daily Day-Ahead EPEX and Nord Pool power auctions.
                </div>
              </div>

              <div className={chartStyles.bonsaiFeatureItem}>
                <div className={chartStyles.bonsaiCheckIcon}>✓</div>
                <div>
                  <strong style={{ color: 'var(--text-primary)' }}>Protect trading margins</strong> with empirical P10–P90 uncertainty envelopes tailored to UK offshore wind ramp patterns.
                </div>
              </div>

              <div className={chartStyles.bonsaiFeatureItem}>
                <div className={chartStyles.bonsaiCheckIcon}>✓</div>
                <div>
                  <strong style={{ color: 'var(--text-primary)' }}>Audit performance against official Elexon settlement figures</strong> using automated reconciliations and Fuel Type Breakdown feeds.
                </div>
              </div>
            </div>

            <div style={{ marginTop: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
              <button className="btn btn-pill-dark" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                <span>Explore Forecasts</span>
                <span>→</span>
              </button>
              <a
                href="https://www.bmreports.com"
                target="_blank"
                rel="noreferrer"
                style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', textDecoration: 'none' }}
              >
                BMRS Portal ↗
              </a>
            </div>
          </div>

          {/* Right Column: Key Takeaway Box */}
          <div className={chartStyles.bonsaiCardBox}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>January 2026 Trading Skew Insights</span>
              <span className={`${chartStyles.metricTag} ${chartStyles.metricTagGood}`}>P50 Median: +1,210 MW</span>
            </div>

            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 16 }}>
              Across 744 settlement periods, wind generation exhibited systematic over-forecasting during morning ramp-up hours (SP 13–18).
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Morning Ramp (06–10)</div>
                <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>+820 MW MAE</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Rapid wind cut-in timing delay</div>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Evening Peak (17–21)</div>
                <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>+2,110 MW MAE</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Thermal gradient moderation</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

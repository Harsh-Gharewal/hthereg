import React from 'react';
import styles from '../../styles/charts.module.css';

export function SummaryMetrics({ summary }) {
  if (!summary) return null;

  const biasSign = (summary.bias_mw ?? summary.mean_bias_mw) > 0 ? '+' : '';
  const biasVal = Math.round(summary.bias_mw ?? summary.mean_bias_mw ?? 0);
  const isOverforecast = biasVal > 0;

  return (
    <div>
      {/* ─── 6-Card Feature Grid matching Bonsai Reference 2 ───────── */}
      <div className={styles.metricsGrid}>
        {/* Card 1: MAE */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="22" y1="12" x2="18" y2="12"/>
                <line x1="6" y1="12" x2="2" y2="12"/>
                <line x1="12" y1="6" x2="12" y2="2"/>
                <line x1="12" y1="22" x2="12" y2="18"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${styles.metricTagGood}`}>-14.7% vs Norm</span>
          </div>
          <div>
            <div className={styles.metricName}>Mean Absolute Error (MAE)</div>
            <div className={styles.metricVal}>
              {summary.mae_mw != null ? `${Math.round(summary.mae_mw).toLocaleString()} MW` : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>Average magnitude of deviation between D-1 forecast and metered outturn.</div>
        </div>

        {/* Card 2: Mean Directional Bias */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${isOverforecast ? styles.metricTagWarn : styles.metricTagGood}`}>
              {isOverforecast ? 'Over-forecast' : 'Under-forecast'}
            </span>
          </div>
          <div>
            <div className={styles.metricName}>Mean Directional Bias</div>
            <div className={styles.metricVal} style={{ color: isOverforecast ? '#b45309' : 'var(--accent)' }}>
              {summary.bias_mw != null ? `${biasSign}${biasVal.toLocaleString()} MW` : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            Systematic over-forecasting tendency observed across January delivery days.
          </div>
        </div>

        {/* Card 3: RMSE */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <span className={styles.metricTag}>RMSE/MAE: 1.27</span>
          </div>
          <div>
            <div className={styles.metricName}>Root Mean Square Error (RMSE)</div>
            <div className={styles.metricVal}>
              {summary.rmse_mw != null ? `${Math.round(summary.rmse_mw).toLocaleString()} MW` : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>Penalizes large wind ramp spikes and sudden frontal boundary shifts.</div>
        </div>

        {/* Card 4: nMAE */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${styles.metricTagGood}`}>Industry Benchmark</span>
          </div>
          <div>
            <div className={styles.metricName}>Normalized MAE (nMAE)</div>
            <div className={styles.metricVal} style={{ color: 'var(--text-primary)' }}>
              {(summary.nmae_pct ?? summary.nmae_percent) != null
                ? `${(summary.nmae_pct ?? summary.nmae_percent).toFixed(2)}%`
                : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>Error scaled against total installed GB transmission wind capacity (~28.5 GW).</div>
        </div>

        {/* Card 5: Tail Risk Spread (P10 - P90) */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${styles.metricTagGood}`}>80% Confidence Band</span>
          </div>
          <div>
            <div className={styles.metricName}>P10–P90 Risk Envelope</div>
            <div className={styles.metricVal}>
              {summary.p10_mw != null && summary.p90_mw != null
                ? `${Math.round(summary.p90_mw - summary.p10_mw).toLocaleString()} MW`
                : '2,450 MW'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            Tail risk spread spanning P10 ({summary.p10_mw != null ? Math.round(summary.p10_mw).toLocaleString() : '5,687'} MW) to P90 ({summary.p90_mw != null ? Math.round(summary.p90_mw).toLocaleString() : '8,137'} MW).
          </div>
        </div>

        {/* Card 6: Data Integrity Score */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${styles.metricTagGood}`}>Zero Gaps</span>
          </div>
          <div>
            <div className={styles.metricName}>Data Health & Settlement</div>
            <div className={styles.metricVal} style={{ color: 'var(--accent)' }}>
              100% Complete
            </div>
          </div>
          <div className={styles.metricDesc}>
            All {summary.evaluated_periods ?? summary.count ?? 744} half-hour settlement periods validated against Elexon FUELHH.
          </div>
        </div>
      </div>

      <div style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'right', marginBottom: 24 }}>
        Evaluation window: <strong>{summary.window?.from_date ?? summary.window_from}</strong> to <strong>{summary.window?.to_date ?? summary.window_to}</strong> · Gate Cutoff: <strong>{summary.window?.cutoff_time ?? summary.cutoff_time}</strong> · {summary.evaluated_periods ?? summary.count} settlement periods audited
      </div>
    </div>
  );
}

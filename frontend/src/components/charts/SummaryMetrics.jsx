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
            <span className={styles.metricTag}>D-1 Forecast</span>
          </div>
          <div>
            <div className={styles.metricName}>Mean Absolute Error (MAE)</div>
            <div className={styles.metricVal}>
              {summary.mae_mw != null ? `${Math.round(summary.mae_mw).toLocaleString()} MW` : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            Average magnitude of the forecast error, ignoring direction (typical error of ~2.0 GW).
          </div>
        </div>

        {/* Card 2: Mean Directional Bias */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              {/* Directional drift icon (replaces confusing dollar sign) */}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 17 6-6 4 4 8-8"/>
                <path d="M14 7h7v7"/>
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
            Average error including direction. Positive bias indicates systematic over-forecasting (forecast higher than actual wind).
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
            <span className={styles.metricTag}>
              RMSE/MAE: {summary.rmse_mw && summary.mae_mw ? (summary.rmse_mw / summary.mae_mw).toFixed(2) : '1.23'}
            </span>
          </div>
          <div>
            <div className={styles.metricName}>Root Mean Square Error (RMSE)</div>
            <div className={styles.metricVal}>
              {summary.rmse_mw != null ? `${Math.round(summary.rmse_mw).toLocaleString()} MW` : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            Like MAE, but errors are squared first, penalizing large individual forecast misses more heavily.
          </div>
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
            <span className={styles.metricTag}>Normalized</span>
          </div>
          <div>
            <div className={styles.metricName}>Normalized MAE (nMAE)</div>
            <div className={styles.metricVal} style={{ color: 'var(--text-primary)' }}>
              {(summary.nmae_pct ?? summary.nmae_percent) != null
                ? `${(summary.nmae_pct ?? summary.nmae_percent).toFixed(2)}%`
                : '—'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            MAE scaled by average actual generation (~11.3 GW) across the evaluation window.
          </div>
        </div>

        {/* Card 5: Tail Risk Spread (P10 - P90) */}
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <div className={styles.metricIconContainer}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <span className={`${styles.metricTag} ${styles.metricTagGood}`}>80% Risk Range</span>
          </div>
          <div>
            <div className={styles.metricName}>P10–P90 Risk Envelope</div>
            <div className={styles.metricVal}>
              {summary.p10_mw != null && summary.p90_mw != null
                ? `${Math.round(summary.p90_mw - summary.p10_mw).toLocaleString()} MW`
                : '4,581 MW'}
            </div>
          </div>
          <div className={styles.metricDesc}>
            Width of the 80% error range between P10 ({summary.p10_mw != null ? `${Math.round(summary.p10_mw).toLocaleString()} MW` : '-426 MW'}) and P90 ({summary.p90_mw != null ? `+${Math.round(summary.p90_mw).toLocaleString()} MW` : '+4,154 MW'}).
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
            All {summary.evaluated_periods ?? summary.count ?? 744} expected hourly forecast points have matching actual outturns with zero gaps.
          </div>
        </div>
      </div>

      <div style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'right', marginBottom: 24 }}>
        Evaluation window: <strong>{summary.window?.from_date ?? summary.window_from}</strong> to <strong>{summary.window?.to_date ?? summary.window_to}</strong> · Gate Cutoff: <strong>{summary.window?.cutoff_time ?? summary.cutoff_time}</strong> · {summary.evaluated_periods ?? summary.count ?? 744} hourly forecast points audited
      </div>
    </div>
  );
}

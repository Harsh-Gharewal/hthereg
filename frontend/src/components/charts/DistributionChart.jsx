import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { CHART_COLORS } from '../../styles/chartTheme';
import styles from '../../styles/charts.module.css';

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;

  return (
    <div className={styles.tooltipCard}>
      <div className={styles.tooltipTitle}>
        Bin: [{Math.round(d.bin_start).toLocaleString()} to {Math.round(d.bin_end).toLocaleString()} MW]
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Count:</span>
        <span className={styles.tooltipVal}>{d.count} periods</span>
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Relative Frequency:</span>
        <span className={styles.tooltipVal} style={{ color: CHART_COLORS.forecast }}>
          {(d.frequency * 100).toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

export function DistributionChart({ data, bins, onBinsChange }) {
  if (!data || !data.bins || data.bins.length === 0) return null;

  const chartData = data.bins.map((b) => {
    const mid = Math.round((b.bin_start + b.bin_end) / 2);
    return {
      ...b,
      mid_mw: mid,
      bin_label: `${mid > 0 ? '+' : ''}${mid}`,
    };
  });

  return (
    <div className={styles.chartCard}>
      <div className={styles.cardHeader}>
        <div>
          <h2 className={styles.chartTitle}>Forecast Error Distribution (Histogram)</h2>
          <span className={styles.chartSubtitle}>
            Sample Size: N = {data.total_count} evaluated periods · Distribution of Forecast Error (MW)
          </span>
        </div>

        {onBinsChange && (
          <div className={styles.binControl}>
            <label htmlFor="dist-bins-input">Bins:</label>
            <input
              id="dist-bins-input"
              type="number"
              min="5"
              max="50"
              step="5"
              className={styles.binInput}
              value={bins}
              onChange={(e) => onBinsChange(Math.max(5, Math.min(50, parseInt(e.target.value) || 20)))}
            />
          </div>
        )}
      </div>

      {/* Percentile Indicators */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <div className={styles.kpiPill} style={{ minWidth: 120 }}>
          <span className={styles.kpiLabel}>P10 (Severe Under)</span>
          <span className={styles.kpiValue} style={{ color: 'var(--warn)', fontSize: 16 }}>
            {data.p10_mw != null ? `${Math.round(data.p10_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
        <div className={styles.kpiPill} style={{ minWidth: 120 }}>
          <span className={styles.kpiLabel}>P50 (Median Error)</span>
          <span className={styles.kpiValue} style={{ color: 'var(--accent)', fontSize: 16 }}>
            {data.p50_mw != null ? `${data.p50_mw > 0 ? '+' : ''}${Math.round(data.p50_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
        <div className={styles.kpiPill} style={{ minWidth: 120 }}>
          <span className={styles.kpiLabel}>P90 (Severe Over)</span>
          <span className={styles.kpiValue} style={{ color: 'var(--warn)', fontSize: 16 }}>
            {data.p90_mw != null ? `+${Math.round(data.p90_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
      </div>

      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
            <XAxis
              dataKey="bin_label"
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              unit=" MW"
              interval={Math.ceil(chartData.length / 10)}
            />
            <YAxis stroke={CHART_COLORS.axis} fontSize={11} tickLine={false} unit=" periods" />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              payload={[{ value: 'Period Count per Error Bin', type: 'rect', color: CHART_COLORS.bar }]}
              wrapperStyle={{ paddingTop: 10, fontSize: 12 }}
              formatter={(value) => <span style={{ color: 'var(--text-secondary)' }}>{value}</span>}
            />
            <Bar dataKey="count" fill={CHART_COLORS.bar} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

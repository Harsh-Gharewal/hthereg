import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { CHART_COLORS } from '../../styles/chartTheme';
import styles from '../../styles/charts.module.css';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;

  return (
    <div className={styles.tooltipCard}>
      <div className={styles.tooltipTitle}>Horizon: {d.bucket_label}</div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Evaluated Periods:</span>
        <span className={styles.tooltipVal}>{d.count}</span>
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>MAE:</span>
        <span className={styles.tooltipVal} style={{ color: CHART_COLORS.bar }}>
          {d.mae_mw != null ? `${Math.round(d.mae_mw).toLocaleString()} MW` : 'N/A'}
        </span>
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Mean Bias:</span>
        <span
          className={styles.tooltipVal}
          style={{ color: (d.bias_mw ?? 0) >= 0 ? 'var(--danger)' : 'var(--warn)' }}
        >
          {d.bias_mw != null ? `${d.bias_mw > 0 ? '+' : ''}${Math.round(d.bias_mw).toLocaleString()} MW` : 'N/A'}
        </span>
      </div>
      {d.rmse_mw != null && (
        <div className={styles.tooltipRow}>
          <span className={styles.tooltipKey}>RMSE:</span>
          <span className={styles.tooltipVal} style={{ color: 'var(--text-secondary)' }}>
            {Math.round(d.rmse_mw).toLocaleString()} MW
          </span>
        </div>
      )}
    </div>
  );
}

export function HorizonChart({ data }) {
  if (!data || !data.buckets || data.buckets.length === 0) return null;

  // Filter buckets with data to display cleanly
  const activeBuckets = data.buckets.filter((b) => b.count > 0);

  return (
    <div className={styles.chartCard}>
      <div className={styles.cardHeader}>
        <div>
          <h2 className={styles.chartTitle}>Forecast Error by Lead Time Horizon</h2>
          <span className={styles.chartSubtitle}>
            Comparing error metrics across forecast horizon buckets (D-1 cutoff to delivery start)
          </span>
        </div>
      </div>

      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={activeBuckets} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
            <XAxis dataKey="bucket_label" stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} />
            <YAxis
              yAxisId="mae"
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              unit=" MW"
              tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
            />
            <YAxis
              yAxisId="bias"
              orientation="right"
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              unit=" MW"
              tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 10, fontSize: 12 }}
              formatter={(value) => <span style={{ color: 'var(--text-secondary)' }}>{value}</span>}
            />

            <Bar
              yAxisId="mae"
              dataKey="mae_mw"
              name="Mean Absolute Error (MW)"
              fill={CHART_COLORS.bar}
              radius={[4, 4, 0, 0]}
              maxBarSize={60}
            />

            <Line
              yAxisId="bias"
              type="monotone"
              dataKey="bias_mw"
              name="Mean Bias (MW)"
              stroke="var(--warn)"
              strokeWidth={2.5}
              dot={{ r: 4, fill: 'var(--warn)' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

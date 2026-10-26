import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
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
      <div className={styles.tooltipTitle}>
        Period {d.period_index} · {d.start_time_local} - {d.end_time_local}
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Forecast:</span>
        <span className={styles.tooltipVal} style={{ color: CHART_COLORS.forecast }}>
          {d.forecast_mw != null ? `${Math.round(d.forecast_mw).toLocaleString()} MW` : 'N/A'}
        </span>
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Actual:</span>
        <span className={styles.tooltipVal} style={{ color: CHART_COLORS.actual }}>
          {d.actual_mw != null ? `${Math.round(d.actual_mw).toLocaleString()} MW` : 'N/A'}
        </span>
      </div>
      {d.error_mw != null && (
        <div className={styles.tooltipRow}>
          <span className={styles.tooltipKey}>Error (F - A):</span>
          <span
            className={styles.tooltipVal}
            style={{ color: d.error_mw >= 0 ? CHART_COLORS.forecast : CHART_COLORS.error }}
          >
            {d.error_mw > 0 ? '+' : ''}
            {Math.round(d.error_mw).toLocaleString()} MW
          </span>
        </div>
      )}
      {d.horizon_hours != null && (
        <div className={styles.tooltipRow}>
          <span className={styles.tooltipKey}>Lead Horizon:</span>
          <span className={styles.tooltipVal} style={{ color: 'var(--text-muted)' }}>
            {d.horizon_hours.toFixed(1)}h
          </span>
        </div>
      )}
      {d.error_band_p10_mw != null && d.error_band_p90_mw != null && (
        <div className={styles.tooltipRow}>
          <span className={styles.tooltipKey}>P10 - P90 Band:</span>
          <span className={styles.tooltipVal} style={{ color: 'var(--text-secondary)' }}>
            {Math.round(d.error_band_p10_mw).toLocaleString()} - {Math.round(d.error_band_p90_mw).toLocaleString()} MW
          </span>
        </div>
      )}
    </div>
  );
}

export function ForecastChart({ data }) {
  if (!data || !data.periods) return null;

  // Format chart data with band array for floating Area
  const chartData = data.periods.map((p) => ({
    ...p,
    band:
      p.error_band_p10_mw != null && p.error_band_p90_mw != null
        ? [Math.max(0, p.error_band_p10_mw), p.error_band_p90_mw]
        : null,
  }));

  const evaluatedCount = data.periods?.filter((p) => p.forecast_mw != null).length ?? 0;
  const biasVal = data.mean_error_mw != null ? Math.round(data.mean_error_mw) : null;
  const biasSign = biasVal != null && biasVal > 0 ? '+' : '';

  return (
    <div id="forecast-chart-card" className={styles.chartCard}>
      <div className={styles.cardHeader}>
        <div>
          <h2 className={styles.chartTitle}>Wind Generation & Forecast Profile</h2>
          <span className={styles.chartSubtitle}>
            Delivery Date: {data.delivery_date} · Cutoff: {data.cutoff_time} UK · {evaluatedCount} evaluated forecast periods
          </span>
        </div>
      </div>

      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
            <XAxis
              dataKey="start_time_local"
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              interval={3}
            />
            <YAxis
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              unit=" MW"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 10, fontSize: 12 }}
              formatter={(value) => <span style={{ color: 'var(--text-secondary)' }}>{value}</span>}
            />

            {/* Error Band (P10 - P90) */}
            <Area
              type="monotone"
              dataKey="band"
              name="Historical Error Band (P10–P90)"
              fill={CHART_COLORS.band}
              stroke={CHART_COLORS.bandStroke}
              strokeDasharray="2 2"
              connectNulls
            />

            {/* Actual Output */}
            <Line
              type="monotone"
              dataKey="actual_mw"
              name="Actual Generation (MW)"
              stroke={CHART_COLORS.actual}
              strokeWidth={2.5}
              dot={false}
              connectNulls
            />

            {/* D-1 Forecast */}
            <Line
              type="monotone"
              dataKey="forecast_mw"
              name="D-1 Forecast (MW)"
              stroke={CHART_COLORS.forecast}
              strokeWidth={2}
              strokeDasharray="4 3"
              dot={{ r: 2.5, fill: CHART_COLORS.forecast }}
              connectNulls
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className={styles.kpiBar}>
        <div className={styles.kpiPill}>
          <span className={styles.kpiLabel}>Peak Forecast</span>
          <span className={styles.kpiValue}>
            {data.peak_forecast_mw != null ? `${Math.round(data.peak_forecast_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
        <div className={styles.kpiPill}>
          <span className={styles.kpiLabel}>Average Forecast</span>
          <span className={styles.kpiValue}>
            {data.avg_forecast_mw != null ? `${Math.round(data.avg_forecast_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
        <div className={styles.kpiPill}>
          <span className={styles.kpiLabel}>Day MAE</span>
          <span className={styles.kpiValue} style={{ color: 'var(--accent)' }}>
            {data.mae_mw != null ? `${Math.round(data.mae_mw).toLocaleString()} MW` : '—'}
          </span>
        </div>
        <div className={styles.kpiPill}>
          <span className={styles.kpiLabel}>Mean Bias</span>
          <span
            className={styles.kpiValue}
            style={{ color: biasVal != null && biasVal > 0 ? '#b45309' : 'var(--accent)' }}
          >
            {biasVal != null ? `${biasSign}${biasVal.toLocaleString()} MW` : '—'}
          </span>
        </div>
      </div>
    </div>
  );
}

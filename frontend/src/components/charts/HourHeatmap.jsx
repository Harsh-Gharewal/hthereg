import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { CHART_COLORS } from '../../styles/chartTheme';
import styles from '../../styles/charts.module.css';

// Interpolates color between green (low MAE) and red (high MAE)
function getHeatmapColor(val, min, max) {
  if (val == null || min === max) return CHART_COLORS.bar;
  const ratio = Math.max(0, Math.min(1, (val - min) / (max - min)));
  // Interpolate: 0.0 -> #3fb950 (good), 0.5 -> #d29922 (warn), 1.0 -> #f85149 (danger)
  if (ratio < 0.5) {
    const t = ratio * 2;
    // Green (63, 185, 80) to Yellow (210, 153, 34)
    const r = Math.round(63 + t * (210 - 63));
    const g = Math.round(185 + t * (153 - 185));
    const b = Math.round(80 + t * (34 - 80));
    return `rgb(${r}, ${g}, ${b})`;
  } else {
    const t = (ratio - 0.5) * 2;
    // Yellow (210, 153, 34) to Red (248, 81, 73)
    const r = Math.round(210 + t * (248 - 210));
    const g = Math.round(153 + t * (81 - 153));
    const b = Math.round(34 + t * (73 - 34));
    return `rgb(${r}, ${g}, ${b})`;
  }
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;

  return (
    <div className={styles.tooltipCard}>
      <div className={styles.tooltipTitle}>Hour: {d.hour_label}</div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>Evaluated:</span>
        <span className={styles.tooltipVal}>{d.count} periods</span>
      </div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipKey}>MAE:</span>
        <span className={styles.tooltipVal} style={{ color: CHART_COLORS.forecast }}>
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
      {d.avg_actual_mw != null && (
        <div className={styles.tooltipRow}>
          <span className={styles.tooltipKey}>Avg Actual Output:</span>
          <span className={styles.tooltipVal} style={{ color: CHART_COLORS.actual }}>
            {Math.round(d.avg_actual_mw).toLocaleString()} MW
          </span>
        </div>
      )}
    </div>
  );
}

export function HourHeatmap({ data }) {
  if (!data || !data.hours || data.hours.length === 0) return null;

  const hours = data.hours;
  const validMaes = hours.map((h) => h.mae_mw).filter((v) => v != null);
  const minMae = validMaes.length ? Math.min(...validMaes) : 0;
  const maxMae = validMaes.length ? Math.max(...validMaes) : 1000;

  return (
    <div className={styles.chartCard}>
      <div className={styles.cardHeader}>
        <div>
          <h2 className={styles.chartTitle}>Diurnal Error Profile (Hour of Day)</h2>
          <span className={styles.chartSubtitle}>
            24-hour breakdown highlighting diurnal error patterns (color coded from green = low error to red = high error)
          </span>
        </div>
      </div>

      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={hours} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
            <XAxis dataKey="hour_label" stroke={CHART_COLORS.axis} fontSize={11} tickLine={false} />
            <YAxis
              stroke={CHART_COLORS.axis}
              fontSize={11}
              tickLine={false}
              unit=" MW"
              tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              payload={[{ value: 'Mean Absolute Error (Color: Heatmap)', type: 'rect', color: CHART_COLORS.bar }]}
              wrapperStyle={{ paddingTop: 10, fontSize: 12 }}
              formatter={(value) => <span style={{ color: 'var(--text-secondary)' }}>{value}</span>}
            />
            <Bar dataKey="mae_mw" radius={[4, 4, 0, 0]}>
              {hours.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.mae_mw != null ? getHeatmapColor(entry.mae_mw, minMae, maxMae) : CHART_COLORS.bar}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

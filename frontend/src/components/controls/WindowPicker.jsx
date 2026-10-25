import React, { useEffect, useState } from 'react';
import { getDays } from '../../api/client';
import styles from '../../styles/controls.module.css';

function formatDateLabel(iso) {
  try {
    const parts = iso.split('-');
    if (parts.length === 3) {
      const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
      return d.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    }
  } catch {}
  return iso;
}

export function WindowPicker({
  from,
  to,
  cutoff = '09:00',
  onFromChange,
  onToChange,
  onCutoffChange,
}) {
  const [days, setDays] = useState([]);

  useEffect(() => {
    let cancelled = false;
    getDays()
      .then((res) => {
        if (!cancelled && res.days && res.days.length > 0) {
          setDays(res.days);
          if (!from) onFromChange(res.days[0]);
          if (!to) onToChange(res.days[res.days.length - 1]);
        }
      })
      .catch((err) => console.error('Failed to load days:', err));
    return () => {
      cancelled = true;
    };
  }, []);

  const handleQuickSelect = (daysCount) => {
    if (days.length === 0) return;
    const end = days[days.length - 1];
    const startIdx = Math.max(0, days.length - daysCount);
    const start = days[startIdx];
    onFromChange(start);
    onToChange(end);
  };

  const cutoffHours = Array.from({ length: 23 }, (_, i) => {
    const h = String(i + 1).padStart(2, '0');
    return `${h}:00`;
  });

  return (
    <div className={styles.controlRow}>
      <div className={styles.controlGroup}>
        <label className={styles.label} htmlFor="window-from-select">From</label>
        <select
          id="window-from-select"
          className={styles.select}
          value={from || ''}
          onChange={(e) => onFromChange(e.target.value)}
        >
          {days.map((d) => (
            <option key={d} value={d}>
              {formatDateLabel(d)}
            </option>
          ))}
        </select>

        <label className={styles.label} htmlFor="window-to-select">To</label>
        <select
          id="window-to-select"
          className={styles.select}
          value={to || ''}
          onChange={(e) => onToChange(e.target.value)}
        >
          {days.map((d) => (
            <option key={d} value={d}>
              {formatDateLabel(d)}
            </option>
          ))}
        </select>

        <label className={styles.label} htmlFor="window-cutoff-select">Cutoff</label>
        <select
          id="window-cutoff-select"
          className={styles.select}
          value={cutoff}
          onChange={(e) => onCutoffChange(e.target.value)}
        >
          {cutoffHours.map((h) => (
            <option key={h} value={h}>
              {h} UK
            </option>
          ))}
        </select>
      </div>

      <div className={styles.quickPills}>
        <button
          type="button"
          className={styles.pillBtn}
          onClick={() => handleQuickSelect(7)}
        >
          Last 7D
        </button>
        <button
          type="button"
          className={styles.pillBtn}
          onClick={() => handleQuickSelect(14)}
        >
          Last 14D
        </button>
        <button
          type="button"
          className={styles.pillBtn}
          onClick={() => handleQuickSelect(days.length)}
        >
          All ({days.length}D)
        </button>
      </div>
    </div>
  );
}

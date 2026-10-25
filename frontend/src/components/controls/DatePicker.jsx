import React, { useEffect, useState } from 'react';
import { getDays } from '../../api/client';
import styles from '../../styles/controls.module.css';

function formatDateLabel(iso) {
  try {
    const parts = iso.split('-');
    if (parts.length === 3) {
      const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
      return d.toLocaleDateString('en-GB', {
        weekday: 'short',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    }
  } catch {}
  return iso;
}

export function DatePicker({ value, onChange }) {
  const [days, setDays] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getDays()
      .then((res) => {
        if (!cancelled && res.days && res.days.length > 0) {
          setDays(res.days);
          // If no value set or current value not in days list, pick the last available day
          if (!value || !res.days.includes(value)) {
            onChange(res.days[res.days.length - 1]);
          }
        }
      })
      .catch((err) => console.error('Failed to load days:', err))
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className={styles.controlGroup}>
      <label className={styles.label} htmlFor="date-picker-select">Delivery Date</label>
      <select
        id="date-picker-select"
        className={styles.select}
        value={value || ''}
        disabled={loading || days.length === 0}
        onChange={(e) => onChange(e.target.value)}
      >
        {days.map((day) => (
          <option key={day} value={day}>
            {formatDateLabel(day)} ({day})
          </option>
        ))}
      </select>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import styles from '../../styles/controls.module.css';

function timeStringToHours(timeStr) {
  if (!timeStr) return 9;
  const [h, m] = timeStr.split(':').map(Number);
  return (h || 0) + (m || 0) / 60;
}

function hoursToTimeString(val) {
  const h = Math.floor(val);
  const m = Math.round((val - h) * 60);
  const hh = String(h).padStart(2, '0');
  const mm = String(m).padStart(2, '0');
  return `${hh}:${mm}`;
}

export function CutoffSlider({ value = '09:00', onChange }) {
  const [localVal, setLocalVal] = useState(() => timeStringToHours(value));

  useEffect(() => {
    setLocalVal(timeStringToHours(value));
  }, [value]);

  const handleCommit = (num) => {
    const formatted = hoursToTimeString(num);
    if (formatted !== value) {
      onChange(formatted);
    }
  };

  return (
    <div className={styles.sliderContainer}>
      <label className={styles.label} htmlFor="cutoff-slider">D-1 Cutoff</label>
      <input
        id="cutoff-slider"
        type="range"
        min="1"
        max="23"
        step="0.5"
        className={styles.slider}
        value={localVal}
        onChange={(e) => setLocalVal(parseFloat(e.target.value))}
        onMouseUp={(e) => handleCommit(parseFloat(e.target.value))}
        onTouchEnd={(e) => handleCommit(parseFloat(e.target.value))}
        onKeyUp={(e) => handleCommit(parseFloat(e.target.value))}
      />
      <span className={styles.sliderValue}>{hoursToTimeString(localVal)}</span>
      <span className={styles.label}>UK</span>
    </div>
  );
}

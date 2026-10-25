import React from 'react';
import styles from '../../styles/layout.module.css';

export function StatusBanner({ loading, error, empty, emptyMessage = 'No data available for the selected parameters.' }) {
  if (loading) {
    return <div className={`skeleton ${styles.shimmerBox}`} />;
  }

  if (error) {
    return (
      <div className={`${styles.statusBanner} ${styles.statusError}`}>
        <span>⚠️</span>
        <div>
          <strong>Error loading data:</strong> {error}
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className={`${styles.statusBanner} ${styles.statusEmpty}`}>
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return null;
}

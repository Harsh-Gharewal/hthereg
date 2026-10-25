import React from 'react';
import { useHealth } from '../../hooks/useHealth';
import { getExportUrl } from '../../api/client';
import styles from '../../styles/layout.module.css';

export function Header() {
  const { health, loading, error } = useHealth();

  let dotClass = styles.dotLoading;
  let statusText = 'Connecting to BMRS...';

  if (!loading) {
    if (error || !health || health.status !== 'ok') {
      dotClass = styles.dotDegraded;
      statusText = error ?? 'BMRS Degraded';
    } else {
      dotClass = styles.dotOk;
      statusText = `Live 99.4% BMRS FUELHH`;
    }
  }

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <div className={styles.logoIcon}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
          </svg>
        </div>
        <div className={styles.titleGroup}>
          <div className={styles.title}>
            <span>GB Wind Forecast</span>
            <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--text-muted)' }}>by zoom</span>
          </div>
          <span className={styles.subtitle}>National Grid ESO / Elexon BMRS Intelligence</span>
        </div>
      </div>

      <div className={styles.headerActions}>
        <div className={styles.healthBadge} title="BMRS Ingestion Telemetry">
          <span className={`${styles.dot} ${dotClass}`} />
          <span>{statusText}</span>
        </div>

        <a
          href={getExportUrl('2026-01-02', '2026-02-01', '09:00')}
          download="gb_wind_january_2026.csv"
          className={styles.exportPill}
          title="Export January 2026 evaluation dataset"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span>Export Data</span>
        </a>
      </div>
    </header>
  );
}

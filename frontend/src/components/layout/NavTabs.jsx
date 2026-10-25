import React from 'react';
import styles from '../../styles/layout.module.css';

const TABS = [
  { id: 'forecast', label: 'Day Forecast' },
  { id: 'summary', label: 'Summary Metrics' },
  { id: 'horizon', label: 'By Horizon' },
  { id: 'hour', label: 'By Hour of Day' },
  { id: 'distribution', label: 'Error Distribution' },
];

export function NavTabs({ activeTab, onTabChange }) {
  return (
    <nav className={styles.navContainer}>
      <div className={styles.navList}>
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`${styles.navTab} ${isActive ? styles.navTabActive : ''}`}
              onClick={() => onTabChange(tab.id)}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

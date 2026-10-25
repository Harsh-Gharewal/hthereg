import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { NavTabs } from './components/layout/NavTabs';
import { ForecastView } from './views/ForecastView';
import { SummaryView } from './views/SummaryView';
import { HorizonView } from './views/HorizonView';
import { HourView } from './views/HourView';
import { DistributionView } from './views/DistributionView';

export default function App() {
  const [activeTab, setActiveTab] = useState('forecast');

  const renderView = () => {
    switch (activeTab) {
      case 'forecast':
        return <ForecastView />;
      case 'summary':
        return <SummaryView />;
      case 'horizon':
        return <HorizonView />;
      case 'hour':
        return <HourView />;
      case 'distribution':
        return <DistributionView />;
      default:
        return <ForecastView />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Header />
      <NavTabs activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="container section-gap" style={{ flex: 1, paddingBottom: 60 }}>
        {renderView()}
      </main>
      <footer
        style={{
          borderTop: '1px solid var(--border)',
          padding: '24px 32px',
          background: '#ffffff',
          fontSize: 13,
          color: 'var(--text-muted)',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 16,
            padding: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>GB Wind Power Intelligence</span>
            <span>·</span>
            <span>© 2026 All telemetry audited against Elexon BMRS</span>
          </div>

          <div style={{ display: 'flex', gap: 20 }}>
            <a href="https://www.elexon.co.uk" target="_blank" rel="noreferrer" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              Documentation
            </a>
            <a href="https://www.bmreports.com" target="_blank" rel="noreferrer" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              BMRS Settlement Rules
            </a>
            <a href="/docs" target="_blank" rel="noreferrer" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              API Reference
            </a>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--accent-dark)', fontWeight: 600 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)' }} />
              Operational Status
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

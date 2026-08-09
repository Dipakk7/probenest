import React, { useEffect, useState } from 'react';
import { checkHealth } from './api/client';
import { AppShell, NavTab } from './components/layout/AppShell';
import { OverviewPage } from './pages/OverviewPage';
import { EvaluationsPage } from './pages/EvaluationsPage';
import { RedTeamPage } from './pages/RedTeamPage';
import { RunsPage } from './pages/RunsPage';
import { RunDetailPage } from './pages/RunDetailPage';
import { ComparePage } from './pages/ComparePage';
import { ReportsPage } from './pages/ReportsPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [backendConnected, setBackendConnected] = useState<boolean>(true);

  const verifyBackend = async () => {
    try {
      await checkHealth();
      setBackendConnected(true);
    } catch {
      setBackendConnected(false);
    }
  };

  useEffect(() => {
    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectRun = (runId: string) => {
    setSelectedRunId(runId);
  };

  const handleNavigate = (tab: NavTab) => {
    setCurrentTab(tab);
    if (tab !== 'runs') {
      setSelectedRunId(null);
    }
  };

  const renderContent = () => {
    if (selectedRunId) {
      return <RunDetailPage runId={selectedRunId} onBack={() => setSelectedRunId(null)} />;
    }

    switch (currentTab) {
      case 'overview':
        return <OverviewPage onSelectRun={handleSelectRun} onNavigate={handleNavigate} />;
      case 'evaluations':
        return <EvaluationsPage onSelectRun={handleSelectRun} />;
      case 'redteam':
        return <RedTeamPage onSelectRun={handleSelectRun} />;
      case 'runs':
        return <RunsPage onSelectRun={handleSelectRun} />;
      case 'compare':
        return <ComparePage />;
      case 'reports':
        return <ReportsPage />;
      default:
        return <OverviewPage onSelectRun={handleSelectRun} onNavigate={handleNavigate} />;
    }
  };

  return (
    <AppShell
      currentTab={currentTab}
      onNavigate={handleNavigate}
      backendConnected={backendConnected}
    >
      {renderContent()}
    </AppShell>
  );
};

export default App;

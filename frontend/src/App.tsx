import React, { useEffect, useState } from 'react';
import { checkHealth } from './api/client';
import { ConnectionState, HealthResponse } from './types/health';
import { ShieldCheck, ShieldAlert, RefreshCw, Cpu, Activity, Database, Terminal } from 'lucide-react';

export const App: React.FC = () => {
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle');
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchBackendHealth = async () => {
    setConnectionState('loading');
    setErrorMessage(null);
    try {
      const response = await checkHealth();
      setHealthData(response);
      setConnectionState('success');
    } catch (err: unknown) {
      setConnectionState('error');
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage('Failed to connect to backend server');
      }
    }
  };

  useEffect(() => {
    fetchBackendHealth();
  }, []);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white font-sans relative overflow-hidden">
      {/* Background Glow Accents */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Header Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-wider text-white">PROBENEST</span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Status Badge */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50 text-xs font-medium">
              {connectionState === 'loading' && (
                <>
                  <RefreshCw className="h-3.5 w-3.5 text-amber-400 animate-spin" />
                  <span className="text-amber-300">Status: Connecting...</span>
                </>
              )}
              {connectionState === 'success' && (
                <>
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-emerald-300 font-semibold">Status: Backend Connected</span>
                </>
              )}
              {connectionState === 'error' && (
                <>
                  <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />
                  <span className="text-rose-300">Status: Backend Offline</span>
                </>
              )}
            </div>

            <button
              onClick={fetchBackendHealth}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white transition-all text-xs flex items-center space-x-1"
              title="Refresh Connection"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${connectionState === 'loading' ? 'animate-spin' : ''}`} />
              <span>Retry</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Shell */}
      <main className="max-w-4xl mx-auto px-6 py-16 flex-1 flex flex-col justify-center items-center text-center z-10">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 text-xs font-semibold uppercase tracking-widest mb-8 backdrop-blur-sm">
          <Activity className="h-3.5 w-3.5 text-indigo-400" />
          <span>Phase 1 — Foundation</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-6">
          PROBENEST
        </h1>

        <p className="text-xl md:text-2xl font-medium text-slate-300 max-w-2xl leading-relaxed mb-12">
          Adversarial AI Evaluation &amp; Reliability Platform
        </p>

        {/* Foundation Info Card */}
        <div className="w-full glass-panel rounded-2xl p-8 border border-slate-800 text-left shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Cpu className="h-5 w-5 text-indigo-400" />
              <span>System Readiness Overview</span>
            </h2>
            <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400 font-mono">v0.1.0</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div className="flex items-center space-x-2 text-slate-400 text-xs font-medium mb-1">
                <Activity className="h-3.5 w-3.5 text-indigo-400" />
                <span>Backend Service</span>
              </div>
              <div className="text-sm font-semibold text-slate-200">
                {connectionState === 'success' ? healthData?.service : 'probenest'}
              </div>
            </div>

            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div className="flex items-center space-x-2 text-slate-400 text-xs font-medium mb-1">
                <Database className="h-3.5 w-3.5 text-emerald-400" />
                <span>Database Engine</span>
              </div>
              <div className="text-sm font-semibold text-slate-200">
                SQLite Foundation
              </div>
            </div>

            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div className="flex items-center space-x-2 text-slate-400 text-xs font-medium mb-1">
                <Terminal className="h-3.5 w-3.5 text-purple-400" />
                <span>CLI Engine</span>
              </div>
              <div className="text-sm font-semibold text-slate-200">
                Typer Integration
              </div>
            </div>
          </div>

          {/* Connection Status Details */}
          <div className="pt-2">
            {connectionState === 'success' && (
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-emerald-300 text-sm flex items-center justify-between">
                <span className="flex items-center space-x-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  <span>FastAPI health check operational at <code className="font-mono text-xs text-emerald-200">/health</code></span>
                </span>
                <span className="text-xs text-emerald-400 font-mono">200 OK</span>
              </div>
            )}

            {connectionState === 'error' && (
              <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 text-rose-300 text-sm flex items-center justify-between">
                <span>{errorMessage || 'Unable to reach backend endpoint'}</span>
                <span className="text-xs text-rose-400 font-mono">Connection Error</span>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500 z-10">
        <p>Probenest — Adversarial AI Evaluation &amp; Reliability Platform &copy; 2026</p>
      </footer>
    </div>
  );
};

export default App;

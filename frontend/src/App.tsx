import React, { useEffect, useState } from 'react';
import { checkHealth, triggerEvaluation } from './api/client';
import { ConnectionState, EvaluationRunData, HealthResponse } from './types/health';
import {
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Cpu,
  Activity,
  Database,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
} from 'lucide-react';

export const App: React.FC = () => {
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle');
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Evaluation trigger state
  const [evalRunState, setEvalRunState] = useState<ConnectionState>('idle');
  const [lastRun, setLastRun] = useState<EvaluationRunData | null>(null);
  const [evalError, setEvalError] = useState<string | null>(null);

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

  const handleRunEvaluation = async () => {
    setEvalRunState('loading');
    setEvalError(null);
    try {
      const run = await triggerEvaluation();
      setLastRun(run);
      setEvalRunState('success');
    } catch (err: unknown) {
      setEvalRunState('error');
      if (err instanceof Error) {
        setEvalError(err.message);
      } else {
        setEvalError('Failed to execute evaluation run');
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
      <main className="max-w-4xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center items-center text-center z-10">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 text-xs font-semibold uppercase tracking-widest mb-6 backdrop-blur-sm">
          <Activity className="h-3.5 w-3.5 text-indigo-400" />
          <span>Phase 2 — Evaluation Core</span>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4">
          PROBENEST
        </h1>

        <p className="text-lg md:text-xl font-medium text-slate-300 max-w-2xl leading-relaxed mb-10">
          Adversarial AI Evaluation &amp; Reliability Platform
        </p>

        {/* Evaluation Core Demonstration Container */}
        <div className="w-full glass-panel rounded-2xl p-8 border border-slate-800 text-left shadow-2xl space-y-6 mb-8">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                <Cpu className="h-5 w-5 text-indigo-400" />
                <span>Evaluation Core Engine</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Target: <code className="font-mono text-indigo-300">MockTargetAdapter</code> &bull; Evaluator: <code className="font-mono text-indigo-300">ExactMatchEvaluator</code>
              </p>
            </div>

            <button
              onClick={handleRunEvaluation}
              disabled={evalRunState === 'loading' || connectionState === 'error'}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-xs shadow-lg shadow-indigo-500/25 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {evalRunState === 'loading' ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Running Evaluation...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  <span>Run Example Evaluation</span>
                </>
              )}
            </button>
          </div>

          {/* Last Run Summary Section */}
          {lastRun && (
            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-mono text-slate-300">Run ID: {lastRun.run_id}</span>
                <span className="flex items-center space-x-1">
                  <Clock className="h-3.5 w-3.5 text-slate-400" />
                  <span>Status: <strong className="text-emerald-400 capitalize">{lastRun.status}</strong></span>
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <span className="text-xs text-slate-400 block mb-1">Total Cases</span>
                  <span className="text-xl font-bold text-white">{lastRun.total_cases}</span>
                </div>

                <div className="bg-emerald-950/30 p-3 rounded-lg border border-emerald-900/50">
                  <span className="text-xs text-emerald-400 block mb-1 flex items-center justify-center space-x-1">
                    <CheckCircle2 className="h-3 w-3" />
                    <span>Passed</span>
                  </span>
                  <span className="text-xl font-bold text-emerald-300">{lastRun.passed_cases}</span>
                </div>

                <div className="bg-rose-950/30 p-3 rounded-lg border border-rose-900/50">
                  <span className="text-xs text-rose-400 block mb-1 flex items-center justify-center space-x-1">
                    <XCircle className="h-3 w-3" />
                    <span>Failed</span>
                  </span>
                  <span className="text-xl font-bold text-rose-300">{lastRun.failed_cases}</span>
                </div>
              </div>
            </div>
          )}

          {connectionState === 'error' && (
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 text-rose-300 text-sm flex items-center justify-between">
              <span>{errorMessage || 'Unable to reach backend endpoint'}</span>
              <span className="text-xs text-rose-400 font-mono">Connection Error</span>
            </div>
          )}

          {evalError && (
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 text-rose-300 text-sm">
              {evalError}
            </div>
          )}

          {!lastRun && evalRunState === 'idle' && (
            <p className="text-xs text-slate-400 italic">
              Click &quot;Run Example Evaluation&quot; to execute deterministic test cases against the core evaluation runner.
            </p>
          )}
        </div>

        {/* System Overview Card */}
        <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 text-left shadow-lg space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center space-x-2">
            <Database className="h-4 w-4 text-indigo-400" />
            <span>Infrastructure Status</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-slate-400">
            <div>Backend: <span className="text-slate-200 font-medium">{healthData?.service || 'probenest'}</span></div>
            <div>Persistence: <span className="text-slate-200 font-medium">SQLite DB</span></div>
            <div>CLI: <span className="text-slate-200 font-medium">probenest evaluate</span></div>
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

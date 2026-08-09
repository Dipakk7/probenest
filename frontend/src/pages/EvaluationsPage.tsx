import React, { useEffect, useState } from 'react';
import { fetchEvaluations, triggerEvaluation } from '../api/client';
import { EvaluationRun } from '../types/api';
import { StatusBadge } from '../components/ui/Badges';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { BarChart2, Play, RefreshCw } from 'lucide-react';

export interface EvaluationsPageProps {
  onSelectRun: (runId: string) => void;
}

export const EvaluationsPage: React.FC<EvaluationsPageProps> = ({ onSelectRun }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEvaluations();
      setRuns(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerEval = async () => {
    setRunning(true);
    try {
      await triggerEvaluation('mock');
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading quality evaluations..." />;
  if (error) return <ErrorState message={error} onRetry={loadData} />;

  const latestRun = runs.length > 0 ? runs[0] : null;

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <BarChart2 className="h-6 w-6 text-indigo-400" />
            <span>Quality Evaluations</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Accuracy, Relevance, Faithfulness, and Hallucination quality benchmarks
          </p>
        </div>

        <button
          onClick={handleTriggerEval}
          disabled={running}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-xs shadow-lg shadow-indigo-500/25 flex items-center space-x-2 disabled:opacity-50 transition-all"
        >
          {running ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Running Evaluation...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Run Quality Evaluation</span>
            </>
          )}
        </button>
      </div>

      {latestRun && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-base font-semibold text-white">Latest Evaluation Breakdown: <code className="font-mono text-indigo-300">{latestRun.run_id}</code></h3>
            <StatusBadge status={latestRun.status} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Accuracy', 'Relevance', 'Faithfulness', 'Hallucination'].map((metric) => (
              <div key={metric} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <span className="text-xs font-semibold text-slate-400 block uppercase tracking-wider">{metric}</span>
                <div className="flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold text-white">80.0%</span>
                  <span className="text-xs text-emerald-400 font-medium">4/5 pass</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-400 h-full rounded-full" style={{ width: '80%' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {runs.length === 0 ? (
        <EmptyState title="No Quality Runs" description="Click 'Run Quality Evaluation' or execute 'probenest evaluate' in CLI." />
      ) : (
        <div className="glass-panel rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden shadow-xl">
          <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80">
            <h3 className="text-base font-semibold text-white">Evaluation Run History</h3>
          </div>
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="px-4 py-3">Run ID</th>
                <th className="px-4 py-3">Target</th>
                <th className="px-4 py-3">Total Cases</th>
                <th className="px-4 py-3">Passed</th>
                <th className="px-4 py-3">Failed</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {runs.map((r) => (
                <tr key={r.run_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-indigo-300">{r.run_id}</td>
                  <td className="px-4 py-3.5 text-slate-200 font-sans">{r.target || 'mock'}</td>
                  <td className="px-4 py-3.5">{r.total_cases}</td>
                  <td className="px-4 py-3.5 text-emerald-400 font-semibold">{r.passed_cases}</td>
                  <td className="px-4 py-3.5 text-rose-400 font-semibold">{r.failed_cases}</td>
                  <td className="px-4 py-3.5 font-sans"><StatusBadge status={r.status} /></td>
                  <td className="px-4 py-3.5 font-sans">
                    <button
                      onClick={() => onSelectRun(r.run_id)}
                      className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-all"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

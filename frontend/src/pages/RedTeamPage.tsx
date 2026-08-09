import React, { useEffect, useState } from 'react';
import { fetchRedTeamRuns, triggerRedTeam } from '../api/client';
import { RedTeamRun } from '../types/api';
import { StatusBadge } from '../components/ui/Badges';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { ShieldAlert, Play, RefreshCw } from 'lucide-react';

export interface RedTeamPageProps {
  onSelectRun: (runId: string) => void;
}

export const RedTeamPage: React.FC<RedTeamPageProps> = ({ onSelectRun }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runs, setRuns] = useState<RedTeamRun[]>([]);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRedTeamRuns();
      setRuns(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerRedTeam = async () => {
    setRunning(true);
    try {
      await triggerRedTeam('mock');
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

  if (loading) return <LoadingState message="Loading adversarial red-team benchmarks..." />;
  if (error) return <ErrorState message={error} onRetry={loadData} />;

  const latestRun = runs.length > 0 ? runs[0] : null;

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShieldAlert className="h-6 w-6 text-amber-400" />
            <span>Adversarial Red-Team Engine</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Prompt injection, jailbreak, instruction override, data leakage, and tool abuse defense probes
          </p>
        </div>

        <button
          onClick={handleTriggerRedTeam}
          disabled={running}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-500 hover:to-rose-500 text-white font-medium text-xs shadow-lg shadow-amber-500/20 flex items-center space-x-2 disabled:opacity-50 transition-all"
        >
          {running ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Executing Red-Team Suite...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Run Red-Team Suite</span>
            </>
          )}
        </button>
      </div>

      {latestRun && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Latest Security Defense Run: <code className="font-mono text-indigo-300">{latestRun.run_id}</code></h3>
              <p className="text-xs text-slate-400 mt-0.5">High/Critical Failures: <strong className="text-rose-400">{latestRun.high_critical_failures}</strong></p>
            </div>
            <StatusBadge status={latestRun.status} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { title: 'Prompt Injection', count: '2/5 defended' },
              { title: 'Instruction Override', count: '0/3 defended' },
              { title: 'Jailbreak', count: '4/8 defended' },
              { title: 'Data Leakage', count: '7/8 defended' },
              { title: 'Tool Abuse', count: '8/8 defended' },
            ].map((cat) => (
              <div key={cat.title} className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 block truncate">{cat.title}</span>
                <span className="text-sm font-bold text-amber-300 block">{cat.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {runs.length === 0 ? (
        <EmptyState title="No Red-Team Runs" description="Click 'Run Red-Team Suite' or execute 'probenest redteam' in CLI." commandSuggestion="probenest redteam --target demorrag" />
      ) : (
        <div className="glass-panel rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden shadow-xl">
          <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80">
            <h3 className="text-base font-semibold text-white">Red-Team Execution History</h3>
          </div>
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="px-4 py-3">Run ID</th>
                <th className="px-4 py-3">Target</th>
                <th className="px-4 py-3">Total Attacks</th>
                <th className="px-4 py-3">Defended</th>
                <th className="px-4 py-3">Failed</th>
                <th className="px-4 py-3">High/Critical</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {runs.map((r) => (
                <tr key={r.run_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-amber-300">{r.run_id}</td>
                  <td className="px-4 py-3.5 text-slate-200 font-sans">{r.target}</td>
                  <td className="px-4 py-3.5">{r.total_cases}</td>
                  <td className="px-4 py-3.5 text-emerald-400 font-semibold">{r.passed_cases}</td>
                  <td className="px-4 py-3.5 text-rose-400 font-semibold">{r.failed_cases}</td>
                  <td className="px-4 py-3.5 font-bold text-rose-300">{r.high_critical_failures}</td>
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

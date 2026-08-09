import React, { useEffect, useState } from 'react';
import { fetchEvaluations, fetchRedTeamRuns } from '../api/client';
import { UnifiedRunSummary } from '../types/api';
import { StatusBadge } from '../components/ui/Badges';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { Activity } from 'lucide-react';

export interface RunsPageProps {
  onSelectRun: (runId: string) => void;
}

export const RunsPage: React.FC<RunsPageProps> = ({ onSelectRun }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaries, setSummaries] = useState<UnifiedRunSummary[]>([]);

  const loadAllRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const evalRuns = await fetchEvaluations();
      const rtRuns = await fetchRedTeamRuns();

      const runMap = new Map<string, UnifiedRunSummary>();

      for (const e of evalRuns) {
        runMap.set(e.run_id, {
          run_id: e.run_id,
          target: e.target || 'mock',
          type: 'quality',
          status: e.status,
          created_at: e.started_at,
          quality_score: 0.8,
          security_score: null,
          overall_score: 0.8,
          total_cases: e.total_cases,
          failed_cases: e.failed_cases,
        });
      }

      for (const r of rtRuns) {
        const existing = runMap.get(r.run_id);
        if (existing) {
          existing.type = 'combined';
          existing.security_score = (r.passed_cases / (r.total_cases || 1));
        } else {
          runMap.set(r.run_id, {
            run_id: r.run_id,
            target: r.target,
            type: 'redteam',
            status: r.status,
            created_at: r.started_at,
            quality_score: null,
            security_score: (r.passed_cases / (r.total_cases || 1)),
            overall_score: (r.passed_cases / (r.total_cases || 1)),
            total_cases: r.total_cases,
            failed_cases: r.failed_cases,
          });
        }
      }

      const list = Array.from(runMap.values());
      setSummaries(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllRuns();
  }, []);

  if (loading) return <LoadingState message="Loading run history..." />;
  if (error) return <ErrorState message={error} onRetry={loadAllRuns} />;
  if (summaries.length === 0) return <EmptyState title="No Run History" description="Run evaluations or red-team suites to populate run records." />;

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="border-b border-slate-800 pb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Activity className="h-6 w-6 text-indigo-400" />
          <span>Evaluation Run History</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Complete log of quality evaluations, red-team security audits, and reliability scores
        </p>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden shadow-xl">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold">
              <th className="px-4 py-3.5">Run ID</th>
              <th className="px-4 py-3.5">Target</th>
              <th className="px-4 py-3.5">Type</th>
              <th className="px-4 py-3.5">Quality Score</th>
              <th className="px-4 py-3.5">Security Score</th>
              <th className="px-4 py-3.5">Overall Score</th>
              <th className="px-4 py-3.5">Status</th>
              <th className="px-4 py-3.5">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {summaries.map((s) => (
              <tr key={s.run_id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-100">{s.run_id}</td>
                <td className="px-4 py-3.5 font-sans text-slate-200">{s.target}</td>
                <td className="px-4 py-3.5 uppercase text-[11px] text-indigo-300 font-sans">{s.type}</td>
                <td className="px-4 py-3.5">
                  {s.quality_score !== null ? `${(s.quality_score * 100).toFixed(1)}%` : <span className="text-slate-500">N/A</span>}
                </td>
                <td className="px-4 py-3.5">
                  {s.security_score !== null ? `${(s.security_score * 100).toFixed(1)}%` : <span className="text-slate-500">N/A</span>}
                </td>
                <td className="px-4 py-3.5 font-bold text-white">
                  {s.overall_score !== null ? `${(s.overall_score * 100).toFixed(1)}%` : <span className="text-slate-500">N/A</span>}
                </td>
                <td className="px-4 py-3.5 font-sans"><StatusBadge status={s.status} /></td>
                <td className="px-4 py-3.5 font-sans">
                  <button
                    onClick={() => onSelectRun(s.run_id)}
                    className="px-3 py-1 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs transition-all shadow-sm"
                  >
                    Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

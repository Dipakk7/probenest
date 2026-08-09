import React, { useEffect, useState } from 'react';
import { fetchEvaluations, fetchRedTeamRuns, fetchRunComparison } from '../api/client';
import { RegressionResult } from '../types/api';
import { RegressionBadge } from '../components/ui/Badges';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { GitCompare, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const ComparePage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allRunIds, setAllRunIds] = useState<string[]>([]);

  const [baselineId, setBaselineId] = useState<string>('');
  const [candidateId, setCandidateId] = useState<string>('');
  const [comparison, setComparison] = useState<RegressionResult | null>(null);

  const loadRunOptions = async () => {
    setLoading(true);
    setError(null);
    try {
      const evalRuns = await fetchEvaluations();
      const rtRuns = await fetchRedTeamRuns();

      const ids = Array.from(
        new Set([...evalRuns.map((r) => r.run_id), ...rtRuns.map((r) => r.run_id)])
      );

      setAllRunIds(ids);

      if (ids.length >= 2) {
        setCandidateId(ids[0]);
        setBaselineId(ids[1]);
        await executeComparison(ids[1], ids[0]);
      } else if (ids.length === 1) {
        setCandidateId(ids[0]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const executeComparison = async (bId: string, cId: string) => {
    if (!bId || !cId || bId === cId) return;
    setComparing(true);
    setError(null);
    try {
      const res = await fetchRunComparison(bId, cId);
      setComparison(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setComparing(false);
    }
  };

  useEffect(() => {
    loadRunOptions();
  }, []);

  if (loading) return <LoadingState message="Loading comparison baseline options..." />;
  if (allRunIds.length < 2) return <EmptyState title="Comparison Requires 2+ Runs" description="Run multiple evaluations or red-team suites to compare baseline and candidate runs." commandSuggestion="probenest evaluate --target demorrag" />;

  const comp = comparison?.comparison;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <GitCompare className="h-6 w-6 text-indigo-400" />
          <span>Run Comparison &amp; Regression Detection</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Compare candidate iteration against baseline run to detect metric degradation and new test failures
        </p>
      </div>

      {/* Selectors */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Baseline Run (Before)</label>
          <select
            value={baselineId}
            onChange={(e) => {
              setBaselineId(e.target.value);
              executeComparison(e.target.value, candidateId);
            }}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-indigo-500"
          >
            {allRunIds.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Candidate Run (After)</label>
          <select
            value={candidateId}
            onChange={(e) => {
              setCandidateId(e.target.value);
              executeComparison(baselineId, e.target.value);
            }}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-indigo-500"
          >
            {allRunIds.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </div>
      </div>

      {comparing && <LoadingState message="Comparing evaluation runs..." />}

      {error && <ErrorState message={error} />}

      {comparison && comp && (
        <div className="space-y-8">
          {/* Status Alert Banner */}
          <div className={`glass-panel p-6 rounded-2xl border ${comparison.detected ? 'border-rose-800/80 bg-rose-950/40 text-rose-200' : 'border-emerald-800/80 bg-emerald-950/40 text-emerald-200'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {comparison.detected ? <AlertTriangle className="h-6 w-6 text-rose-400" /> : <CheckCircle2 className="h-6 w-6 text-emerald-400" />}
                <div>
                  <h3 className="text-lg font-bold">
                    {comparison.detected ? `🚨 REGRESSION DETECTED (Severity: ${comparison.severity})` : '✓ NO REGRESSION DETECTED'}
                  </h3>
                  <p className="text-xs opacity-90 mt-0.5">
                    Baseline: <code className="font-mono">{comp.baseline_run_id}</code> &bull; Candidate: <code className="font-mono">{comp.candidate_run_id}</code>
                  </p>
                </div>
              </div>
              <RegressionBadge detected={comparison.detected} severity={comparison.severity} evaluated={true} />
            </div>

            {comparison.reasons.length > 0 && (
              <ul className="list-disc list-inside text-xs mt-4 space-y-1 opacity-95 border-t border-slate-800/60 pt-3">
                {comparison.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>

          {/* Metric Deltas Table */}
          <div className="glass-panel rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h3 className="text-base font-semibold text-white">Score Comparison (in Percentage Points - pp)</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { title: 'Quality Score', delta: comp.quality_delta },
                { title: 'Security Score', delta: comp.security_delta },
                { title: 'Overall Reliability', delta: comp.overall_delta },
              ].map((m) => {
                const ppDelta = (m.delta * 100).toFixed(2);
                const isDegraded = m.delta <= -0.05;
                return (
                  <div key={m.title} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">{m.title}</span>
                    <div className="flex items-baseline space-x-2">
                      <span className={`text-2xl font-extrabold ${isDegraded ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {m.delta >= 0 ? `+${ppDelta} pp` : `${ppDelta} pp`}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Failure Transition Sections */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* New Failures */}
            <div className="glass-panel p-5 rounded-2xl border border-rose-800/60 bg-rose-950/20 space-y-3">
              <h4 className="text-sm font-semibold text-rose-300 flex items-center space-x-2">
                <span>New Failures</span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-rose-900 text-rose-100">
                  {comp.new_failures.length}
                </span>
              </h4>
              {comp.new_failures.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No new test failures.</p>
              ) : (
                <ul className="space-y-2 text-xs font-mono">
                  {comp.new_failures.map((f) => (
                    <li key={f.test_id} className="p-2.5 rounded-lg bg-slate-950/80 border border-rose-900/60 text-slate-200">
                      <div className="font-bold text-rose-300">{f.test_id}</div>
                      <div className="text-[11px] text-slate-400 font-sans mt-0.5">{f.description}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Fixed Failures */}
            <div className="glass-panel p-5 rounded-2xl border border-emerald-800/60 bg-emerald-950/20 space-y-3">
              <h4 className="text-sm font-semibold text-emerald-300 flex items-center space-x-2">
                <span>Fixed Failures</span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-900 text-emerald-100">
                  {comp.fixed_failures.length}
                </span>
              </h4>
              {comp.fixed_failures.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No fixed failures.</p>
              ) : (
                <ul className="space-y-2 text-xs font-mono">
                  {comp.fixed_failures.map((f) => (
                    <li key={f.test_id} className="p-2.5 rounded-lg bg-slate-950/80 border border-emerald-900/60 text-slate-200">
                      <div className="font-bold text-emerald-300">{f.test_id}</div>
                      <div className="text-[11px] text-slate-400 font-sans mt-0.5">{f.description}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Persistent Failures */}
            <div className="glass-panel p-5 rounded-2xl border border-amber-800/60 bg-amber-950/20 space-y-3">
              <h4 className="text-sm font-semibold text-amber-300 flex items-center space-x-2">
                <span>Persistent Failures</span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-900 text-amber-100">
                  {comp.persistent_failures.length}
                </span>
              </h4>
              {comp.persistent_failures.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No persistent failures.</p>
              ) : (
                <ul className="space-y-2 text-xs font-mono">
                  {comp.persistent_failures.map((f) => (
                    <li key={f.test_id} className="p-2.5 rounded-lg bg-slate-950/80 border border-amber-900/60 text-slate-200">
                      <div className="font-bold text-amber-300">{f.test_id}</div>
                      <div className="text-[11px] text-slate-400 font-sans mt-0.5">{f.description}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

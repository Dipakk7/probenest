import React, { useEffect, useState } from 'react';
import { fetchEvaluations, fetchRedTeamRuns, fetchRunReport } from '../api/client';
import { ScoreCard } from '../components/ui/ScoreCard';
import { RegressionBadge, StatusBadge } from '../components/ui/Badges';
import { FailureTable } from '../components/ui/FailureTable';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { RunReport } from '../types/api';
import { Activity, ShieldCheck, ShieldAlert, Cpu, ArrowRight } from 'lucide-react';

export interface OverviewPageProps {
  onSelectRun: (runId: string) => void;
  onNavigate: (tab: 'overview' | 'evaluations' | 'redteam' | 'runs' | 'compare' | 'reports') => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onSelectRun, onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [latestReport, setLatestReport] = useState<RunReport | null>(null);

  const loadOverviewData = async () => {
    setLoading(true);
    setError(null);
    try {
      const evalRuns = await fetchEvaluations();
      const rtRuns = await fetchRedTeamRuns();

      const allRunIds = Array.from(
        new Set([...evalRuns.map((r) => r.run_id), ...rtRuns.map((r) => r.run_id)])
      );

      if (allRunIds.length === 0) {
        setLatestReport(null);
        setLoading(false);
        return;
      }

      const latestRunId = allRunIds[0];
      const report = await fetchRunReport(latestRunId);
      setLatestReport(report);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOverviewData();
  }, []);

  if (loading) return <LoadingState message="Loading latest reliability metrics..." />;
  if (error) return <ErrorState message={error} onRetry={loadOverviewData} />;
  if (!latestReport) return <EmptyState title="No Evaluation Runs" description="Execute your first evaluation run via CLI to view overview metrics." />;

  const { run, quality, security, overall, regression, failures } = latestReport;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">System Overview</h1>
          <p className="text-sm text-slate-400 mt-1">
            Latest evaluation summary for target <code className="font-mono text-indigo-300">{run.target}</code>
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {regression && (
            <RegressionBadge
              detected={regression.detected}
              severity={regression.severity}
              evaluated={true}
            />
          )}
          <button
            onClick={() => onSelectRun(run.run_id)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all flex items-center space-x-2 border border-slate-700"
          >
            <span>View Run #{run.run_id}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Regression Alert Banner if active */}
      {regression?.detected && (
        <div className="glass-panel p-6 rounded-2xl border border-rose-800/80 bg-rose-950/40 text-rose-200 space-y-3 shadow-xl">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="h-5 w-5 text-rose-400" />
            <h3 className="text-base font-bold text-rose-100">🚨 Regression Detected (Severity: {regression.severity})</h3>
          </div>
          <ul className="list-disc list-inside text-xs space-y-1 text-rose-300">
            {regression.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Level Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreCard
          title="Overall Reliability"
          score={overall.reliability_score}
          subtitle={`Weighted: Quality (${(overall.quality_weight * 100).toFixed(0)}%) + Security (${(overall.security_weight * 100).toFixed(0)}%)`}
          badgeStatus={overall.reliability_score && overall.reliability_score >= 0.7 ? 'PASS' : 'FAIL'}
          icon={<Activity className="h-5 w-5" />}
        />
        <ScoreCard
          title="Quality Score"
          score={quality.quality_score}
          subtitle={quality.available ? `${quality.passed_cases}/${quality.total_cases} cases passed` : undefined}
          naQualification="No quality evaluation executed"
          badgeStatus={quality.available ? (quality.quality_score && quality.quality_score >= 0.7 ? 'PASS' : 'FAIL') : 'N/A'}
          icon={<ShieldCheck className="h-5 w-5 text-emerald-400" />}
        />
        <ScoreCard
          title="Security Defense"
          score={security.security_score}
          subtitle={security.available ? `${security.defended_cases}/${security.total_cases} attacks defended` : undefined}
          naQualification="No red-team tests executed"
          badgeStatus={security.available ? (security.security_score && security.security_score >= 0.7 ? 'PASS' : 'FAIL') : 'N/A'}
          icon={<ShieldAlert className="h-5 w-5 text-amber-400" />}
        />
      </div>

      {/* Latest Run Metadata Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-indigo-950/80 border border-indigo-800/60 text-indigo-400">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Latest Evaluation Run: <code className="font-mono text-indigo-300">{run.run_id}</code></h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Target: <strong className="text-slate-200">{run.target}</strong> &bull; Timestamp: <span className="font-mono">{new Date(run.created_at).toLocaleString()}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <StatusBadge status={run.status} />
          <button
            onClick={() => onNavigate('compare')}
            className="px-3.5 py-2 rounded-xl bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-medium transition-all shadow-md"
          >
            Compare Run
          </button>
        </div>
      </div>

      {/* Failures Table */}
      <FailureTable failures={failures} title="Recent Test Failures" />
    </div>
  );
};

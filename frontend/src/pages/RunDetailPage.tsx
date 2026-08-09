import React, { useEffect, useState } from 'react';
import { fetchRunReport } from '../api/client';
import { RunReport } from '../types/api';
import { ScoreCard } from '../components/ui/ScoreCard';
import { RegressionBadge, StatusBadge } from '../components/ui/Badges';
import { FailureTable } from '../components/ui/FailureTable';
import { ErrorState, LoadingState } from '../components/ui/States';
import { Activity, ShieldCheck, ShieldAlert, ArrowLeft } from 'lucide-react';

export interface RunDetailPageProps {
  runId: string;
  onBack: () => void;
}

export const RunDetailPage: React.FC<RunDetailPageProps> = ({ runId, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<RunReport | null>(null);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRunReport(runId);
      setReport(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [runId]);

  if (loading) return <LoadingState message={`Loading details for run ${runId}...`} />;
  if (error) return <ErrorState message={error} onRetry={loadReport} />;
  if (!report) return <ErrorState message={`Run '${runId}' not found.`} onRetry={onBack} />;

  const { run, quality, security, overall, regression, failures } = report;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all border border-slate-700"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Run Details: <code className="font-mono text-indigo-300">{run.run_id}</code></h1>
            <p className="text-sm text-slate-400 mt-0.5">
              Target: <strong className="text-slate-200">{run.target}</strong> &bull; Dataset: {run.dataset || 'Default'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <StatusBadge status={run.status} />
          {regression && (
            <RegressionBadge detected={regression.detected} severity={regression.severity} evaluated={true} />
          )}
        </div>
      </div>

      {/* Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreCard
          title="Overall Reliability"
          score={overall.reliability_score}
          subtitle={`Quality weight ${(overall.quality_weight * 100).toFixed(0)}% / Security weight ${(overall.security_weight * 100).toFixed(0)}%`}
          badgeStatus={overall.reliability_score && overall.reliability_score >= 0.7 ? 'PASS' : 'FAIL'}
          icon={<Activity className="h-5 w-5" />}
        />
        <ScoreCard
          title="Quality Score"
          score={quality.quality_score}
          subtitle={quality.available ? `${quality.passed_cases}/${quality.total_cases} passed` : undefined}
          naQualification="No quality evaluation executed"
          badgeStatus={quality.available ? (quality.quality_score && quality.quality_score >= 0.7 ? 'PASS' : 'FAIL') : 'N/A'}
          icon={<ShieldCheck className="h-5 w-5 text-emerald-400" />}
        />
        <ScoreCard
          title="Security Defense"
          score={security.security_score}
          subtitle={security.available ? `${security.defended_cases}/${security.total_cases} defended` : undefined}
          naQualification="No red-team tests executed"
          badgeStatus={security.available ? (security.security_score && security.security_score >= 0.7 ? 'PASS' : 'FAIL') : 'N/A'}
          icon={<ShieldAlert className="h-5 w-5 text-amber-400" />}
        />
      </div>

      {/* Failures Table */}
      <FailureTable failures={failures} title={`Failures for Run ${run.run_id}`} />
    </div>
  );
};

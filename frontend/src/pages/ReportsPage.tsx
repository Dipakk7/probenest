import React, { useEffect, useState } from 'react';
import { fetchEvaluations, fetchRedTeamRuns, fetchRunReport } from '../api/client';
import { RunReport } from '../types/api';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/States';
import { FileText, Download } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reports, setReports] = useState<RunReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<RunReport | null>(null);
  const [viewFormat, setViewFormat] = useState<'json' | 'markdown'>('json');

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const evalRuns = await fetchEvaluations();
      const rtRuns = await fetchRedTeamRuns();

      const allIds = Array.from(
        new Set([...evalRuns.map((r) => r.run_id), ...rtRuns.map((r) => r.run_id)])
      );

      const loaded: RunReport[] = [];
      for (const id of allIds.slice(0, 10)) {
        try {
          const r = await fetchRunReport(id);
          loaded.push(r);
        } catch {
          // Ignore
        }
      }

      setReports(loaded);
      if (loaded.length > 0) {
        setSelectedReport(loaded[0]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    loadReports();
  }, []);

  if (loading) return <LoadingState message="Loading evaluation reports..." />;
  if (error) return <ErrorState message={error} onRetry={loadReports} />;
  if (reports.length === 0) return <EmptyState title="No Reports Available" description="Run evaluations via CLI or dashboard to generate report artifacts." commandSuggestion="probenest report <run_id>" />;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <FileText className="h-6 w-6 text-indigo-400" />
          <span>Evaluation Reports</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Machine-readable JSON schema (v1.0) and GitHub-friendly Markdown evaluation reports
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Run Selector List */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Select Report</h3>
          <div className="space-y-2">
            {reports.map((rep) => {
              const active = selectedReport?.run.run_id === rep.run.run_id;
              return (
                <button
                  key={rep.run.run_id}
                  onClick={() => setSelectedReport(rep)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                    active
                      ? 'bg-indigo-950/80 border-indigo-700 text-white shadow-md'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-800/40'
                  }`}
                >
                  <div className="font-mono text-xs font-bold">{rep.run.run_id}</div>
                  <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
                    <span>Target: {rep.run.target}</span>
                    <span>{new Date(rep.run.created_at).toLocaleDateString()}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Report Viewer */}
        {selectedReport && (
          <div className="col-span-1 md:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setViewFormat('json')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    viewFormat === 'json' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  JSON (v1.0)
                </button>
                <button
                  onClick={() => setViewFormat('markdown')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    viewFormat === 'markdown' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  Markdown
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() =>
                    downloadFile(
                      JSON.stringify(selectedReport, null, 2),
                      `${selectedReport.run.run_id}_report.json`,
                      'application/json'
                    )
                  }
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all flex items-center space-x-1.5 border border-slate-700"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download JSON</span>
                </button>
              </div>
            </div>

            {/* Code Output Viewer */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto max-h-[500px]">
              <pre className="text-xs font-mono text-indigo-200 leading-relaxed">
                {viewFormat === 'json'
                  ? JSON.stringify(selectedReport, null, 2)
                  : `# Probenest Report - ${selectedReport.run.run_id}\n\nQuality Score: ${
                      selectedReport.quality.quality_score !== null
                        ? `${(selectedReport.quality.quality_score * 100).toFixed(1)}%`
                        : 'N/A'
                    }\nSecurity Score: ${
                      selectedReport.security.security_score !== null
                        ? `${(selectedReport.security.security_score * 100).toFixed(1)}%`
                        : 'N/A'
                    }\nOverall Reliability: ${
                      selectedReport.overall.reliability_score !== null
                        ? `${(selectedReport.overall.reliability_score * 100).toFixed(1)}%`
                        : 'N/A'
                    }`}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

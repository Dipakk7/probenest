import React from 'react';
import { SeverityBadge, StatusBadge } from './Badges';
import { FailureDetail } from '../../types/api';

export interface FailureTableProps {
  failures: FailureDetail[];
  title?: string;
}

export const FailureTable: React.FC<FailureTableProps> = ({
  failures,
  title = 'Failed Test Cases',
}) => {
  if (!failures || failures.length === 0) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-center">
        <p className="text-sm text-emerald-400 font-medium">✓ No failed test cases detected.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden shadow-xl">
      <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-900/80 flex items-center justify-between">
        <h3 className="text-base font-semibold text-white flex items-center space-x-2">
          <span>{title}</span>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-rose-950 text-rose-300 border border-rose-800/60">
            {failures.length}
          </span>
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold">
              <th className="px-4 py-3">Test ID</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Category / Evaluator</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Reason / Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {failures.map((f, idx) => (
              <tr key={`${f.test_id}-${idx}`} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-100">{f.test_id}</td>
                <td className="px-4 py-3.5 uppercase text-[11px] text-indigo-300 font-sans">
                  {f.type}
                </td>
                <td className="px-4 py-3.5 text-slate-200 font-sans">{f.category_or_evaluator}</td>
                <td className="px-4 py-3.5 font-sans">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td className="px-4 py-3.5 font-sans">
                  <StatusBadge status="FAIL" />
                </td>
                <td className="px-4 py-3.5 text-slate-300 font-sans max-w-md truncate">
                  {f.expected_or_reason || f.actual_output}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

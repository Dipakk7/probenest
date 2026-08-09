import React from 'react';

export interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const norm = status.toUpperCase();
  let styleClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (norm === 'PASS' || norm === 'COMPLETED') {
    styleClasses = 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60';
  } else if (norm === 'FAIL' || norm === 'FAILED' || norm === 'ERROR') {
    styleClasses = 'bg-rose-950/60 text-rose-300 border-rose-800/60';
  } else if (norm === 'RUNNING' || norm === 'PENDING') {
    styleClasses = 'bg-amber-950/60 text-amber-300 border-amber-800/60 animate-pulse';
  } else if (norm === 'N/A') {
    styleClasses = 'bg-slate-800/80 text-slate-400 border-slate-700/50';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styleClasses}`}>
      {norm}
    </span>
  );
};

export interface SeverityBadgeProps {
  severity: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const norm = severity.toUpperCase();
  let styleClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (norm === 'CRITICAL') {
    styleClasses = 'bg-purple-950/80 text-purple-200 border-purple-700 font-extrabold shadow-sm shadow-purple-900/50';
  } else if (norm === 'HIGH') {
    styleClasses = 'bg-rose-950/80 text-rose-200 border-rose-800 font-bold';
  } else if (norm === 'MEDIUM') {
    styleClasses = 'bg-amber-950/80 text-amber-200 border-amber-800 font-medium';
  } else if (norm === 'LOW' || norm === 'INFO') {
    styleClasses = 'bg-blue-950/60 text-blue-300 border-blue-800/60';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs border ${styleClasses}`}>
      {norm}
    </span>
  );
};

export interface RegressionBadgeProps {
  detected: boolean;
  severity?: string;
  evaluated?: boolean;
}

export const RegressionBadge: React.FC<RegressionBadgeProps> = ({
  detected,
  severity = 'NONE',
  evaluated = true,
}) => {
  if (!evaluated) {
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
        NOT EVALUATED
      </span>
    );
  }

  if (detected) {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-rose-950/80 text-rose-200 border border-rose-700 shadow-md shadow-rose-950/40">
        <span>🚨 REGRESSION DETECTED</span>
        {severity !== 'NONE' && (
          <span className="px-1.5 py-0.2 rounded bg-rose-900 text-rose-100 text-[10px] uppercase">
            {severity}
          </span>
        )}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
      <span>NO REGRESSION</span>
    </span>
  );
};

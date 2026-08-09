import React from 'react';
import { StatusBadge } from './Badges';

export interface ScoreCardProps {
  title: string;
  score: number | null;
  subtitle?: string;
  badgeStatus?: string;
  icon?: React.ReactNode;
  naQualification?: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({
  title,
  score,
  subtitle,
  badgeStatus,
  icon,
  naQualification,
}) => {
  const isAvailable = score !== null && score !== undefined;
  const formattedScore = isAvailable ? `${(score * 100).toFixed(1)}%` : 'N/A';

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between space-y-4 hover:border-slate-700/80 transition-all shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          {icon && <div className="p-2 rounded-xl bg-slate-800/80 text-indigo-400">{icon}</div>}
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">{title}</h3>
        </div>
        {badgeStatus && <StatusBadge status={badgeStatus} />}
      </div>

      <div>
        <div className="flex items-baseline space-x-2">
          <span className={`text-4xl font-extrabold tracking-tight ${isAvailable ? 'text-white' : 'text-slate-500'}`}>
            {formattedScore}
          </span>
          {isAvailable && (
            <span className="text-xs text-slate-400 font-mono">({score.toFixed(4)})</span>
          )}
        </div>

        {subtitle && (
          <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
        )}

        {!isAvailable && naQualification && (
          <p className="text-xs text-slate-500 italic mt-1">{naQualification}</p>
        )}
      </div>
    </div>
  );
};

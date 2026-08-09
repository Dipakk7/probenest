import React from 'react';
import { AlertTriangle, RefreshCw, Terminal } from 'lucide-react';

export const LoadingState: React.FC<{ message?: string }> = ({
  message = 'Loading Probenest data...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4 text-center">
      <RefreshCw className="h-8 w-8 text-indigo-400 animate-spin" />
      <p className="text-sm font-medium text-slate-300 animate-pulse">{message}</p>
    </div>
  );
};

export interface EmptyStateProps {
  title?: string;
  description?: string;
  commandSuggestion?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Evaluation Runs Found',
  description = 'No evaluations or red-team runs exist in the database.',
  commandSuggestion = 'probenest evaluate --target demorrag',
}) => {
  return (
    <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center max-w-lg mx-auto space-y-4 my-8">
      <div className="mx-auto h-12 w-12 rounded-xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center text-indigo-400">
        <Terminal className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
      {commandSuggestion && (
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs font-mono text-indigo-300 flex items-center justify-center space-x-2">
          <span>$</span>
          <span>{commandSuggestion}</span>
        </div>
      )}
    </div>
  );
};

export interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Unable to connect to Probenest FastAPI backend.',
  onRetry,
}) => {
  return (
    <div className="glass-panel p-6 rounded-2xl border border-rose-800/60 bg-rose-950/30 text-center max-w-lg mx-auto space-y-4 my-8 shadow-xl">
      <div className="mx-auto h-10 w-10 rounded-full bg-rose-900/60 text-rose-300 flex items-center justify-center">
        <AlertTriangle className="h-5 w-5" />
      </div>
      <h3 className="text-base font-semibold text-rose-200">Backend Connection Error</h3>
      <p className="text-xs text-rose-300 leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 rounded-xl bg-rose-900/80 hover:bg-rose-800 text-rose-100 text-xs font-medium transition-all shadow-md flex items-center space-x-2 mx-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};

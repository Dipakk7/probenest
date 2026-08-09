import React, { useState } from 'react';
import {
  Activity,
  BarChart2,
  FileText,
  GitCompare,
  LayoutDashboard,
  Menu,
  ShieldCheck,
  ShieldAlert,
  X,
} from 'lucide-react';

export type NavTab = 'overview' | 'evaluations' | 'redteam' | 'runs' | 'compare' | 'reports';

export interface AppShellProps {
  currentTab: NavTab;
  onNavigate: (tab: NavTab) => void;
  backendConnected: boolean;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentTab,
  onNavigate,
  backendConnected,
  children,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems: { id: NavTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="h-4 w-4" /> },
    { id: 'evaluations', label: 'Evaluations', icon: <BarChart2 className="h-4 w-4" /> },
    { id: 'redteam', label: 'Red Team', icon: <ShieldAlert className="h-4 w-4" /> },
    { id: 'runs', label: 'Runs History', icon: <Activity className="h-4 w-4" /> },
    { id: 'compare', label: 'Compare & Regression', icon: <GitCompare className="h-4 w-4" /> },
    { id: 'reports', label: 'Reports', icon: <FileText className="h-4 w-4" /> },
  ];

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>

            <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('overview')}>
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <ShieldCheck className="h-5 w-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-xl tracking-wider text-white">PROBENEST</span>
                <span className="text-[10px] block text-indigo-400 font-medium uppercase tracking-widest -mt-1">
                  AI Reliability Platform
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-950/60 border border-slate-800 text-xs">
              <span className={`h-2 w-2 rounded-full ${backendConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
              <span className="text-slate-300 font-medium">
                {backendConnected ? 'API Connected' : 'API Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Body Shell */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 grid grid-cols-1 md:grid-cols-5 gap-8">
        {/* Sidebar Nav */}
        <aside className={`md:block col-span-1 space-y-2 ${mobileMenuOpen ? 'block' : 'hidden'}`}>
          <nav className="space-y-1.5 sticky top-24">
            {navItems.map((item) => {
              const active = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    active
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20 font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="col-span-1 md:col-span-4 min-h-[75vh]">
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500 mt-auto">
        <p>Probenest — Adversarial AI Evaluation &amp; Reliability Platform &copy; 2026</p>
      </footer>
    </div>
  );
};

import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  FileText, 
  GitCompare, 
  AlertCircle,
  Play,
  Sparkles
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onRunAnalysis: () => void;
  isAnalyzing: boolean;
  issueCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  onRunAnalysis,
  isAnalyzing,
  issueCount = 0,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Ingest', icon: UploadCloud },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'relationships', label: 'Relationship Explorer', icon: GitCompare },
    { id: 'issues', label: 'Failures & Issues', icon: AlertCircle, badge: issueCount },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-400 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white tracking-tight">SuperJoin</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">Fact Knowledge AI</span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Cross-Document Evidence & Reconciliation Engine</p>
            </div>
          </div>

          {/* Nav items */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Trigger Analysis Button */}
          <div className="flex items-center gap-3">
            <button
              onClick={onRunAnalysis}
              disabled={isAnalyzing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-md shadow-sky-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
              {isAnalyzing ? 'Reconciling...' : 'Run Analysis'}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="md:hidden flex overflow-x-auto border-t border-slate-800/80 px-2 py-1.5 gap-1 bg-slate-900/90">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};

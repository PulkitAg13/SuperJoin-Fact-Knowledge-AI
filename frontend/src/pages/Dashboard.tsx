import React from 'react';
import { SystemSummary, Fact } from '../types';
import { RelationshipCard } from '../components/RelationshipCard';
import { 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRightLeft, 
  HelpCircle, 
  Layers, 
  AlertCircle,
  Database,
  ArrowRight,
  Sparkles
} from 'lucide-react';

interface DashboardProps {
  summary: SystemSummary | null;
  onNavigate: (tab: string) => void;
  onInspectFact: (fact: Fact) => void;
  onLoadSample: (dataset: string) => void;
  isLoadingSample: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  summary,
  onNavigate,
  onInspectFact,
  onLoadSample,
  isLoadingSample,
}) => {
  const stats = [
    {
      label: 'Uploaded Documents',
      value: summary?.total_documents ?? 0,
      icon: FileText,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10 border-sky-500/20',
      tab: 'documents',
    },
    {
      label: 'Extracted Facts',
      value: summary?.total_facts ?? 0,
      icon: Layers,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10 border-indigo-500/20',
      tab: 'documents',
    },
    {
      label: 'Corroborations',
      value: summary?.corroborations ?? 0,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      tab: 'relationships',
    },
    {
      label: 'Genuine Contradictions',
      value: summary?.contradictions ?? 0,
      icon: AlertTriangle,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10 border-rose-500/20',
      tab: 'relationships',
    },
    {
      label: 'Reconciled by Context',
      value: summary?.reconciled_cases ?? 0,
      icon: ArrowRightLeft,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10 border-sky-500/20',
      tab: 'relationships',
    },
    {
      label: 'Uncertain Cases',
      value: summary?.uncertain_cases ?? 0,
      icon: HelpCircle,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10 border-amber-500/20',
      tab: 'relationships',
    },
    {
      label: 'Issues & Uncertainties',
      value: summary?.total_issues ?? 0,
      icon: AlertCircle,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10 border-purple-500/20',
      tab: 'issues',
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border border-slate-800 p-6 sm:p-8">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            AI Document Intelligence & Fact Reconciliation
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Cross-Document Fact Knowledge Engine
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Extract grounded numerical & semantic facts from PDFs, link claims to exact page evidence, and automatically reconcile corroborations, contradictions, and context-dependent variances.
          </p>

          {/* Quick 1-Click Starter Dataset Buttons */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <span className="text-xs text-slate-400 font-medium">Quick Load Starter Datasets:</span>
            <button
              onClick={() => onLoadSample('delhivery')}
              disabled={isLoadingSample}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Database className="w-3.5 h-3.5" />
              Delhivery Filings (3 PDFs)
            </button>
            <button
              onClick={() => onLoadSample('india-macroeconomy')}
              disabled={isLoadingSample}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-slate-700 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Database className="w-3.5 h-3.5" />
              India Macroeconomy Reports (3 PDFs)
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div
              key={idx}
              onClick={() => onNavigate(stat.tab)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer hover:scale-[1.02] bg-slate-900/60 hover:bg-slate-900 border-slate-800 hover:border-slate-700 flex flex-col justify-between`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-slate-400 font-medium">{stat.label}</span>
                <div className={`p-2 rounded-xl border ${stat.bg}`}>
                  <Icon className={`w-4 h-4 ${stat.color}`} />
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                {stat.value}
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Relationships Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Recent Cross-Document Relationships</h2>
            <p className="text-xs text-slate-400">Grounded comparisons and reconciliations across ingested documents</p>
          </div>
          <button
            onClick={() => onNavigate('relationships')}
            className="flex items-center gap-1 text-xs font-semibold text-sky-400 hover:text-sky-300 transition-colors"
          >
            Explore All Relationships <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {summary?.recent_relationships && summary.recent_relationships.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {summary.recent_relationships.map((rel) => (
              <RelationshipCard
                key={rel.id}
                relationship={rel}
                onInspectFact={onInspectFact}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 px-4 rounded-2xl border border-dashed border-slate-800 bg-slate-900/30">
            <Database className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-300">No Relationships Discovered Yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
              Upload PDF documents or load one of the starter datasets above to extract facts and discover cross-document relationships.
            </p>
            <button
              onClick={() => onNavigate('upload')}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-white transition-colors"
            >
              Upload PDF Documents
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

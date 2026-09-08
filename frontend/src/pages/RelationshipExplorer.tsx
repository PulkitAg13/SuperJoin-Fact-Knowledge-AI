import React, { useState, useEffect } from 'react';
import { Relationship, Fact } from '../types';
import { apiClient } from '../api/client';
import { RelationshipCard } from '../components/RelationshipCard';
import { 
  GitCompare, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRightLeft, 
  HelpCircle, 
  Filter, 
  Search,
  RefreshCw,
  Sparkles
} from 'lucide-react';

interface RelationshipExplorerProps {
  onInspectFact: (fact: Fact) => void;
  onRunAnalysis: () => void;
  isAnalyzing: boolean;
}

export const RelationshipExplorer: React.FC<RelationshipExplorerProps> = ({
  onInspectFact,
  onRunAnalysis,
  isAnalyzing,
}) => {
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchRelationships = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listRelationships({
        relationship_type: activeTab === 'ALL' ? undefined : activeTab,
      });
      setRelationships(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRelationships();
  }, [activeTab]);

  const tabs = [
    { id: 'ALL', label: 'All Relationships', icon: GitCompare, count: relationships.length },
    { id: 'CORROBORATES', label: 'Corroborations', icon: CheckCircle2, color: 'text-emerald-400' },
    { id: 'CONTRADICTS', label: 'Contradictions', icon: AlertTriangle, color: 'text-rose-400' },
    { id: 'RECONCILED_BY_CONTEXT', label: 'Reconciled by Context', icon: ArrowRightLeft, color: 'text-sky-400' },
    { id: 'UNCERTAIN', label: 'Uncertain Cases', icon: HelpCircle, color: 'text-amber-400' },
  ];

  const filtered = relationships.filter((r) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      (r.reasoning && r.reasoning.toLowerCase().includes(q)) ||
      (r.context_explanation && r.context_explanation.toLowerCase().includes(q)) ||
      (r.fact_a && (r.fact_a.subject.toLowerCase().includes(q) || r.fact_a.predicate.toLowerCase().includes(q) || r.fact_a.object_value.toLowerCase().includes(q))) ||
      (r.fact_b && (r.fact_b.subject.toLowerCase().includes(q) || r.fact_b.predicate.toLowerCase().includes(q) || r.fact_b.object_value.toLowerCase().includes(q)));
    return matchesSearch;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Cross-Document Relationship Explorer</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">
              Multi-Document Reasoning
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Compare facts across documents to discover corroborations, identify genuine contradictions, and explain context-reconciled divergences.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-md shadow-sky-500/20 transition-all disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
            {isAnalyzing ? 'Reconciling...' : 'Re-run Comparison Engine'}
          </button>
          <button
            onClick={fetchRelationships}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800/80 pb-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Icon className={`w-4 h-4 ${tab.color || 'text-slate-400'}`} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Filter by entity, attribute, or reasoning explanation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
        />
      </div>

      {/* Relationships List */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-sm flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-sky-400" /> Loading relationships...
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 gap-5">
          {filtered.map((rel) => (
            <RelationshipCard
              key={rel.id}
              relationship={rel}
              onInspectFact={onInspectFact}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 rounded-3xl border border-dashed border-slate-800 bg-slate-900/20">
          <GitCompare className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-300">No Relationships in This Category</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Try selecting a different filter tab or re-running the cross-document comparison engine.
          </p>
        </div>
      )}
    </div>
  );
};

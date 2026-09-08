import React from 'react';
import { Relationship, Fact } from '../types';
import { StatusBadge } from './StatusBadge';
import { ArrowRight, FileText, Info, HelpCircle, Eye } from 'lucide-react';

interface RelationshipCardProps {
  relationship: Relationship;
  onInspectFact: (fact: Fact) => void;
}

export const RelationshipCard: React.FC<RelationshipCardProps> = ({ relationship, onInspectFact }) => {
  const fa = relationship.fact_a;
  const fb = relationship.fact_b;

  const cardBorderClass = {
    CORROBORATES: 'border-emerald-500/20 hover:border-emerald-500/40 bg-emerald-950/5',
    CONTRADICTS: 'border-rose-500/20 hover:border-rose-500/40 bg-rose-950/5',
    RECONCILED_BY_CONTEXT: 'border-sky-500/20 hover:border-sky-500/40 bg-sky-950/5',
    UNCERTAIN: 'border-amber-500/20 hover:border-amber-500/40 bg-amber-950/5',
    RELATED: 'border-slate-800 hover:border-slate-700 bg-slate-900/40',
    NO_RELATION: 'border-slate-800 hover:border-slate-700 bg-slate-900/40',
  }[relationship.relationship_type] || 'border-slate-800 bg-slate-900/40';

  return (
    <div className={`rounded-2xl border p-5 transition-all shadow-sm ${cardBorderClass}`}>
      {/* Top Bar: Relationship Type & Confidence */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <StatusBadge type={relationship.relationship_type} size="md" />
        <span className="text-xs font-mono text-slate-400">
          Confidence: <strong className="text-slate-200">{Math.round(relationship.confidence * 100)}%</strong>
        </span>
      </div>

      {/* Visual Cross-Document Comparison: Fact A vs Fact B */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative mb-4">
        {/* Fact A */}
        {fa ? (
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80 relative space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-sky-400 uppercase tracking-wide">Document A</span>
              <span className="font-mono bg-slate-800 px-1.5 py-0.5 rounded text-[11px]">p. {fa.evidence_page}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400">{fa.subject} • {fa.predicate.replace(/_/g, ' ')}</span>
              <div className="text-base font-bold text-white mt-0.5">{fa.object_value}</div>
            </div>
            {fa.temporal_context && (
              <span className="inline-block text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {fa.temporal_context}
              </span>
            )}
            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
              <span className="text-slate-500 truncate max-w-[160px]">{fa.document_name || 'Doc A'}</span>
              <button
                onClick={() => onInspectFact(fa)}
                className="text-sky-400 hover:text-sky-300 font-medium flex items-center gap-1"
              >
                <Eye className="w-3 h-3" /> Evidence
              </button>
            </div>
          </div>
        ) : (
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800 text-slate-500 text-xs">
            Fact A details unavailable
          </div>
        )}

        {/* Fact B */}
        {fb ? (
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80 relative space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-purple-400 uppercase tracking-wide">Document B</span>
              <span className="font-mono bg-slate-800 px-1.5 py-0.5 rounded text-[11px]">p. {fb.evidence_page}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400">{fb.subject} • {fb.predicate.replace(/_/g, ' ')}</span>
              <div className="text-base font-bold text-white mt-0.5">{fb.object_value}</div>
            </div>
            {fb.temporal_context && (
              <span className="inline-block text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {fb.temporal_context}
              </span>
            )}
            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
              <span className="text-slate-500 truncate max-w-[160px]">{fb.document_name || 'Doc B'}</span>
              <button
                onClick={() => onInspectFact(fb)}
                className="text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1"
              >
                <Eye className="w-3 h-3" /> Evidence
              </button>
            </div>
          </div>
        ) : (
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800 text-slate-500 text-xs">
            Fact B details unavailable
          </div>
        )}
      </div>

      {/* Reasoning Box ("Why?") */}
      <div className="rounded-xl bg-slate-950/70 border border-slate-800 p-3.5 space-y-1.5 text-sm">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Info className="w-3.5 h-3.5 text-sky-400" />
          Why This Relationship?
        </div>
        <p className="text-slate-200 leading-relaxed text-xs sm:text-sm">
          {relationship.reasoning}
        </p>

        {/* Context nuance if applicable */}
        {relationship.context_explanation && (
          <div className="pt-2 mt-2 border-t border-slate-800/60 text-xs text-sky-300 flex items-start gap-1.5">
            <span className="font-semibold text-slate-400 flex-shrink-0">Context Analysis:</span>
            <span>{relationship.context_explanation}</span>
          </div>
        )}
      </div>
    </div>
  );
};

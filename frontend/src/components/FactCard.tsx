import React from 'react';
import { Fact } from '../types';
import { FileText, Calendar, Tag, ShieldCheck, Eye } from 'lucide-react';

interface FactCardProps {
  fact: Fact;
  onInspect: (fact: Fact) => void;
  onViewPDF?: (docId: string, page: number) => void;
}

export const FactCard: React.FC<FactCardProps> = ({ fact, onInspect, onViewPDF }) => {
  return (
    <div className="group relative bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all shadow-sm hover:shadow-md hover:shadow-sky-500/5">
      {/* Header: Entity & Predicate */}
      <div className="flex items-start justify-between gap-2 mb-2.5">
        <div className="flex-1">
          <span className="text-xs uppercase tracking-wider font-semibold text-sky-400">
            {fact.subject}
          </span>
          <h4 className="text-base font-medium text-slate-100 mt-0.5 capitalize">
            {fact.predicate.replace(/_/g, ' ')}
          </h4>
        </div>
        <span className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700/60 font-mono">
          p. {fact.evidence_page}
        </span>
      </div>

      {/* Main Fact Value */}
      <div className="bg-slate-950/60 rounded-lg p-2.5 border border-slate-800/80 mb-3">
        <div className="text-lg font-bold text-white tracking-tight">
          {fact.object_value}
        </div>
        {fact.normalized_value_text && fact.normalized_value_text !== fact.object_value && (
          <div className="text-xs text-slate-400 font-mono mt-1 flex items-center gap-1.5">
            <span className="text-slate-500">Normalized:</span>
            <span className="text-sky-300 font-medium">{fact.normalized_value_text}</span>
          </div>
        )}
      </div>

      {/* Context Tags */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {fact.temporal_context && (
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/50">
            <Calendar className="w-3 h-3 text-slate-400" />
            {fact.temporal_context}
          </span>
        )}
        {fact.scope_context && (
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/50">
            <Tag className="w-3 h-3 text-slate-400" />
            {fact.scope_context}
          </span>
        )}
        {fact.geographic_context && (
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/50">
            {fact.geographic_context}
          </span>
        )}
        <span className="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ml-auto">
          <ShieldCheck className="w-3 h-3" />
          {Math.round(fact.confidence * 100)}%
        </span>
      </div>

      {/* Evidence snippet teaser */}
      <div className="text-xs text-slate-400 line-clamp-2 italic bg-slate-950/30 p-2 rounded border border-slate-800/40 mb-3 font-serif">
        "{fact.evidence_text}"
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
        <span className="text-slate-500 truncate max-w-[180px] flex items-center gap-1">
          <FileText className="w-3 h-3 flex-shrink-0" />
          {fact.document_name || 'Document'}
        </span>
        <button
          onClick={() => onInspect(fact)}
          className="flex items-center gap-1 font-medium text-sky-400 hover:text-sky-300 transition-colors"
        >
          <Eye className="w-3.5 h-3.5" />
          Inspect Evidence
        </button>
      </div>
    </div>
  );
};

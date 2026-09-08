import React from 'react';
import { Fact } from '../types';
import { X, FileText, ExternalLink, Calendar, MapPin, Layers, CheckCircle, ShieldCheck } from 'lucide-react';
import { apiClient } from '../api/client';

interface FactDetailModalProps {
  fact: Fact | null;
  onClose: () => void;
  onOpenPDF: (docId: string, page: number) => void;
}

export const FactDetailModal: React.FC<FactDetailModalProps> = ({ fact, onClose, onOpenPDF }) => {
  if (!fact) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 animate-pulse" />
            <h3 className="text-lg font-semibold text-white">Fact Intelligence & Grounding</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {/* Extracted vs Normalized Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Extracted Fact */}
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-sky-400" />
                Original Extracted Fact
              </div>
              <div className="space-y-1.5 text-sm">
                <div>
                  <span className="text-slate-500 text-xs">Subject:</span>
                  <p className="font-medium text-slate-200">{fact.subject}</p>
                </div>
                <div>
                  <span className="text-slate-500 text-xs">Predicate:</span>
                  <p className="font-medium text-slate-200">{fact.predicate}</p>
                </div>
                <div>
                  <span className="text-slate-500 text-xs">Original Value:</span>
                  <p className="text-base font-bold text-sky-400">{fact.object_value}</p>
                </div>
              </div>
            </div>

            {/* Normalized Fact */}
            <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-800/40 space-y-3">
              <div className="text-xs font-semibold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5 text-sky-400" />
                Normalized Canonical Form
              </div>
              <div className="space-y-1.5 text-sm font-mono">
                <div>
                  <span className="text-slate-500 text-xs font-sans">Normalized Entity:</span>
                  <p className="font-medium text-sky-200 text-xs">{fact.normalized_subject}</p>
                </div>
                <div>
                  <span className="text-slate-500 text-xs font-sans">Normalized Predicate:</span>
                  <p className="font-medium text-sky-200 text-xs">{fact.normalized_predicate}</p>
                </div>
                <div>
                  <span className="text-slate-500 text-xs font-sans">Canonical Value:</span>
                  <p className="text-base font-bold text-sky-300">
                    {fact.normalized_value !== null ? fact.normalized_value.toLocaleString() : (fact.normalized_value_text || '—')}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Context Dimensions */}
          <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Contextual Metadata</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80">
                <span className="text-[11px] text-slate-500 flex items-center gap-1 mb-1">
                  <Calendar className="w-3 h-3 text-slate-400" /> Time / Period
                </span>
                <p className="font-medium text-slate-200 text-xs">{fact.temporal_context || 'Unspecified'}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80">
                <span className="text-[11px] text-slate-500 flex items-center gap-1 mb-1">
                  <Layers className="w-3 h-3 text-slate-400" /> Scope / Segment
                </span>
                <p className="font-medium text-slate-200 text-xs">{fact.scope_context || 'Global / Unspecified'}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80">
                <span className="text-[11px] text-slate-500 flex items-center gap-1 mb-1">
                  <MapPin className="w-3 h-3 text-slate-400" /> Geography
                </span>
                <p className="font-medium text-slate-200 text-xs">{fact.geographic_context || 'India'}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80">
                <span className="text-[11px] text-slate-500 flex items-center gap-1 mb-1">
                  <ShieldCheck className="w-3 h-3 text-slate-400" /> Unit & Type
                </span>
                <p className="font-medium text-slate-200 text-xs">
                  {fact.unit ? `${fact.unit} (${fact.value_type})` : fact.value_type}
                </p>
              </div>
            </div>
          </div>

          {/* Grounded Source Evidence */}
          <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-amber-400" /> Grounded Evidence Excerpt
              </h4>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                {Math.round(fact.confidence * 100)}% Extraction Confidence
              </span>
            </div>

            <blockquote className="p-3.5 rounded-lg bg-slate-900/90 border-l-4 border-sky-500 text-slate-200 text-sm font-serif italic leading-relaxed">
              "{fact.evidence_text}"
            </blockquote>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 text-xs text-slate-400">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5 text-slate-500" />
                  Source: <strong className="text-slate-300 ml-1">{fact.document_name || 'Document'}</strong>
                </span>
                <span>•</span>
                <span>Page: <strong className="text-slate-300 ml-1">Page {fact.evidence_page}</strong></span>
              </div>
              <button
                onClick={() => onOpenPDF(fact.document_id, fact.evidence_page)}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                View in Source PDF
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

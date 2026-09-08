import React, { useState, useEffect } from 'react';
import { ProcessingIssue } from '../types';
import { apiClient } from '../api/client';
import { AlertTriangle, AlertCircle, Info, ShieldAlert, RefreshCw, FileText, CheckCircle2 } from 'lucide-react';

interface FailureUncertaintyPageProps {
  onOpenPDF: (docId: string, page: number) => void;
}

export const FailureUncertaintyPage: React.FC<FailureUncertaintyPageProps> = ({ onOpenPDF }) => {
  const [issues, setIssues] = useState<ProcessingIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');

  const fetchIssues = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listIssues({
        severity: selectedSeverity === 'ALL' ? undefined : selectedSeverity,
      });
      setIssues(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, [selectedSeverity]);

  const severityBadge = (sev: string) => {
    switch (sev) {
      case 'ERROR':
        return (
          <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 font-semibold">
            <AlertCircle className="w-3.5 h-3.5" /> ERROR
          </span>
        );
      case 'WARNING':
        return (
          <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-semibold">
            <AlertTriangle className="w-3.5 h-3.5" /> WARNING
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 font-semibold">
            <Info className="w-3.5 h-3.5" /> INFO
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Extraction & Reasoning Failures / Uncertainties</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium">
              Case 4 Demonstration
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Transparent reporting of low-confidence OCR, tabular parsing limitations, entity ambiguities, and uncertain cross-document relationships.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="ALL">All Severities</option>
            <option value="ERROR">Errors</option>
            <option value="WARNING">Warnings</option>
            <option value="INFO">Info / Observations</option>
          </select>
          <button
            onClick={fetchIssues}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Info Callout */}
      <div className="rounded-2xl border border-amber-500/30 bg-amber-950/10 p-4 sm:p-5 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs sm:text-sm text-slate-300 space-y-1 leading-relaxed">
          <strong className="text-amber-300">Why are failures surfaced here?</strong> Real-world PDF intelligence systems encounter unparseable scanned pages, dense multi-column tabular artifacts, and entity ambiguities. SuperJoin surfaces these transparently rather than hallucinating confident facts.
        </div>
      </div>

      {/* Issues List */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-sm flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-sky-400" /> Loading issues...
        </div>
      ) : issues.length > 0 ? (
        <div className="space-y-4">
          {issues.map((iss) => (
            <div
              key={iss.id}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 hover:border-slate-700 transition-all"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  {severityBadge(iss.severity)}
                  <span className="text-xs font-mono text-slate-400 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                    {iss.category}
                  </span>
                </div>
                {iss.confidence !== null && iss.confidence !== undefined && (
                  <span className="text-xs text-slate-500 font-mono">
                    Model Confidence: <strong className="text-amber-400">{Math.round(iss.confidence * 100)}%</strong>
                  </span>
                )}
              </div>

              <div>
                <h4 className="text-sm font-semibold text-slate-100">{iss.description}</h4>
                {iss.document_name && (
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                    <FileText className="w-3.5 h-3.5 text-slate-500" />
                    <span>Document: <strong className="text-slate-300">{iss.document_name}</strong></span>
                    {iss.page_number && (
                      <>
                        <span>•</span>
                        <span>Page {iss.page_number}</span>
                      </>
                    )}
                  </div>
                )}
              </div>

              {iss.raw_snippet && (
                <div className="rounded-xl bg-slate-950/80 p-3 border border-slate-800/80 text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                  {iss.raw_snippet}
                </div>
              )}

              {iss.document_id && iss.page_number && (
                <div className="pt-2 border-t border-slate-800/60 flex justify-end">
                  <button
                    onClick={() => onOpenPDF(iss.document_id!, iss.page_number!)}
                    className="text-xs font-medium text-sky-400 hover:text-sky-300 flex items-center gap-1"
                  >
                    View Page in PDF →
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 rounded-3xl border border-dashed border-slate-800 bg-slate-900/20">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-300">No Current Extraction or Reasoning Failures</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            All processed pages and facts completed with high extraction and comparison confidence.
          </p>
        </div>
      )}
    </div>
  );
};

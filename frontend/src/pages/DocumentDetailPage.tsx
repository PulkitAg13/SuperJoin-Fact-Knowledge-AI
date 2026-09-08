import React, { useState, useEffect } from 'react';
import { Document, Fact } from '../types';
import { apiClient } from '../api/client';
import { FactCard } from '../components/FactCard';
import { StatusBadge } from '../components/StatusBadge';
import { ArrowLeft, ExternalLink, Search, Filter, FileText, RefreshCw } from 'lucide-react';

interface DocumentDetailPageProps {
  documentId: string;
  onBack: () => void;
  onInspectFact: (fact: Fact) => void;
  onOpenPDF: (docId: string, page: number) => void;
}

export const DocumentDetailPage: React.FC<DocumentDetailPageProps> = ({
  documentId,
  onBack,
  onInspectFact,
  onOpenPDF,
}) => {
  const [doc, setDoc] = useState<Document | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPredicate, setSelectedPredicate] = useState<string>('ALL');

  const fetchDocAndFacts = async () => {
    setLoading(true);
    try {
      const [docData, factsData] = await Promise.all([
        apiClient.getDocument(documentId),
        apiClient.getDocumentFacts(documentId),
      ]);
      setDoc(docData);
      setFacts(factsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocAndFacts();
  }, [documentId]);

  const predicates = Array.from(new Set(facts.map((f) => f.predicate)));

  const filteredFacts = facts.filter((f) => {
    const matchesSearch =
      f.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.predicate.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.object_value.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.evidence_text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPred = selectedPredicate === 'ALL' || f.predicate === selectedPredicate;
    return matchesSearch && matchesPred;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">{doc?.filename || 'Document Details'}</h1>
              {doc && <StatusBadge type={doc.status} size="sm" />}
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-3">
              <span>{doc?.page_count} Pages</span>
              <span>•</span>
              <span>{facts.length} Grounded Facts</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onOpenPDF(documentId, 1)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" /> View Original PDF
          </button>
          <button
            onClick={fetchDocAndFacts}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search facts by subject, attribute, value, or evidence text..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={selectedPredicate}
            onChange={(e) => setSelectedPredicate(e.target.value)}
            className="bg-slate-900/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="ALL">All Attributes ({facts.length})</option>
            {predicates.map((p) => (
              <option key={p} value={p}>
                {p.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Facts Grid */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-sm flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-sky-400" /> Loading extracted facts...
        </div>
      ) : filteredFacts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredFacts.map((fact) => (
            <FactCard
              key={fact.id}
              fact={fact}
              onInspect={onInspectFact}
              onViewPDF={onOpenPDF}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 rounded-3xl border border-dashed border-slate-800 bg-slate-900/20">
          <FileText className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-sm text-slate-400">No facts match your search criteria.</p>
        </div>
      )}
    </div>
  );
};

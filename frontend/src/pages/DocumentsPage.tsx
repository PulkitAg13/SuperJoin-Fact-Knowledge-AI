import React, { useState } from 'react';
import { Document } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { FileText, Eye, Trash2, Calendar, Layers, ExternalLink, Plus } from 'lucide-react';
import { apiClient } from '../api/client';

interface DocumentsPageProps {
  documents: Document[];
  onSelectDocument: (docId: string) => void;
  onOpenPDF: (docId: string, page: number) => void;
  onRefresh: () => void;
  onNavigateToUpload: () => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({
  documents,
  onSelectDocument,
  onOpenPDF,
  onRefresh,
  onNavigateToUpload,
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this document and all its extracted facts?')) {
      return;
    }
    setDeletingId(docId);
    try {
      await apiClient.deleteDocument(docId);
      onRefresh();
    } catch (err) {
      alert('Failed to delete document');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Ingested PDF Documents</h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse registered files, review extraction progress, and inspect fact candidates.
          </p>
        </div>
        <button
          onClick={onNavigateToUpload}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-sky-600 hover:bg-sky-500 text-white transition-colors self-start"
        >
          <Plus className="w-4 h-4" /> Upload Documents
        </button>
      </div>

      {documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelectDocument(doc.id)}
              className="group cursor-pointer rounded-2xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 hover:bg-slate-900 p-5 transition-all shadow-sm hover:shadow-md flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="p-2.5 rounded-xl bg-slate-800 text-sky-400">
                    <FileText className="w-6 h-6" />
                  </div>
                  <StatusBadge type={doc.status} size="sm" />
                </div>

                <h3 className="text-base font-semibold text-white group-hover:text-sky-400 transition-colors line-clamp-2">
                  {doc.filename}
                </h3>

                <div className="mt-3 space-y-1.5 text-xs text-slate-400">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Pages:</span>
                    <span className="font-mono text-slate-300">{doc.page_count} pages</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">File Size:</span>
                    <span className="font-mono text-slate-300">{(doc.file_size_bytes / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Grounded Facts:</span>
                    <span className="font-semibold text-sky-400 font-mono">{doc.fact_count} facts</span>
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenPDF(doc.id, 1);
                  }}
                  className="flex items-center gap-1 text-slate-400 hover:text-sky-400 transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> PDF
                </button>
                <div className="flex items-center gap-3">
                  <button
                    onClick={(e) => handleDelete(e, doc.id)}
                    disabled={deletingId === doc.id}
                    className="p-1 rounded text-slate-500 hover:text-rose-400 transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <span className="text-sky-400 group-hover:translate-x-0.5 transition-transform font-medium flex items-center gap-1">
                    Inspect Facts →
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 rounded-3xl border border-dashed border-slate-800 bg-slate-900/30">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No Documents Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Get started by uploading PDF documents or ingesting the sample datasets.
          </p>
          <button
            onClick={onNavigateToUpload}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white transition-colors"
          >
            Go to Upload Page
          </button>
        </div>
      )}
    </div>
  );
};

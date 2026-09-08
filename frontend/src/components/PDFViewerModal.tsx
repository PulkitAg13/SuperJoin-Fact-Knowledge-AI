import React from 'react';
import { X, ExternalLink, Download } from 'lucide-react';
import { apiClient } from '../api/client';

interface PDFViewerModalProps {
  documentId: string | null;
  pageNumber?: number;
  onClose: () => void;
}

export const PDFViewerModal: React.FC<PDFViewerModalProps> = ({ documentId, pageNumber = 1, onClose }) => {
  if (!documentId) return null;

  const pdfUrl = `${apiClient.getPDFUrl(documentId)}#page=${pageNumber}`;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
      <div className="relative w-full max-w-5xl h-[90vh] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-900">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-semibold text-white">Source Document Preview</h3>
            <span className="text-xs px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
              Page {pageNumber}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              title="Open in new window"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Embedded PDF iframe */}
        <div className="flex-1 w-full bg-slate-950">
          <iframe
            src={pdfUrl}
            className="w-full h-full border-0"
            title="PDF Viewer"
          />
        </div>
      </div>
    </div>
  );
};

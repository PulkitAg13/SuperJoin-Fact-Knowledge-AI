import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw, Database, Trash2 } from 'lucide-react';
import { apiClient } from '../api/client';
import { Document } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface UploadPageProps {
  documents: Document[];
  onRefresh: () => void;
  onNavigateToDocument: (docId: string) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({
  documents,
  onRefresh,
  onNavigateToDocument,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const processFiles = async (files: File[]) => {
    const pdfs = files.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
    if (pdfs.length === 0) {
      setErrorMessage('Please upload only PDF documents.');
      return;
    }

    setUploading(true);
    setErrorMessage(null);
    try {
      await apiClient.uploadDocuments(pdfs);
      onRefresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(Array.from(e.target.files));
    }
  };

  const handleLoadSample = async (datasetName: string) => {
    setLoadingSample(datasetName);
    setErrorMessage(null);
    try {
      await apiClient.loadSampleDataset(datasetName);
      onRefresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load sample dataset');
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-200">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">PDF Ingestion & Ingestion Pipeline</h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload new PDFs or load curated starter datasets to run grounded fact extraction and reconciliation.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Drag and Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-sky-400 bg-sky-500/10 scale-[1.01]'
            : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/70'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          onChange={handleFileInput}
          className="hidden"
        />
        <div className="w-16 h-16 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center mx-auto mb-4">
          <UploadCloud className={`w-8 h-8 ${uploading ? 'animate-bounce' : ''}`} />
        </div>
        <h3 className="text-base font-semibold text-white">
          {uploading ? 'Uploading and Registering Documents...' : 'Drag & Drop PDF Documents Here'}
        </h3>
        <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
          Supports multi-file upload. PDF text will be extracted page-by-page, chunked, and grounded to evidence.
        </p>
        <button
          type="button"
          disabled={uploading}
          className="mt-5 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          Browse Local Files
        </button>
      </div>

      {/* Starter Datasets Loader Banner */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-sky-400" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Curated Starter Datasets (One-Click Ingest)
          </h2>
        </div>
        <p className="text-xs text-slate-400">
          Load the pre-configured assignment datasets directly from local files:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between space-y-3">
            <div>
              <div className="font-semibold text-sm text-white">Delhivery Corporate Filings</div>
              <p className="text-xs text-slate-400 mt-1">
                Prospectus 2022, FY24 Annual Report, and Q4 FY24 Earnings Presentation.
              </p>
            </div>
            <button
              onClick={() => handleLoadSample('delhivery')}
              disabled={loadingSample !== null}
              className="w-full py-2 px-3 rounded-lg text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loadingSample === 'delhivery' ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Database className="w-3.5 h-3.5" />
              )}
              {loadingSample === 'delhivery' ? 'Ingesting Delhivery...' : 'Ingest Delhivery Dataset (3 PDFs)'}
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between space-y-3">
            <div>
              <div className="font-semibold text-sm text-white">India Macroeconomic Reports</div>
              <p className="text-xs text-slate-400 mt-1">
                Economic Survey 2024-25, RBI Annual Report, and IMF Article IV Consultation.
              </p>
            </div>
            <button
              onClick={() => handleLoadSample('india-macroeconomy')}
              disabled={loadingSample !== null}
              className="w-full py-2 px-3 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loadingSample === 'india-macroeconomy' ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Database className="w-3.5 h-3.5" />
              )}
              {loadingSample === 'india-macroeconomy' ? 'Ingesting Macro...' : 'Ingest Macroeconomy Dataset (3 PDFs)'}
            </button>
          </div>
        </div>
      </div>

      {/* Uploaded Documents List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white tracking-tight">Ingested Documents & Processing Status</h2>
          <button
            onClick={onRefresh}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Status
          </button>
        </div>

        {documents.length > 0 ? (
          <div className="divide-y divide-slate-800/80 rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-900/90 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="p-2.5 rounded-xl bg-slate-800 text-sky-400 mt-0.5">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white hover:text-sky-400 cursor-pointer" onClick={() => onNavigateToDocument(doc.id)}>
                      {doc.filename}
                    </h4>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
                      <span>{doc.page_count} pages</span>
                      <span>•</span>
                      <span>{(doc.file_size_bytes / 1024 / 1024).toFixed(2)} MB</span>
                      <span>•</span>
                      <span className="text-sky-400 font-medium">{doc.fact_count} facts extracted</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  <StatusBadge type={doc.status} />
                  <button
                    onClick={() => onNavigateToDocument(doc.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                  >
                    View Facts
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 rounded-2xl border border-slate-800/80 bg-slate-900/20 text-xs text-slate-500">
            No documents uploaded yet. Upload a PDF or load a sample above.
          </div>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { UploadPage } from './pages/UploadPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailPage } from './pages/DocumentDetailPage';
import { RelationshipExplorer } from './pages/RelationshipExplorer';
import { FailureUncertaintyPage } from './pages/FailureUncertaintyPage';
import { FactDetailModal } from './components/FactDetailModal';
import { PDFViewerModal } from './components/PDFViewerModal';
import { Document, Fact, SystemSummary } from './types';
import { apiClient } from './api/client';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [summary, setSummary] = useState<SystemSummary | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  // Modals
  const [activeFact, setActiveFact] = useState<Fact | null>(null);
  const [pdfModal, setPdfModal] = useState<{ docId: string; page: number } | null>(null);

  const fetchAppData = async () => {
    try {
      const [sumData, docsData] = await Promise.all([
        apiClient.getSummary(),
        apiClient.getDocuments(),
      ]);
      setSummary(sumData);
      setDocuments(docsData);
    } catch (err) {
      console.error('Error polling app data:', err);
    }
  };

  useEffect(() => {
    fetchAppData();
    // Poll every 5 seconds if there are documents in progress
    const interval = setInterval(() => {
      fetchAppData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      await apiClient.triggerAnalysis();
      await fetchAppData();
      setCurrentTab('relationships');
    } catch (err) {
      alert('Analysis error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleLoadSample = async (dataset: string) => {
    setIsLoadingSample(true);
    try {
      await apiClient.loadSampleDataset(dataset);
      await fetchAppData();
      setCurrentTab('documents');
    } catch (err: any) {
      alert(err.message || 'Failed to load dataset');
    } finally {
      setIsLoadingSample(false);
    }
  };

  const handleSelectDocument = (docId: string) => {
    setSelectedDocId(docId);
    setCurrentTab('document_detail');
  };

  const handleOpenPDF = (docId: string, page: number) => {
    setPdfModal({ docId, page });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        onRunAnalysis={handleRunAnalysis}
        isAnalyzing={isAnalyzing}
        issueCount={summary?.total_issues ?? 0}
      />

      {/* Main Page Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === 'dashboard' && (
          <Dashboard
            summary={summary}
            onNavigate={setCurrentTab}
            onInspectFact={setActiveFact}
            onLoadSample={handleLoadSample}
            isLoadingSample={isLoadingSample}
          />
        )}

        {currentTab === 'upload' && (
          <UploadPage
            documents={documents}
            onRefresh={fetchAppData}
            onNavigateToDocument={handleSelectDocument}
          />
        )}

        {currentTab === 'documents' && (
          <DocumentsPage
            documents={documents}
            onSelectDocument={handleSelectDocument}
            onOpenPDF={handleOpenPDF}
            onRefresh={fetchAppData}
            onNavigateToUpload={() => setCurrentTab('upload')}
          />
        )}

        {currentTab === 'document_detail' && selectedDocId && (
          <DocumentDetailPage
            documentId={selectedDocId}
            onBack={() => setCurrentTab('documents')}
            onInspectFact={setActiveFact}
            onOpenPDF={handleOpenPDF}
          />
        )}

        {currentTab === 'relationships' && (
          <RelationshipExplorer
            onInspectFact={setActiveFact}
            onRunAnalysis={handleRunAnalysis}
            isAnalyzing={isAnalyzing}
          />
        )}

        {currentTab === 'issues' && (
          <FailureUncertaintyPage onOpenPDF={handleOpenPDF} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>SuperJoin Fact Knowledge AI • Engineering Assignment Submission</p>
      </footer>

      {/* Fact Detail Modal */}
      <FactDetailModal
        fact={activeFact}
        onClose={() => setActiveFact(null)}
        onOpenPDF={(docId, page) => {
          setActiveFact(null);
          handleOpenPDF(docId, page);
        }}
      />

      {/* Source PDF Viewer Modal */}
      <PDFViewerModal
        documentId={pdfModal?.docId || null}
        pageNumber={pdfModal?.page || 1}
        onClose={() => setPdfModal(null)}
      />
    </div>
  );
};

export default App;

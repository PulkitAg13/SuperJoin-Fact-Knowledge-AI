import { Document, Fact, Relationship, ProcessingIssue, SystemSummary } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = {
  // Summary & Dashboard
  async getSummary(): Promise<SystemSummary> {
    const res = await fetch(`${API_BASE}/summary`);
    if (!res.ok) throw new Error('Failed to fetch summary');
    return res.json();
  },

  // Documents
  async getDocuments(): Promise<Document[]> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(id: string): Promise<Document> {
    const res = await fetch(`${API_BASE}/documents/${id}`);
    if (!res.ok) throw new Error('Failed to fetch document');
    return res.json();
  },

  async getDocumentFacts(documentId: string): Promise<Fact[]> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/facts`);
    if (!res.ok) throw new Error('Failed to fetch document facts');
    return res.json();
  },

  async uploadDocuments(files: File[]): Promise<Document[]> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async loadSampleDataset(datasetName: string): Promise<Document[]> {
    const res = await fetch(`${API_BASE}/documents/load-sample?dataset_name=${encodeURIComponent(datasetName)}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to load sample dataset' }));
      throw new Error(err.detail || 'Failed to load sample dataset');
    }
    return res.json();
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  async getDocumentStatus(id: string): Promise<{ id: string; status: string; fact_count: number }> {
    const res = await fetch(`${API_BASE}/documents/${id}/status`);
    if (!res.ok) throw new Error('Failed to fetch document status');
    return res.json();
  },

  // Facts
  async listFacts(params?: {
    document_id?: string;
    entity?: string;
    predicate?: string;
    value_type?: string;
    search?: string;
  }): Promise<Fact[]> {
    const query = new URLSearchParams();
    if (params?.document_id) query.append('document_id', params.document_id);
    if (params?.entity) query.append('entity', params.entity);
    if (params?.predicate) query.append('predicate', params.predicate);
    if (params?.value_type) query.append('value_type', params.value_type);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/facts?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch facts');
    return res.json();
  },

  async getFact(id: string): Promise<Fact> {
    const res = await fetch(`${API_BASE}/facts/${id}`);
    if (!res.ok) throw new Error('Failed to fetch fact');
    return res.json();
  },

  // Relationships
  async listRelationships(params?: {
    relationship_type?: string;
    document_id?: string;
  }): Promise<Relationship[]> {
    const query = new URLSearchParams();
    if (params?.relationship_type) query.append('relationship_type', params.relationship_type);
    if (params?.document_id) query.append('document_id', params.document_id);

    const res = await fetch(`${API_BASE}/relationships?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch relationships');
    return res.json();
  },

  async getRelationship(id: string): Promise<Relationship> {
    const res = await fetch(`${API_BASE}/relationships/${id}`);
    if (!res.ok) throw new Error('Failed to fetch relationship');
    return res.json();
  },

  async triggerAnalysis(): Promise<{ status: string; relationships_discovered: number }> {
    const res = await fetch(`${API_BASE}/analyze`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger analysis');
    return res.json();
  },

  // Issues / Uncertainties
  async listIssues(params?: {
    category?: string;
    severity?: string;
  }): Promise<ProcessingIssue[]> {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    if (params?.severity) query.append('severity', params.severity);

    const res = await fetch(`${API_BASE}/issues?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch issues');
    return res.json();
  },

  getPDFUrl(documentId: string): string {
    return `${API_BASE}/documents/${documentId}/pdf`;
  }
};

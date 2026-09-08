export interface Document {
  id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  status: 'UPLOADED' | 'EXTRACTING' | 'EXTRACTED' | 'ANALYZING' | 'COMPLETED' | 'FAILED';
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  fact_count: number;
}

export interface Fact {
  id: string;
  document_id: string;
  subject: string;
  predicate: string;
  object_value: string;
  normalized_subject: string;
  normalized_predicate: string;
  normalized_value: number | null;
  normalized_value_text: string | null;
  value_type: string;
  unit: string | null;
  currency: string | null;
  temporal_context: string | null;
  geographic_context: string | null;
  scope_context: string | null;
  qualifiers: string | null;
  confidence: number;
  evidence_text: string;
  evidence_page: number;
  evidence_chunk_id?: string | null;
  created_at: string;
  document_name?: string | null;
}

export type RelationshipType = 
  | 'CORROBORATES'
  | 'CONTRADICTS'
  | 'RECONCILED_BY_CONTEXT'
  | 'RELATED'
  | 'UNCERTAIN'
  | 'NO_RELATION';

export interface Relationship {
  id: string;
  fact_a_id: string;
  fact_b_id: string;
  relationship_type: RelationshipType;
  confidence: number;
  reasoning: string;
  context_explanation?: string | null;
  created_at: string;
  fact_a?: Fact;
  fact_b?: Fact;
}

export interface ProcessingIssue {
  id: string;
  document_id?: string | null;
  category: string;
  severity: 'INFO' | 'WARNING' | 'ERROR';
  page_number?: number | null;
  description: string;
  raw_snippet?: string | null;
  confidence?: number | null;
  created_at: string;
  document_name?: string | null;
}

export interface SystemSummary {
  total_documents: number;
  total_facts: number;
  total_relationships: number;
  corroborations: number;
  contradictions: number;
  reconciled_cases: number;
  uncertain_cases: number;
  total_issues: number;
  recent_relationships: Relationship[];
}

/**
 * API Envelope Schemas for KathaYantra REST Endpoints.
 */

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
  meta: Record<string, any>;
}

export interface SingleResponse<T> {
  data: T;
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  detail?: any | null;
}

export interface SearchSuggestion {
  text: string;
  suggestion_type: "title" | "motif" | "alternate_name" | "region";
  category?: string | null;
  country_code?: string | null;
}

export interface DatasetQualityResponse {
  status: string;
  published_records: number;
  seed_files_valid: number;
  total_seed_files: number;
  staged_candidates_count: number;
  retrieval_index_count: number;
  audit_summary: Record<string, any>;
}

export interface SourceRegistryItem {
  id: string;
  name: string;
  canonical_url: string;
  docs_or_dataset_url: string;
  source_type: string;
  api_status: string;
  auth_required: boolean;
  rate_limit_info: string;
  content_format: string;
  supported_research_purpose: string;
  geographic_or_cultural_coverage: string[];
  licensing_info: string;
  rights_assessment_status: string;
  full_text_reuse_verified: boolean;
  retain_metadata_only: boolean;
  last_checked_date: string;
  implementation_status: string;
  known_limitations: string;
}

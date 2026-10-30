/**
 * Local AI Archivist TypeScript Schemas.
 */

export type AIAnswerType =
  | "grounded_answer"
  | "insufficient_evidence"
  | "out_of_scope"
  | "model_unavailable"
  | "error";

export interface AISourceCitation {
  story_id: string;
  story_title: string;
  country_code: string;
  category: string;
  publisher: string;
  url: string;
  citation?: string | null;
  attribution_text?: string | null;
  license_name?: string | null;
}

export interface AIQuestionRequest {
  question: string;
  country_code?: string | null;
  category?: "folklore" | "urban_legend" | null;
  max_records?: number;
}

export interface AIQuestionResponse {
  question: string;
  answer: string;
  answer_type: AIAnswerType;
  supporting_story_ids: string[];
  sources: AISourceCitation[];
  retrieval_status: string;
  limitations?: string | null;
  model_provider: string;
  model_tag: string;
  prompt_version: string;
  generated_at: string;
}

export interface AIComparisonRequest {
  story_ids: string[];
  aspect_notes?: string | null;
}

export interface AIComparisonResponse {
  summary: string;
  compared_story_ids: string[];
  similarities: string[];
  differences: string[];
  cultural_context: string[];
  uncertain_details: string[];
  sources: AISourceCitation[];
  model_provider: string;
  model_tag: string;
  prompt_version: string;
  generated_at: string;
}

export interface AIFictionRequest {
  inspiration_story_ids: string[];
  setting?: string;
  atmosphere?: string;
  narrative_style?: string;
  creative_prompt?: string | null;
}

export interface AIFictionResponse {
  fiction_record: {
    id: string;
    title: string;
    story_text: string;
    disclaimer: string;
    setting: string;
    atmosphere: string;
    inspired_by_story_ids: string[];
    created_at: string;
  };
  saved_path?: string | null;
  model_tag: string;
  prompt_version: string;
  generated_at: string;
}

export interface AIOllamaHealthResponse {
  status: "available" | "model_missing" | "unavailable" | "misconfigured";
  provider: string;
  base_url: string;
  configured_model: string;
  model_available: boolean;
  installed_models: string[];
  message: string;
  timestamp: string;
}

/**
 * Story and Folklore TypeScript Schemas matching KathaYantra Backend v2.0.0.
 */

export type Category = "folklore" | "urban_legend";

export type VerificationStatus = "verified" | "needs_review" | "rejected";

export type ContentOrigin =
  | "licensed_dataset"
  | "public_domain_source"
  | "original_summary"
  | "metadata_only"
  | "user_contributed"
  | "ai_generated_fiction";

export type RightsStatus =
  | "approved"
  | "metadata_only"
  | "public_domain_verified"
  | "permission_required"
  | "needs_rights_review"
  | "restricted"
  | "unknown";

export interface StorySource {
  id?: string | null;
  title: string;
  publisher: string;
  name?: string;
  url: string;
  canonical_url?: string | null;
  external_id?: string | null;
  source_type: string;
  language: string;
  published_at?: string | null;
  license_name?: string | null;
  license_url?: string | null;
  rights_status: RightsStatus;
  reuse_scope: string;
  attribution_required: boolean;
  attribution_text?: string | null;
  full_text_reuse_allowed: boolean;
  notes?: string | null;
  citation?: string | null;
  access_date?: string | null;
}

export interface StoryRecord {
  id: string;
  schema_version: string;
  record_version: string;
  title: string;
  slug: string;
  country_code: string;
  category: Category;
  subtype?: string | null;
  summary: string;
  long_description?: string | null;
  alternate_names: string[];
  language: string;
  alternate_languages: string[];
  motifs: string[];
  themes: string[];
  historical_period?: string | null;
  region_or_community?: string | null;
  community_attributions: string[];
  geographic_associations: string[];
  variant_notes?: string | null;
  related_record_ids: string[];
  sources: StorySource[];
  source_type: string;
  license: string;
  rights_status: RightsStatus;
  attribution_text?: string | null;
  canonical_url?: string | null;
  retrieved_at?: string | null;
  verification_status: VerificationStatus;
  content_origin: ContentOrigin;
  created_at: string;
  updated_at: string;
}

export interface RelatedStoryItem {
  story_id: string;
  title: string;
  category: Category;
  country_code: string;
  summary: string;
  relationship_basis: string;
  shared_motifs: string[];
  shared_themes: string[];
}

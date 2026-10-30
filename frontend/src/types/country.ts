/**
 * Country Registry and Statistics TypeScript Schemas.
 */

export interface CountryRecordTargets {
  folklore: number;
  urban_legends: number;
}

export interface CountryRecord {
  code: string;
  name: string;
  display_name: string;
  iso_alpha2: string;
  region: string;
  primary_languages: string[];
  regions_or_communities: string[];
  cultural_context: string;
  cultural_context_notes?: string;
  enabled: boolean;
  status: string;
  record_targets: CountryRecordTargets;
  target_folklore_count: number;
  target_urban_legends_count: number;
  total_target: number;
  created_at: string;
  updated_at: string;
  schema_version: string;
}

export interface CountryStatsResponse {
  country_code: string;
  country_name: string;
  folklore_count: number;
  urban_legend_count: number;
  total_count: number;
  folklore_target: number;
  urban_legend_target: number;
  total_target: number;
  folklore_gap: number;
  urban_legend_gap: number;
  total_gap: number;
  is_quotas_met: boolean;
  source_count: number;
  cultural_context: string;
}


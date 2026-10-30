/**
 * Image Asset and Manifest TypeScript Schemas.
 */

export interface ImageAssetRecord {
  image_id: string;
  aspect: string;
  title: string;
  source_institution: string;
  source_url: string;
  image_url: string;
  catalog_url?: string;
  local_path: string;
  license: string;
  license_url: string;
  attribution: string;
  image_type: string;
  depicts: string;
  historical_period: string;
  cultural_region: string;
  geographic_association: string;
  format: string;
  width: number;
  height: number;
  verified_authentic: boolean;
  ai_generated: boolean;
}

export interface StoryImageManifestItem {
  story_id: string;
  title: string;
  slug: string;
  country_code: string;
  category: "folklore" | "urban_legend";
  subtype: string;
  historical_period: string;
  cultural_region: string;
  geographic_associations: string[];
  total_images: number;
  images: ImageAssetRecord[];
}

export interface ImageManifest {
  manifest_version: string;
  generated_at: string;
  project: string;
  dataset_integrity: {
    total_records: number;
    total_images_documented: number;
    target_per_record: number;
    fulfillment_rate_percent: number;
    ai_generated_images_count: number;
    verified_authentic_images_count: number;
  };
  images_by_category: Record<string, number>;
  images_by_country: Record<string, number>;
  license_distribution: Record<string, number>;
  institution_distribution: Record<string, number>;
  image_types_distribution: Record<string, number>;
  records: StoryImageManifestItem[];
}

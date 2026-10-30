/**
 * High-Precision Typed API Client for KathaYantra Backend REST API.
 */

import {
  AIComparisonRequest,
  AIComparisonResponse,
  AIFictionRequest,
  AIFictionResponse,
  AIOllamaHealthResponse,
  AIQuestionRequest,
  AIQuestionResponse,
} from "@/types/ai";
import {
  DatasetQualityResponse,
  ErrorResponse,
  PaginatedResponse,
  SearchSuggestion,
  SingleResponse,
  SourceRegistryItem,
} from "@/types/api";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import {
  Category,
  RelatedStoryItem,
  StoryRecord,
  StorySource,
} from "@/types/story";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const API_PREFIX = process.env.NEXT_PUBLIC_API_PREFIX || "/api/v1";

export class ApiError extends Error {
  errorCode: string;
  detail: any;
  status: number;

  constructor(
    message: string,
    errorCode: string,
    status: number,
    detail: any = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.errorCode = errorCode;
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${API_PREFIX}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      let errPayload: ErrorResponse = {
        error_code: `HTTP_${res.status}`,
        message: res.statusText || "An API error occurred",
        detail: null,
      };

      try {
        errPayload = await res.json();
      } catch {
        // Non-JSON response
      }

      throw new ApiError(
        errPayload.message || `Request failed with status ${res.status}`,
        errPayload.error_code || "UNKNOWN_ERROR",
        res.status,
        errPayload.detail,
      );
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      err.message || "Network connection failure to KathaYantra backend",
      "CONNECTION_ERROR",
      0,
      err,
    );
  }
}

export const api = {
  // --- System ---
  async getHealth(): Promise<Record<string, any>> {
    return request<Record<string, any>>("/health");
  },

  async getOllamaHealth(): Promise<AIOllamaHealthResponse> {
    return request<AIOllamaHealthResponse>("/health/ollama");
  },

  // --- Countries ---
  async listCountries(
    params: { limit?: number; offset?: number } = {},
  ): Promise<PaginatedResponse<CountryRecord>> {
    const q = new URLSearchParams();
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return request<PaginatedResponse<CountryRecord>>(
      `/countries?${q.toString()}`,
    );
  },

  async getCountry(code: string): Promise<CountryRecord> {
    const res = await request<SingleResponse<CountryRecord>>(
      `/countries/${code.toUpperCase()}`,
    );
    return res.data;
  },

  async getCountryStats(code: string): Promise<CountryStatsResponse> {
    const res = await request<SingleResponse<CountryStatsResponse>>(
      `/countries/${code.toUpperCase()}/stats`,
    );
    return res.data;
  },

  async getCountryStories(
    code: string,
    params: {
      category?: Category;
      language?: string;
      motif?: string;
      q?: string;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
      offset?: number;
    } = {},
  ): Promise<PaginatedResponse<StoryRecord>> {
    const q = new URLSearchParams();
    if (params.category) q.set("category", params.category);
    if (params.language) q.set("language", params.language);
    if (params.motif) q.set("motif", params.motif);
    if (params.q) q.set("q", params.q);
    if (params.sort_by) q.set("sort_by", params.sort_by);
    if (params.sort_order) q.set("sort_order", params.sort_order);
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return request<PaginatedResponse<StoryRecord>>(
      `/countries/${code.toUpperCase()}/stories?${q.toString()}`,
    );
  },

  // --- Folklore ---
  async listFolklore(
    params: {
      country_code?: string;
      region?: string;
      language?: string;
      motif?: string;
      theme?: string;
      q?: string;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
      offset?: number;
    } = {},
  ): Promise<PaginatedResponse<StoryRecord>> {
    const q = new URLSearchParams();
    if (params.country_code) q.set("country_code", params.country_code);
    if (params.region) q.set("region", params.region);
    if (params.language) q.set("language", params.language);
    if (params.motif) q.set("motif", params.motif);
    if (params.theme) q.set("theme", params.theme);
    if (params.q) q.set("q", params.q);
    if (params.sort_by) q.set("sort_by", params.sort_by);
    if (params.sort_order) q.set("sort_order", params.sort_order);
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return request<PaginatedResponse<StoryRecord>>(`/folklore?${q.toString()}`);
  },

  async getFolklore(id: string): Promise<StoryRecord> {
    const res = await request<SingleResponse<StoryRecord>>(
      `/folklore/${id.toUpperCase()}`,
    );
    return res.data;
  },

  // --- Urban Legends ---
  async listUrbanLegends(
    params: {
      country_code?: string;
      region?: string;
      language?: string;
      motif?: string;
      theme?: string;
      q?: string;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
      offset?: number;
    } = {},
  ): Promise<PaginatedResponse<StoryRecord>> {
    const q = new URLSearchParams();
    if (params.country_code) q.set("country_code", params.country_code);
    if (params.region) q.set("region", params.region);
    if (params.language) q.set("language", params.language);
    if (params.motif) q.set("motif", params.motif);
    if (params.theme) q.set("theme", params.theme);
    if (params.q) q.set("q", params.q);
    if (params.sort_by) q.set("sort_by", params.sort_by);
    if (params.sort_order) q.set("sort_order", params.sort_order);
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return request<PaginatedResponse<StoryRecord>>(
      `/urban-legends?${q.toString()}`,
    );
  },

  async getUrbanLegend(id: string): Promise<StoryRecord> {
    const res = await request<SingleResponse<StoryRecord>>(
      `/urban-legends/${id.toUpperCase()}`,
    );
    return res.data;
  },

  // --- Unified Stories ---
  async getStory(id: string): Promise<StoryRecord> {
    const res = await request<SingleResponse<StoryRecord>>(
      `/stories/${id.toUpperCase()}`,
    );
    return res.data;
  },

  async getStorySources(id: string): Promise<StorySource[]> {
    const res = await request<SingleResponse<StorySource[]>>(
      `/stories/${id.toUpperCase()}/sources`,
    );
    return res.data;
  },

  async getRelatedStories(
    id: string,
    limit: number = 5,
  ): Promise<RelatedStoryItem[]> {
    const res = await request<SingleResponse<RelatedStoryItem[]>>(
      `/stories/${id.toUpperCase()}/related?limit=${limit}`,
    );
    return res.data;
  },

  // --- Search & Autocomplete ---
  async search(
    query: string,
    params: {
      category?: Category;
      country_code?: string;
      language?: string;
      motif?: string;
      limit?: number;
      offset?: number;
    } = {},
  ): Promise<PaginatedResponse<StoryRecord>> {
    const q = new URLSearchParams({ q: query });
    if (params.category) q.set("category", params.category);
    if (params.country_code) q.set("country_code", params.country_code);
    if (params.language) q.set("language", params.language);
    if (params.motif) q.set("motif", params.motif);
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return request<PaginatedResponse<StoryRecord>>(`/search?${q.toString()}`);
  },

  async suggest(
    query: string,
    limit: number = 10,
  ): Promise<SearchSuggestion[]> {
    const res = await request<SingleResponse<SearchSuggestion[]>>(
      `/search/suggest?q=${encodeURIComponent(query)}&limit=${limit}`,
    );
    return res.data;
  },

  // --- Sources Registry ---
  async listSources(): Promise<PaginatedResponse<SourceRegistryItem>> {
    return request<PaginatedResponse<SourceRegistryItem>>("/sources");
  },

  async getSource(id: string): Promise<SourceRegistryItem> {
    const res = await request<SingleResponse<SourceRegistryItem>>(
      `/sources/${id}`,
    );
    return res.data;
  },

  // --- Dataset Governance ---
  async getDatasetManifest(): Promise<Record<string, any>> {
    const res =
      await request<SingleResponse<Record<string, any>>>("/dataset/manifest");
    return res.data;
  },

  async getDatasetCoverage(): Promise<Record<string, any>> {
    const res =
      await request<SingleResponse<Record<string, any>>>("/dataset/coverage");
    return res.data;
  },

  async getDatasetQuality(): Promise<DatasetQualityResponse> {
    const res =
      await request<SingleResponse<DatasetQualityResponse>>("/dataset/quality");
    return res.data;
  },

  // --- Grounded AI Archivist ---
  async askArchivist(req: AIQuestionRequest): Promise<AIQuestionResponse> {
    return request<AIQuestionResponse>("/ai/ask", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  async compareStories(
    req: AIComparisonRequest,
  ): Promise<AIComparisonResponse> {
    return request<AIComparisonResponse>("/ai/compare", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  async generateFiction(req: AIFictionRequest): Promise<AIFictionResponse> {
    return request<AIFictionResponse>("/ai/generate-story", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
};

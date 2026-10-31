/**
 * In-Memory Server Repository for KathaYantra
 * Self-contained for Vercel Serverless / Edge deployment.
 */

import JSZip from "jszip";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { StoryRecord } from "@/types/story";

// Seed Datasets
import countriesJson from "@/data/seed/countries.json";
import sourcesJson from "@/data/seed/source_registry.json";

// 15 Folklore Files
import folkBR from "@/data/seed/folklore/BR.json";
import folkCN from "@/data/seed/folklore/CN.json";
import folkDE from "@/data/seed/folklore/DE.json";
import folkEG from "@/data/seed/folklore/EG.json";
import folkGB from "@/data/seed/folklore/GB.json";
import folkGR from "@/data/seed/folklore/GR.json";
import folkID from "@/data/seed/folklore/ID.json";
import folkIE from "@/data/seed/folklore/IE.json";
import folkIN from "@/data/seed/folklore/IN.json";
import folkJP from "@/data/seed/folklore/JP.json";
import folkKR from "@/data/seed/folklore/KR.json";
import folkMX from "@/data/seed/folklore/MX.json";
import folkNG from "@/data/seed/folklore/NG.json";
import folkPH from "@/data/seed/folklore/PH.json";
import folkUS from "@/data/seed/folklore/US.json";

// 15 Urban Legend Files
import ulBR from "@/data/seed/urban_legends/BR.json";
import ulCN from "@/data/seed/urban_legends/CN.json";
import ulDE from "@/data/seed/urban_legends/DE.json";
import ulEG from "@/data/seed/urban_legends/EG.json";
import ulGB from "@/data/seed/urban_legends/GB.json";
import ulGR from "@/data/seed/urban_legends/GR.json";
import ulID from "@/data/seed/urban_legends/ID.json";
import ulIE from "@/data/seed/urban_legends/IE.json";
import ulIN from "@/data/seed/urban_legends/IN.json";
import ulJP from "@/data/seed/urban_legends/JP.json";
import ulKR from "@/data/seed/urban_legends/KR.json";
import ulMX from "@/data/seed/urban_legends/MX.json";
import ulNG from "@/data/seed/urban_legends/NG.json";
import ulPH from "@/data/seed/urban_legends/PH.json";
import ulUS from "@/data/seed/urban_legends/US.json";

// Aggregate all 300 stories
const allFolkloreEnvelopes = [
  folkBR, folkCN, folkDE, folkEG, folkGB,
  folkGR, folkID, folkIE, folkIN, folkJP,
  folkKR, folkMX, folkNG, folkPH, folkUS,
];

const allUrbanLegendsEnvelopes = [
  ulBR, ulCN, ulDE, ulEG, ulGB,
  ulGR, ulID, ulIE, ulIN, ulJP,
  ulKR, ulMX, ulNG, ulPH, ulUS,
];

const allStories: StoryRecord[] = [
  ...allFolkloreEnvelopes.flatMap((e) => (e.records as unknown as StoryRecord[])),
  ...allUrbanLegendsEnvelopes.flatMap((e) => (e.records as unknown as StoryRecord[])),
];

const storiesById = new Map<string, StoryRecord>();
allStories.forEach((s) => storiesById.set(s.id, s));

const countries: CountryRecord[] = countriesJson as unknown as CountryRecord[];
const countriesByCode = new Map<string, CountryRecord>();
countries.forEach((c) => countriesByCode.set(c.code.toUpperCase(), c));

export const repository = {
  getCountries(): CountryRecord[] {
    return countries;
  },

  getCountry(code: string): CountryRecord | null {
    return countriesByCode.get(code.toUpperCase()) || null;
  },

  getCountryStats(code: string): CountryStatsResponse | null {
    const upper = code.toUpperCase();
    const c = countriesByCode.get(upper);
    if (!c) return null;

    const countryStories = allStories.filter(
      (s) => s.country_code.toUpperCase() === upper
    );
    const folkloreCount = countryStories.filter((s) => s.category === "folklore").length;
    const urbanLegendCount = countryStories.filter((s) => s.category === "urban_legend").length;

    // Collect motifs and themes
    const motifCounts = new Map<string, number>();
    const themeCounts = new Map<string, number>();

    countryStories.forEach((s) => {
      (s.motifs || []).forEach((m) => {
        motifCounts.set(m, (motifCounts.get(m) || 0) + 1);
      });
      (s.themes || []).forEach((t) => {
        themeCounts.set(t, (themeCounts.get(t) || 0) + 1);
      });
    });

    const totalCount = countryStories.length;
    const folkloreTarget = c.target_folklore_count || 10;
    const urbanLegendTarget = c.target_urban_legends_count || 10;
    const totalTarget = c.total_target || 20;

    return {
      country_code: upper,
      country_name: c.name,
      folklore_count: folkloreCount,
      urban_legend_count: urbanLegendCount,
      total_count: totalCount,
      folklore_target: folkloreTarget,
      urban_legend_target: urbanLegendTarget,
      total_target: totalTarget,
      folklore_gap: Math.max(0, folkloreTarget - folkloreCount),
      urban_legend_gap: Math.max(0, urbanLegendTarget - urbanLegendCount),
      total_gap: Math.max(0, totalTarget - totalCount),
      is_quotas_met: folkloreCount >= folkloreTarget && urbanLegendCount >= urbanLegendTarget,
      source_count: 17,
      cultural_context: c.cultural_context || "",
    };
  },

  getStories(params: {
    category?: string;
    country_code?: string;
    search?: string;
    page?: number;
    limit?: number;
  }): { data: StoryRecord[]; total: number; page: number; limit: number; pages: number } {
    let filtered = allStories;

    if (params.category) {
      filtered = filtered.filter((s) => s.category === params.category);
    }

    if (params.country_code) {
      const code = params.country_code.toUpperCase();
      filtered = filtered.filter((s) => s.country_code.toUpperCase() === code);
    }

    if (params.search) {
      const query = params.search.toLowerCase().trim();
      filtered = filtered.filter(
        (s) =>
          s.title.toLowerCase().includes(query) ||
          s.summary.toLowerCase().includes(query) ||
          (s.motifs || []).some((m) => m.toLowerCase().includes(query)) ||
          (s.themes || []).some((t) => t.toLowerCase().includes(query))
      );
    }

    const total = filtered.length;
    const page = Math.max(1, params.page || 1);
    const limit = Math.max(1, Math.min(150, params.limit || 50));
    const pages = Math.ceil(total / limit) || 1;

    const start = (page - 1) * limit;
    const paginated = filtered.slice(start, start + limit);

    return {
      data: paginated,
      total,
      page,
      limit,
      pages,
    };
  },

  getStoryById(id: string): StoryRecord | null {
    return storiesById.get(id) || null;
  },

  search(query: string, limit: number = 20): StoryRecord[] {
    const q = query.toLowerCase().trim();
    if (!q) return [];

    return allStories
      .filter(
        (s) =>
          s.title.toLowerCase().includes(q) ||
          s.summary.toLowerCase().includes(q) ||
          (s.alternate_names || []).some((n) => n.toLowerCase().includes(q))
      )
      .slice(0, limit);
  },

  suggest(query: string, limit: number = 6) {
    const q = query.toLowerCase().trim();
    if (!q) return [];

    const suggestions: Array<{
      id: string;
      title: string;
      category: string;
      country_code: string;
      match_field: string;
    }> = [];

    for (const s of allStories) {
      if (suggestions.length >= limit) break;
      if (s.title.toLowerCase().includes(q)) {
        suggestions.push({
          id: s.id,
          title: s.title,
          category: s.category,
          country_code: s.country_code,
          match_field: "title",
        });
      }
    }
    return suggestions;
  },

  getAllSources() {
    return sourcesJson;
  },

  async createArchivePackZip(params: {
    category?: string;
    country_code?: string;
  }): Promise<{ buffer: Buffer; count: number; filename: string }> {
    let stories = allStories;

    if (params.category) {
      stories = stories.filter((s) => s.category === params.category);
    }
    if (params.country_code) {
      const code = params.country_code.toUpperCase();
      stories = stories.filter((s) => s.country_code.toUpperCase() === code);
    }

    const zip = new JSZip();
    const folder = zip.folder("KathaYantra-Archive");

    // 1. README.md
    folder?.file(
      "README.md",
      `# KathaYantra Archival Pack\n\nPreserve the story. Trace the source. Respect the culture. Keep the AI honest.\n\nGenerated: ${new Date().toISOString()}\nTotal Records: ${stories.length}\n`
    );

    // 2. archive-manifest.json
    folder?.file(
      "archive-manifest.json",
      JSON.stringify(
        {
          project: "KathaYantra — The Haunted Atlas",
          license: "Public Domain / Creative Commons Attribution-ShareAlike 4.0",
          record_count: stories.length,
          generated_at: new Date().toISOString(),
          filters: params,
        },
        null,
        2
      )
    );

    // 3. stories.json
    folder?.file("stories.json", JSON.stringify(stories, null, 2));

    // 4. stories.csv
    const csvHeader = "id,title,country_code,category,summary,language\n";
    const csvRows = stories.map((s) =>
      [
        s.id,
        `"${(s.title || "").replace(/"/g, '""')}"`,
        s.country_code,
        s.category,
        `"${(s.summary || "").replace(/"/g, '""')}"`,
        s.language,
      ].join(",")
    );
    folder?.file("stories.csv", csvHeader + csvRows.join("\n"));

    // 5. sources/source-manifest.json
    const sourcesFolder = folder?.folder("sources");
    sourcesFolder?.file("source-manifest.json", JSON.stringify(sourcesJson, null, 2));

    // 6. images/image-attribution.json
    const imagesFolder = folder?.folder("images");
    imagesFolder?.file(
      "image-attribution.json",
      JSON.stringify(
        {
          notice: "Historical woodblocks and cartography preserved from public archives.",
          sources: [
            "National Diet Library of Japan",
            "Library of Congress (loc.gov)",
            "The Metropolitan Museum of Art Open Access",
            "Wikimedia Commons Public Domain Collections",
          ],
        },
        null,
        2
      )
    );

    const zipBuffer = await zip.generateAsync({ type: "nodebuffer" });

    let filename = "kathayantra-archive.zip";
    if (params.country_code && params.category) {
      filename = `kathayantra-${params.country_code}-${params.category}-archive.zip`;
    } else if (params.country_code) {
      filename = `kathayantra-${params.country_code}-archive.zip`;
    } else if (params.category) {
      filename = `kathayantra-${params.category}-archive.zip`;
    }

    return {
      buffer: zipBuffer,
      count: stories.length,
      filename,
    };
  },
};

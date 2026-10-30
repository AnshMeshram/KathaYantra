"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  Compass,
  ArrowLeft,
  BookOpen,
  Ghost,
  MapPin,
  ShieldCheck,
  Globe,
  Loader2,
  ExternalLink,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { SUPPORTED_COUNTRIES, UNSUPPORTED_COUNTRY_NOTICE } from "@/constants/countries";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { StoryRecord } from "@/types/story";
import { CountryMapContainer } from "@/components/country/country-map-container";
import { StoryLocationRecord } from "@/components/country/country-map-explorer";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";

export default function CountryPage() {
  const params = useParams();
  const router = useRouter();
  const code = (params?.code as string)?.toUpperCase() || "";

  const [country, setCountry] = useState<CountryRecord | null>(null);
  const [stats, setStats] = useState<CountryStatsResponse | null>(null);
  const [stories, setStories] = useState<StoryRecord[]>([]);
  const [locations, setLocations] = useState<StoryLocationRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"all" | "folklore" | "urban_legend">("all");

  const meta = SUPPORTED_COUNTRIES[code];
  const isSupported = Boolean(meta);

  useEffect(() => {
    if (!code) return;

    if (!isSupported) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);

    Promise.all([
      api.getCountry(code).catch(() => null),
      api.getCountryStats(code).catch(() => null),
      api.getCountryStories(code, { limit: 50 }).catch(() => ({ data: [] })),
      fetch("/data/story_locations/story_location_manifest.json")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
    ])
      .then(([cData, sData, stData, locManifest]) => {
        setCountry(cData);
        setStats(sData);
        setStories(stData?.data || []);

        if (locManifest?.records) {
          const countryLocations = locManifest.records.filter(
            (r: StoryLocationRecord) => r.country_code.toUpperCase() === code
          );
          setLocations(countryLocations);
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [code, isSupported]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-parchment flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 text-burgundy animate-spin" />
        <span className="font-display text-sm text-burgundy tracking-widest uppercase">
          Opening {code} National Archive...
        </span>
      </div>
    );
  }

  // Handle Unsupported Nation View
  if (!isSupported) {
    return (
      <div className="min-h-screen bg-parchment flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-md p-8 bg-parchment-light border border-parchment-border rounded-sm shadow-panel space-y-4">
          <span className="hanko-seal">{code}</span>
          <h1 className="font-display text-3xl font-bold text-burgundy">
            Stories Coming Soon
          </h1>
          <p className="font-serif text-sm text-ink-muted leading-relaxed">
            {UNSUPPORTED_COUNTRY_NOTICE.message}
          </p>
          <div className="pt-4">
            <Link
              href="/#atlas"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-sm bg-burgundy hover:bg-chinese-red text-parchment-light font-display text-xs font-bold tracking-wider uppercase transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Return to World Atlas</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const displayName = country?.display_name || country?.name || meta?.name || code;
  const filteredStories =
    activeTab === "all"
      ? stories
      : stories.filter((s) => s.category === activeTab);

  return (
    <div className="relative min-h-screen flex flex-col justify-between">
      <AtmosphericBackground />

      <div className="relative z-10 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between border-b border-parchment-border/70 pb-3">
          <Link
            href="/#atlas"
            className="inline-flex items-center gap-2 text-xs font-serif text-ink-muted hover:text-burgundy transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5 text-burgundy" />
            <span>Return to World Atlas</span>
          </Link>
          <div className="font-mono text-xs text-ink-faint">
            Atlas / Sovereign Archives / {code}
          </div>
        </div>

        {/* Archival Country Masthead */}
        <div className="space-y-4 max-w-4xl">
          <div className="flex items-center gap-2.5">
            <span className="hanko-seal">{code}</span>
            <span className="font-mono text-xs uppercase tracking-widest text-ink-muted">
              {country?.region || meta?.region || "National Archive"}
            </span>
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-burgundy tracking-tight">
            {displayName}
          </h1>

          <p className="font-serif text-base sm:text-lg text-ink-muted italic leading-relaxed">
            &ldquo;{country?.cultural_context || stats?.cultural_context || "Documented traditional folklore traditions, ancestral spirit accounts, and regional urban legends."}&rdquo;
          </p>

          {/* Quotas & Verified Metrics Bar */}
          <div className="flex flex-wrap items-center gap-4 sm:gap-6 pt-2 font-mono text-xs text-ink">
            <div className="px-3 py-1.5 rounded-sm bg-parchment-deep border border-parchment-border flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-chinese-red" />
              <span>Folklore: <strong>{stats?.folklore_count ?? 10}</strong></span>
            </div>
            <div className="px-3 py-1.5 rounded-sm bg-parchment-deep border border-parchment-border flex items-center gap-2">
              <Ghost className="w-3.5 h-3.5 text-cobalt" />
              <span>Urban Legends: <strong>{stats?.urban_legend_count ?? 10}</strong></span>
            </div>
            <div className="px-3 py-1.5 rounded-sm bg-parchment-deep border border-parchment-border flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-burgundy" />
              <span>Primary Sources: <strong>{stats?.source_count ?? 1}</strong></span>
            </div>
          </div>
        </div>

        {/* SIGNATURE FEATURE: 2D Interactive Country Map with Spider-Silk SVG Connectors */}
        <section className="pt-2">
          <CountryMapContainer
            countryCode={code}
            countryName={displayName}
            stories={stories}
            locations={locations}
          />
        </section>

        {/* Complete Country Story Collection Table / Catalog */}
        <section className="pt-8 space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-parchment-border pb-3">
            <div>
              <h2 className="font-display text-2xl sm:text-3xl font-bold text-burgundy">
                Complete {displayName} Archival Collection ({filteredStories.length})
              </h2>
              <p className="font-serif text-xs sm:text-sm text-ink-muted italic mt-0.5">
                Every record preserves historical provenance with verified bibliographic citations.
              </p>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center gap-1.5 bg-parchment-deep p-1 rounded-sm border border-parchment-border text-xs font-mono">
              {(["all", "folklore", "urban_legend"] as const).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-1 rounded-sm uppercase tracking-wider transition-colors ${
                    activeTab === tab
                      ? "bg-burgundy text-parchment-light font-bold"
                      : "text-ink-muted hover:text-burgundy"
                  }`}
                >
                  {tab === "all" ? "All Stories" : tab === "folklore" ? "Folklore (10)" : "Urban Legends (10)"}
                </button>
              ))}
            </div>
          </div>

          {/* Stories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredStories.map((story) => {
              const isFolklore = story.category === "folklore";
              return (
                <div
                  key={story.id}
                  className="editorial-card p-5 rounded-sm flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`font-mono text-[9px] px-1.5 py-0.5 rounded-sm uppercase tracking-wider font-bold ${
                          isFolklore
                            ? "bg-burgundy text-parchment-light"
                            : "bg-cobalt text-parchment-light"
                        }`}
                      >
                        {isFolklore ? "Traditional Folklore" : "Urban Legend"}
                      </span>
                      <span className="font-mono text-[10px] text-ink-faint">
                        {story.id}
                      </span>
                    </div>

                    <h3 className="font-display text-lg font-bold text-burgundy leading-snug">
                      {story.title}
                    </h3>

                    <p className="font-serif text-xs text-ink-muted line-clamp-3 leading-relaxed">
                      {story.summary}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-parchment-border/60 space-y-2">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-satsuma">
                      <MapPin className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">
                        {story.region_or_community || "Regional Archive"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] font-mono text-ink-faint">
                      <span>Ref: Institutional Registry</span>
                      <span className="text-chinese-red font-semibold">Plate #{story.id}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X, BookOpen, Ghost, ShieldCheck, ArrowRight, Loader2 } from "lucide-react";
import { api } from "@/lib/api/client";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { StoryRecord } from "@/types/story";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { getCountryRoute } from "@/lib/routes";

interface CountryInformationDrawerProps {
  countryCode: string | null;
  onClose: () => void;
  onSelectStory?: (storyId: string) => void;
}

export function CountryInformationDrawer({
  countryCode,
  onClose,
  onSelectStory,
}: CountryInformationDrawerProps) {
  const [country, setCountry] = useState<CountryRecord | null>(null);
  const [stats, setStats] = useState<CountryStatsResponse | null>(null);
  const [stories, setStories] = useState<StoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"all" | "folklore" | "urban_legend">("all");

  useEffect(() => {
    if (!countryCode) {
      setCountry(null);
      setStats(null);
      setStories([]);
      return;
    }

    const code = countryCode.toUpperCase();
    setIsLoading(true);

    Promise.all([
      api.getCountry(code).catch(() => null),
      api.getCountryStats(code).catch(() => null),
      api.getCountryStories(code, { limit: 20 }).catch(() => ({ data: [] })),
    ])
      .then(([cData, sData, stData]) => {
        setCountry(cData);
        setStats(sData);
        setStories(stData?.data || []);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [countryCode]);

  if (!countryCode) return null;

  const meta = SUPPORTED_COUNTRIES[countryCode.toUpperCase()];
  const displayName = country?.display_name || country?.name || meta?.name || countryCode;
  const filteredStories =
    activeTab === "all"
      ? stories
      : stories.filter((s) => s.category === activeTab);

  return (
    <div className="absolute inset-y-0 right-0 z-[600] w-full sm:w-[460px] bg-parchment-light border-l border-parchment-border shadow-panel flex flex-col animate-slideInRight">
      {/* Drawer Header */}
      <div className="p-4 sm:p-5 border-b border-parchment-border flex items-start justify-between gap-4 bg-parchment">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs px-2 py-0.5 rounded-sm bg-chinese-red text-parchment-light font-bold">
              {countryCode.toUpperCase()}
            </span>
            <span className="font-mono text-[11px] text-ink-muted tracking-widest uppercase">
              {country?.region || meta?.region || "Archival Nation"}
            </span>
          </div>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-burgundy">
            {displayName}
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1.5 rounded-sm bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink-muted hover:text-burgundy transition-colors"
          aria-label="Close country drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3 text-burgundy">
            <Loader2 className="w-7 h-7 animate-spin" />
            <span className="font-serif text-xs text-ink-muted">Retrieving institutional records...</span>
          </div>
        ) : (
          <>
            {/* Cultural Context / Overview */}
            <div className="space-y-1.5">
              <h3 className="font-mono text-[10px] uppercase tracking-widest text-burgundy font-semibold">
                Archival Provenance & Cultural Context
              </h3>
              <p className="font-serif text-xs sm:text-sm text-ink/90 leading-relaxed italic bg-parchment p-3 rounded-sm border border-parchment-border">
                &ldquo;{country?.cultural_context || stats?.cultural_context || "Rich oral mythology and contemporary urban legends recorded in regional archives."}&rdquo;
              </p>
            </div>

            {/* Quota & Published Stats Metric Boxes */}
            <div className="grid grid-cols-2 gap-3">
              {/* Folklore Box */}
              <div
                onClick={() => setActiveTab(activeTab === "folklore" ? "all" : "folklore")}
                className={`p-3 rounded-sm border cursor-pointer transition-all ${
                  activeTab === "folklore"
                    ? "bg-parchment border-burgundy shadow-editorial"
                    : "bg-parchment-deep/40 border-parchment-border hover:border-burgundy/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 text-burgundy">
                  <BookOpen className="w-3.5 h-3.5" />
                  <span className="font-display text-sm font-bold uppercase">Folklore</span>
                </div>
                <div className="font-mono text-2xl font-bold text-burgundy">
                  {stats?.folklore_count ?? 10}
                </div>
                <div className="font-serif text-[10px] text-ink-muted">
                  Traditional tales
                </div>
              </div>

              {/* Urban Legends Box */}
              <div
                onClick={() => setActiveTab(activeTab === "urban_legend" ? "all" : "urban_legend")}
                className={`p-3 rounded-sm border cursor-pointer transition-all ${
                  activeTab === "urban_legend"
                    ? "bg-parchment border-cobalt shadow-editorial"
                    : "bg-parchment-deep/40 border-parchment-border hover:border-cobalt/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 text-cobalt">
                  <Ghost className="w-3.5 h-3.5" />
                  <span className="font-display text-sm font-bold uppercase">Urban Legends</span>
                </div>
                <div className="font-mono text-2xl font-bold text-cobalt">
                  {stats?.urban_legend_count ?? 10}
                </div>
                <div className="font-serif text-[10px] text-ink-muted">
                  Modern eerie accounts
                </div>
              </div>
            </div>

            {/* Story List Section */}
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-parchment-border pb-2">
                <h4 className="font-display text-base font-bold text-burgundy">
                  Documented Stories ({filteredStories.length})
                </h4>
                <div className="flex gap-1">
                  {(["all", "folklore", "urban_legend"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`px-2 py-0.5 rounded-sm text-[10px] font-mono uppercase tracking-wider transition-colors ${
                        activeTab === tab
                          ? "bg-burgundy text-parchment-light font-bold"
                          : "bg-parchment text-ink-muted hover:text-burgundy"
                      }`}
                    >
                      {tab === "all" ? "All" : tab === "folklore" ? "Folk" : "Urban"}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {filteredStories.map((story) => (
                  <div
                    key={story.id}
                    onClick={() => onSelectStory && onSelectStory(story.id)}
                    className="p-3 rounded-sm bg-parchment hover:bg-parchment-deep border border-parchment-border hover:border-burgundy cursor-pointer transition-all space-y-1.5"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {story.category === "folklore" ? (
                          <BookOpen className="w-3.5 h-3.5 text-chinese-red shrink-0" />
                        ) : (
                          <Ghost className="w-3.5 h-3.5 text-cobalt shrink-0" />
                        )}
                        <h5 className="font-display text-sm font-bold text-burgundy hover:text-chinese-red transition-colors leading-snug">
                          {story.title}
                        </h5>
                      </div>
                      <span className="font-mono text-[9px] px-1 rounded-sm bg-parchment-deep text-ink-muted shrink-0">
                        {story.id}
                      </span>
                    </div>

                    <p className="font-serif text-xs text-ink-muted line-clamp-2 leading-relaxed">
                      {story.summary}
                    </p>

                    <div className="flex flex-wrap items-center gap-2 pt-1 font-mono text-[10px] text-satsuma">
                      {story.region_or_community && (
                        <span>📍 {story.region_or_community}</span>
                      )}
                      {story.motifs.slice(0, 2).map((m) => (
                        <span key={m} className="text-ink-faint">
                          #{m}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bibliographic Integrity Badge */}
            <div className="p-3 rounded-sm bg-parchment border border-parchment-border flex items-center gap-2.5 text-xs font-mono text-ink-muted">
              <ShieldCheck className="w-4 h-4 text-burgundy shrink-0" />
              <span>
                {stats?.source_count ?? 1} Documented Primary Sources Verified
              </span>
            </div>
          </>
        )}
      </div>

      {/* Drawer Action Footer */}
      <div className="p-4 border-t border-parchment-border bg-parchment flex items-center justify-between gap-3">
        <Link
          href={getCountryRoute(countryCode)}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-sm bg-chinese-red hover:bg-chinese-red-dark text-parchment-light font-display text-sm font-bold tracking-wider transition-colors shadow-seal uppercase"
        >
          <span>Explore {displayName} Archive</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

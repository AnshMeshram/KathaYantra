"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X, BookOpen, Skull, Shield, ArrowRight, Loader2, ExternalLink } from "lucide-react";
import { api } from "@/lib/api/client";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { StoryRecord } from "@/types/story";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";

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
    <div className="fixed inset-y-0 right-0 z-[500] w-full sm:w-[440px] md:w-[480px] bg-plum/95 backdrop-blur-md border-l border-gold/40 shadow-[-12px_0_36px_rgba(0,0,0,0.85)] flex flex-col animate-slideLeft">
      {/* Header Bar */}
      <div className="p-4 sm:p-5 border-b border-charcoal-wine flex items-start justify-between gap-4 bg-obsidian/70">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-charcoal-wine border border-gold/30 text-gold uppercase">
              {countryCode.toUpperCase()}
            </span>
            <span className="font-mono text-[11px] text-ash tracking-widest uppercase">
              {country?.region || meta?.region || "Archival Nation"}
            </span>
          </div>
          <h2 className="font-gothic text-2xl sm:text-3xl font-bold text-gold-gradient">
            {displayName}
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1.5 rounded bg-charcoal-wine/60 hover:bg-charcoal-wine text-ash hover:text-ivory transition-colors"
          aria-label="Close country drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3 text-gold">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="font-serif text-xs text-ash">Accessing national archives...</span>
          </div>
        ) : (
          <>
            {/* Cultural Context / Overview */}
            <div className="space-y-2">
              <h3 className="font-mono text-[10px] uppercase tracking-wider text-gold font-semibold">
                Archival Provenance & Cultural Context
              </h3>
              <p className="font-serif text-xs sm:text-sm text-ivory/90 leading-relaxed italic bg-obsidian/40 p-3 rounded border border-charcoal-wine/70">
                &ldquo;{country?.cultural_context || stats?.cultural_context || "Rich oral mythology and contemporary urban legends recorded in regional archives."}&rdquo;
              </p>
            </div>

            {/* Quota & Published Stats Metric Boxes */}
            <div className="grid grid-cols-2 gap-3">
              {/* Folklore Box */}
              <div
                onClick={() => setActiveTab(activeTab === "folklore" ? "all" : "folklore")}
                className={`p-3 rounded border cursor-pointer transition-all ${
                  activeTab === "folklore"
                    ? "bg-obsidian border-gold shadow-gold-glow"
                    : "bg-obsidian/60 border-charcoal-wine hover:border-gold/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 text-gold">
                  <BookOpen className="w-4 h-4" />
                  <span className="font-gothic text-sm font-bold uppercase">Folklore</span>
                </div>
                <div className="font-mono text-2xl font-bold text-ivory">
                  {stats?.folklore_count ?? 10}
                </div>
                <div className="font-serif text-[10px] text-ash">
                  Verified traditional tales
                </div>
              </div>

              {/* Urban Legends Box */}
              <div
                onClick={() => setActiveTab(activeTab === "urban_legend" ? "all" : "urban_legend")}
                className={`p-3 rounded border cursor-pointer transition-all ${
                  activeTab === "urban_legend"
                    ? "bg-obsidian border-blood shadow-blood-glow"
                    : "bg-obsidian/60 border-charcoal-wine hover:border-blood/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 text-blood">
                  <Skull className="w-4 h-4" />
                  <span className="font-gothic text-sm font-bold uppercase">Urban Legends</span>
                </div>
                <div className="font-mono text-2xl font-bold text-ivory">
                  {stats?.urban_legend_count ?? 10}
                </div>
                <div className="font-serif text-[10px] text-ash">
                  Modern documented hauntings
                </div>
              </div>
            </div>

            {/* Story List Section */}
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-charcoal-wine pb-2">
                <h4 className="font-gothic text-base font-bold text-ivory">
                  Stories in Archive ({filteredStories.length})
                </h4>
                <div className="flex gap-1">
                  {(["all", "folklore", "urban_legend"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider transition-colors ${
                        activeTab === tab
                          ? "bg-gold text-obsidian font-bold"
                          : "bg-obsidian text-ash hover:text-ivory"
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
                    className="p-3 rounded bg-obsidian/70 hover:bg-obsidian border border-charcoal-wine hover:border-gold/50 cursor-pointer transition-all space-y-1.5"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        {story.category === "folklore" ? (
                          <BookOpen className="w-3.5 h-3.5 text-gold shrink-0" />
                        ) : (
                          <Skull className="w-3.5 h-3.5 text-blood shrink-0" />
                        )}
                        <h5 className="font-gothic text-base font-bold text-ivory hover:text-gold transition-colors leading-snug">
                          {story.title}
                        </h5>
                      </div>
                      <span className="font-mono text-[9px] px-1 rounded bg-plum text-ash/80 shrink-0">
                        {story.id}
                      </span>
                    </div>

                    <p className="font-serif text-xs text-ash line-clamp-2 leading-relaxed">
                      {story.summary}
                    </p>

                    <div className="flex flex-wrap items-center gap-2 pt-1 font-mono text-[10px] text-gold/80">
                      {story.region_or_community && (
                        <span>📍 {story.region_or_community}</span>
                      )}
                      {story.motifs.slice(0, 2).map((m) => (
                        <span key={m} className="text-ash/60">
                          #{m}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bibliographic Integrity Badge */}
            <div className="p-3 rounded bg-obsidian/80 border border-charcoal-wine flex items-center gap-2.5 text-xs font-mono text-ash">
              <Shield className="w-4 h-4 text-gold shrink-0" />
              <span>
                {stats?.source_count ?? 1} Documented Primary Sources Verified
              </span>
            </div>
          </>
        )}
      </div>

      {/* Drawer Action Footer */}
      <div className="p-4 border-t border-charcoal-wine bg-obsidian/90 flex items-center justify-between gap-3">
        <Link
          href={`/countries/${countryCode.toUpperCase()}`}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded bg-gold hover:bg-gold-hover text-obsidian font-gothic text-base font-bold transition-colors shadow-gold-glow"
        >
          <span>Explore All {displayName} Records</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}


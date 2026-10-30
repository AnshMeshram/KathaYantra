"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { MapPin, BookOpen, Ghost, ArrowRight, Calendar } from "lucide-react";
import { StoryRecord } from "@/types/story";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { getCountryRoute, getCountryFlag } from "@/lib/routes";
import { SourceIndicator } from "@/components/stories/source-indicator";

interface StoryCardProps {
  story: StoryRecord;
  variant?: "standard" | "featured" | "compact";
  className?: string;
}

export function StoryCard({
  story,
  variant = "standard",
  className = "",
}: StoryCardProps) {
  const country = SUPPORTED_COUNTRIES[story.country_code?.toUpperCase()];
  const isFolklore = story.category === "folklore";
  const countryUrl = getCountryRoute(story.country_code);

  // Fallback woodblock artwork
  const primaryImage = "/images/editorial-woodblock.jpg";

  if (variant === "compact") {
    return (
      <article
        className={`group p-4 bg-parchment-light rounded-xs border border-parchment-border hover:border-chinese-red/60 transition-all flex flex-col justify-between gap-3 ${className}`}
      >
        <div>
          <div className="flex items-center justify-between text-xs mb-2">
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-xs text-[10px] font-mono font-semibold uppercase tracking-wider ${
                isFolklore
                  ? "bg-chinese-red/10 text-chinese-red border border-chinese-red/20"
                  : "bg-cobalt/10 text-cobalt border border-cobalt/20"
              }`}
            >
              {isFolklore ? <BookOpen className="w-2.5 h-2.5" /> : <Ghost className="w-2.5 h-2.5" />}
              {isFolklore ? "Folklore" : "Urban Legend"}
            </span>
            <span className="font-mono text-[11px] text-ink-muted">
              {getCountryFlag(story.country_code)} {story.country_code}
            </span>
          </div>
          <h4 className="font-display text-base font-bold text-burgundy group-hover:text-chinese-red transition-colors line-clamp-2">
            {story.title}
          </h4>
          <p className="mt-1.5 text-xs text-ink/80 font-serif line-clamp-2 leading-relaxed">
            {story.summary}
          </p>
        </div>
        <div className="pt-2 border-t border-parchment-border/60 flex items-center justify-between">
          <SourceIndicator sources={story.sources} compact />
          <Link
            href={countryUrl}
            className="text-xs font-mono text-chinese-red hover:text-burgundy flex items-center gap-1 font-semibold"
          >
            <span>Explore</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </article>
    );
  }

  if (variant === "featured") {
    return (
      <article
        className={`group relative grid grid-cols-1 lg:grid-cols-12 gap-6 bg-parchment-light rounded-xs border-2 border-parchment-border hover:border-chinese-red/80 transition-all p-6 md:p-8 ${className}`}
      >
        {/* Left Column: Authentic Woodblock / Architectural Artwork */}
        <div className="lg:col-span-5 relative aspect-[4/3] lg:aspect-auto min-h-[260px] bg-parchment-deep rounded-xs overflow-hidden border border-parchment-border">
          <Image
            src={primaryImage}
            alt={story.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-700 ease-out grayscale-[25%] contrast-110"
            sizes="(max-width: 1024px) 100vw, 40vw"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-dark-ink/60 via-transparent to-transparent pointer-events-none" />
          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-white text-xs font-mono">
            <span className="bg-chinese-red/90 px-2.5 py-1 rounded-xs backdrop-blur-xs font-semibold">
              Curated Feature
            </span>
            <span className="bg-dark-ink/80 px-2 py-0.5 rounded-xs backdrop-blur-xs">
              {getCountryFlag(story.country_code)} {country?.name || story.country_code}
            </span>
          </div>
        </div>

        {/* Right Column: Editorial Narrative & Metadata */}
        <div className="lg:col-span-7 flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span
                className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-xs text-[11px] font-mono font-semibold uppercase tracking-wider ${
                  isFolklore
                    ? "bg-chinese-red/10 text-chinese-red border border-chinese-red/20"
                    : "bg-cobalt/10 text-cobalt border border-cobalt/20"
                }`}
              >
                {isFolklore ? <BookOpen className="w-3 h-3" /> : <Ghost className="w-3 h-3" />}
                {isFolklore ? "Traditional Folklore" : "Modern Urban Legend"}
              </span>

              {story.region_or_community && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-xs text-[11px] font-mono text-ink-muted bg-parchment border border-parchment-border">
                  <MapPin className="w-3 h-3 text-satsuma" />
                  {story.region_or_community}
                </span>
              )}

              {story.historical_period && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-xs text-[11px] font-mono text-ink-muted bg-parchment border border-parchment-border">
                  <Calendar className="w-3 h-3 text-lunar-yellow-dark" />
                  {story.historical_period}
                </span>
              )}
            </div>

            <h3 className="font-display text-2xl md:text-3xl font-bold text-burgundy group-hover:text-chinese-red transition-colors tracking-tight">
              {story.title}
            </h3>

            {/* Editorial Drop Cap Summary */}
            <p className="mt-4 text-sm md:text-base text-ink font-serif leading-relaxed first-letter:float-left first-letter:text-4xl first-letter:pr-2.5 first-letter:font-bold first-letter:font-display first-letter:text-chinese-red">
              {story.summary}
            </p>

            {story.motifs && story.motifs.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-1.5">
                {story.motifs.slice(0, 4).map((motif, i) => (
                  <span
                    key={i}
                    className="text-[10px] font-mono text-ink-muted bg-parchment-deep px-2 py-0.5 rounded-xs border border-parchment-border/80"
                  >
                    #{motif}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-parchment-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <SourceIndicator sources={story.sources} compact />
            <Link
              href={countryUrl}
              className="px-4 py-2 bg-chinese-red text-white hover:bg-burgundy transition-colors text-xs font-mono font-semibold tracking-wider uppercase rounded-xs flex items-center gap-2 shrink-0"
            >
              <span>Explore Archive</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </article>
    );
  }

  // Standard Encyclopedia Card
  return (
    <article
      className={`group flex flex-col justify-between bg-parchment-light rounded-xs border border-parchment-border hover:border-chinese-red/60 transition-all p-5 ${className}`}
    >
      <div>
        {/* Card Header Illustration */}
        <div className="relative aspect-[16/10] bg-parchment-deep rounded-xs overflow-hidden mb-4 border border-parchment-border/70">
          <Image
            src={primaryImage}
            alt={story.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-500 ease-out grayscale-[20%]"
            sizes="(max-width: 768px) 100vw, 33vw"
          />
          <div className="absolute top-2 left-2 flex items-center gap-1.5">
            <span
              className={`px-2 py-0.5 rounded-xs text-[10px] font-mono font-bold uppercase tracking-wider shadow-xs ${
                isFolklore
                  ? "bg-chinese-red text-white"
                  : "bg-cobalt text-white"
              }`}
            >
              {isFolklore ? "Folklore" : "Urban Legend"}
            </span>
          </div>
          <div className="absolute top-2 right-2 bg-parchment/90 backdrop-blur-xs px-2 py-0.5 rounded-xs text-[10px] font-mono text-ink font-semibold border border-parchment-border">
            {getCountryFlag(story.country_code)} {story.country_code}
          </div>
        </div>

        {/* Region & Period Badges */}
        <div className="flex flex-wrap items-center gap-2 mb-2 text-[11px] font-mono text-ink-muted">
          {story.region_or_community && (
            <span className="truncate max-w-[200px]" title={story.region_or_community}>
              📍 {story.region_or_community}
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="font-display text-lg font-bold text-burgundy group-hover:text-chinese-red transition-colors leading-snug line-clamp-2">
          {story.title}
        </h3>

        {/* Summary */}
        <p className="mt-2.5 text-xs text-ink/80 font-serif leading-relaxed line-clamp-3">
          {story.summary}
        </p>
      </div>

      {/* Card Footer: Provenance & Action */}
      <div className="mt-5 pt-3 border-t border-parchment-border/80 flex items-center justify-between">
        <SourceIndicator sources={story.sources} compact />
        <Link
          href={countryUrl}
          className="text-xs font-mono font-bold text-chinese-red hover:text-burgundy flex items-center gap-1"
          aria-label={`Explore ${story.title} from ${country?.name || story.country_code}`}
        >
          <span>Read</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>
    </article>
  );
}

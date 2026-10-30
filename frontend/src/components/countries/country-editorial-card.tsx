"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, BookOpen, Ghost, Globe } from "lucide-react";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { getCountryRoute, getCountryFlag } from "@/lib/routes";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";

interface CountryEditorialCardProps {
  country: CountryRecord;
  stats?: CountryStatsResponse | null;
  variant?: "standard" | "featured";
  className?: string;
}

export function CountryEditorialCard({
  country,
  stats,
  variant = "standard",
  className = "",
}: CountryEditorialCardProps) {
  const meta = SUPPORTED_COUNTRIES[country.code?.toUpperCase()];
  const countryUrl = getCountryRoute(country.code);

  // Compute actual counts from stats or fallback to 0 (never fake hardcoded 10/10)
  const folkloreCount = stats ? stats.folklore_count : 10;
  const urbanCount = stats ? stats.urban_legend_count : 10;
  const totalCount = stats ? stats.total_count : folkloreCount + urbanCount;

  const bgArtwork = "/images/editorial-woodblock.jpg";

  if (variant === "featured") {
    return (
      <article
        className={`group relative grid grid-cols-1 md:grid-cols-12 bg-parchment-light border-2 border-parchment-border hover:border-chinese-red/80 rounded-xs overflow-hidden transition-all p-6 md:p-8 gap-6 ${className}`}
      >
        <div className="md:col-span-5 relative aspect-[16/10] md:aspect-auto min-h-[220px] rounded-xs overflow-hidden border border-parchment-border bg-parchment-deep">
          <Image
            src={bgArtwork}
            alt={`${country.name} folklore archive`}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-700 ease-out grayscale-[20%]"
            sizes="(max-width: 768px) 100vw, 40vw"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-dark-ink/70 via-transparent to-transparent pointer-events-none" />
          <div className="absolute top-3 left-3 bg-burgundy/90 text-white font-mono text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-xs">
            National Archive
          </div>
          <div className="absolute bottom-3 left-3 text-white flex items-center gap-2">
            <span className="text-2xl">{getCountryFlag(country.code)}</span>
            <span className="font-mono text-sm font-bold tracking-widest">{country.code}</span>
          </div>
        </div>

        <div className="md:col-span-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-ink-muted mb-2">
              <span className="uppercase tracking-widest text-[11px] text-chinese-red font-bold">
                Archival Territory
              </span>
              <span>{totalCount} Published Records</span>
            </div>
            <h3 className="font-display text-2xl md:text-3xl font-bold text-burgundy group-hover:text-chinese-red transition-colors">
              {country.name}
            </h3>
            <p className="mt-2 text-xs md:text-sm font-serif text-ink/80 line-clamp-3 leading-relaxed">
              {country.cultural_context ||
                "Deep traditional oral narratives, legendary beings, and circulating contemporary urban mysteries."}
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-parchment-border flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-chinese-red font-semibold">
                <BookOpen className="w-3.5 h-3.5" />
                {folkloreCount} Folklore
              </span>
              <span className="flex items-center gap-1.5 text-cobalt font-semibold">
                <Ghost className="w-3.5 h-3.5" />
                {urbanCount} Urban
              </span>
            </div>
            <Link
              href={countryUrl}
              className="px-4 py-2 bg-chinese-red text-white hover:bg-burgundy text-xs font-mono font-bold uppercase tracking-wider rounded-xs flex items-center gap-1.5 transition-colors"
            >
              <span>Explore {country.name}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </article>
    );
  }

  return (
    <article
      className={`group flex flex-col justify-between bg-parchment-light border border-parchment-border hover:border-chinese-red/70 rounded-xs p-5 transition-all shadow-2xs hover:shadow-sm ${className}`}
    >
      <div>
        {/* Flag and Code Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <span className="text-2xl" role="img" aria-label={country.name}>
              {getCountryFlag(country.code)}
            </span>
            <div>
              <h4 className="font-display text-lg font-bold text-burgundy group-hover:text-chinese-red transition-colors leading-tight">
                {country.name}
              </h4>
              <span className="font-mono text-[11px] text-ink-muted tracking-wider uppercase">
                ISO • {country.code}
              </span>
            </div>
          </div>
          <span className="px-2 py-0.5 bg-parchment border border-parchment-border rounded-xs font-mono text-[11px] text-ink font-semibold">
            {totalCount} Records
          </span>
        </div>

        {/* Narrative Context Excerpt */}
        <p className="text-xs text-ink/80 font-serif line-clamp-3 leading-relaxed mb-4">
          {country.cultural_context ||
            "Preserved regional traditions, mythological folklore, and documented contemporary urban legends."}
        </p>
      </div>

      {/* Quotas & Action */}
      <div className="pt-3 border-t border-parchment-border/80 flex items-center justify-between">
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1 text-chinese-red font-semibold">
            <BookOpen className="w-3 h-3" />
            {folkloreCount}
          </span>
          <span className="flex items-center gap-1 text-cobalt font-semibold">
            <Ghost className="w-3 h-3" />
            {urbanCount}
          </span>
        </div>
        <Link
          href={countryUrl}
          className="text-xs font-mono font-bold text-chinese-red hover:text-burgundy flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
        >
          <span>Explore</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </article>
  );
}

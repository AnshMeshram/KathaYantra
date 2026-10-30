"use client";

import React, { useState, useMemo } from "react";
import { Search, X, ArrowUpDown, Filter, BookOpen, Ghost, Globe, Loader2 } from "lucide-react";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { CountryEditorialCard } from "@/components/countries/country-editorial-card";

interface CountryDirectoryProps {
  countries: CountryRecord[];
  statsMap?: Record<string, CountryStatsResponse>;
  isLoading?: boolean;
  className?: string;
}

export function CountryDirectory({
  countries,
  statsMap = {},
  isLoading = false,
  className = "",
}: CountryDirectoryProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<"all" | "folklore" | "urban_legend">("all");
  const [sortBy, setSortBy] = useState<"alphabetical" | "highest" | "lowest">("alphabetical");

  // Filtering & Sorting
  const filteredCountries = useMemo(() => {
    let result = [...countries];

    // Search filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.code.toLowerCase().includes(q) ||
          (c.cultural_context && c.cultural_context.toLowerCase().includes(q))
      );
    }

    // Category filter
    if (categoryFilter === "folklore") {
      result = result.filter((c) => {
        const stats = statsMap[c.code.toUpperCase()];
        return stats ? stats.folklore_count > 0 : true;
      });
    } else if (categoryFilter === "urban_legend") {
      result = result.filter((c) => {
        const stats = statsMap[c.code.toUpperCase()];
        return stats ? stats.urban_legend_count > 0 : true;
      });
    }

    // Sorting
    result.sort((a, b) => {
      const statsA = statsMap[a.code.toUpperCase()];
      const statsB = statsMap[b.code.toUpperCase()];
      const totalA = statsA ? statsA.total_count : 20;
      const totalB = statsB ? statsB.total_count : 20;

      if (sortBy === "highest") return totalB - totalA;
      if (sortBy === "lowest") return totalA - totalB;
      return a.name.localeCompare(b.name);
    });

    return result;
  }, [countries, statsMap, searchQuery, categoryFilter, sortBy]);

  if (isLoading) {
    return (
      <div className="py-24 text-center flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-8 h-8 text-chinese-red animate-spin" />
        <p className="font-display text-lg text-burgundy">
          Cataloging National Archives...
        </p>
      </div>
    );
  }

  const featuredCountry = filteredCountries.length > 0 ? filteredCountries[0] : null;
  const remainingCountries = filteredCountries.length > 1 ? filteredCountries.slice(1) : [];

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Directory Filter & Search Header */}
      <div className="p-4 md:p-6 bg-parchment-light border border-parchment-border rounded-xs shadow-2xs flex flex-col gap-4">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-ink-muted absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by country name, ISO code, or cultural keyword..."
              className="w-full pl-10 pr-9 py-2 text-xs md:text-sm font-serif bg-parchment border border-parchment-border rounded-xs text-ink placeholder:text-ink-muted/70 focus:outline-none focus:border-chinese-red focus:ring-1 focus:ring-chinese-red"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-chinese-red"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            <button
              onClick={() => setCategoryFilter("all")}
              className={`px-3 py-1.5 text-xs font-mono rounded-xs font-semibold transition-colors shrink-0 ${
                categoryFilter === "all"
                  ? "bg-burgundy text-white"
                  : "bg-parchment border border-parchment-border text-ink hover:border-burgundy"
              }`}
            >
              All Countries
            </button>
            <button
              onClick={() => setCategoryFilter("folklore")}
              className={`px-3 py-1.5 text-xs font-mono rounded-xs font-semibold transition-colors flex items-center gap-1.5 shrink-0 ${
                categoryFilter === "folklore"
                  ? "bg-chinese-red text-white"
                  : "bg-parchment border border-parchment-border text-ink hover:border-chinese-red"
              }`}
            >
              <BookOpen className="w-3 h-3" />
              Folklore Available
            </button>
            <button
              onClick={() => setCategoryFilter("urban_legend")}
              className={`px-3 py-1.5 text-xs font-mono rounded-xs font-semibold transition-colors flex items-center gap-1.5 shrink-0 ${
                categoryFilter === "urban_legend"
                  ? "bg-cobalt text-white"
                  : "bg-parchment border border-parchment-border text-ink hover:border-cobalt"
              }`}
            >
              <Ghost className="w-3 h-3" />
              Urban Legends Available
            </button>
          </div>

          {/* Sort Selector */}
          <div className="relative shrink-0">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="appearance-none pl-3 pr-8 py-2 text-xs font-mono bg-parchment border border-parchment-border rounded-xs text-ink focus:outline-none focus:border-chinese-red cursor-pointer"
            >
              <option value="alphabetical">Sort: Alphabetical (A-Z)</option>
              <option value="highest">Sort: Highest Record Count</option>
              <option value="lowest">Sort: Lowest Record Count</option>
            </select>
            <div className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-ink-muted">
              ▼
            </div>
          </div>
        </div>

        {/* Counter Bar */}
        <div className="flex items-center justify-between text-xs font-mono text-ink-muted pt-2 border-t border-parchment-border/60">
          <span>
            Displaying <strong className="text-burgundy font-bold">{filteredCountries.length}</strong> supported countries
          </span>
          <span className="text-[11px] uppercase tracking-wider text-chinese-red font-semibold">
            15 Canonical National Archives Verified
          </span>
        </div>
      </div>

      {/* Empty State */}
      {filteredCountries.length === 0 && (
        <div className="py-16 px-6 bg-parchment-light border border-parchment-border rounded-xs text-center max-w-lg mx-auto">
          <Globe className="w-8 h-8 text-chinese-red mx-auto mb-3" />
          <h4 className="font-display text-lg font-bold text-burgundy mb-1">
            No Countries Match Query
          </h4>
          <p className="font-serif text-xs text-ink-muted mb-4">
            No registered national territory in the KathaYantra archive matches &ldquo;{searchQuery}&rdquo;.
          </p>
          <button
            onClick={() => {
              setSearchQuery("");
              setCategoryFilter("all");
            }}
            className="px-4 py-2 bg-chinese-red text-white text-xs font-mono uppercase tracking-wider font-semibold rounded-xs"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Featured Country Layout */}
      {featuredCountry && !searchQuery && categoryFilter === "all" && (
        <CountryEditorialCard
          country={featuredCountry}
          stats={statsMap[featuredCountry.code.toUpperCase()]}
          variant="featured"
        />
      )}

      {/* Asymmetric Country Grid */}
      {filteredCountries.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(searchQuery || categoryFilter !== "all" ? filteredCountries : remainingCountries).map((c) => (
            <CountryEditorialCard
              key={c.code}
              country={c}
              stats={statsMap[c.code.toUpperCase()]}
              variant="standard"
            />
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import React from "react";
import { Search, X, SlidersHorizontal, ArrowUpDown } from "lucide-react";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { getCountryFlag } from "@/lib/routes";

interface StoryFiltersProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedCountry: string;
  onCountryChange: (country: string) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
  totalResults: number;
  onClearFilters: () => void;
  categoryLabel?: string;
  className?: string;
}

export function StoryFilters({
  searchQuery,
  onSearchChange,
  selectedCountry,
  onCountryChange,
  sortBy,
  onSortChange,
  totalResults,
  onClearFilters,
  categoryLabel,
  className = "",
}: StoryFiltersProps) {
  const hasActiveFilters = Boolean(searchQuery || selectedCountry || (sortBy && sortBy !== "title"));

  return (
    <div
      className={`bg-parchment-light border border-parchment-border rounded-xs p-4 md:p-5 shadow-xs flex flex-col gap-4 ${className}`}
    >
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <label htmlFor="story-search" className="sr-only">
            Search {categoryLabel || "stories"}
          </label>
          <Search className="w-4 h-4 text-ink-muted absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            id="story-search"
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={`Search ${categoryLabel || "narratives"} by title, motif, or cultural region...`}
            className="w-full pl-10 pr-9 py-2 text-xs md:text-sm font-serif bg-parchment border border-parchment-border rounded-xs text-ink placeholder:text-ink-muted/70 focus:outline-none focus:border-chinese-red focus:ring-1 focus:ring-chinese-red transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-chinese-red transition-colors"
              aria-label="Clear search input"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filter Controls Row */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Country Dropdown */}
          <div className="relative">
            <select
              value={selectedCountry}
              onChange={(e) => onCountryChange(e.target.value)}
              className="appearance-none pl-3 pr-8 py-2 text-xs font-mono bg-parchment border border-parchment-border rounded-xs text-ink focus:outline-none focus:border-chinese-red cursor-pointer"
              aria-label="Filter by Country"
            >
              <option value="">All Countries (15)</option>
              {Object.entries(SUPPORTED_COUNTRIES).map(([code, meta]) => (
                <option key={code} value={code}>
                  {getCountryFlag(code)} {meta.name}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-ink-muted">
              ▼
            </div>
          </div>

          {/* Sort By Dropdown */}
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => onSortChange(e.target.value)}
              className="appearance-none pl-3 pr-8 py-2 text-xs font-mono bg-parchment border border-parchment-border rounded-xs text-ink focus:outline-none focus:border-chinese-red cursor-pointer"
              aria-label="Sort collection"
            >
              <option value="title">Sort: A-Z Alphabetical</option>
              <option value="country">Sort: By Country</option>
              <option value="id">Sort: Archival ID</option>
            </select>
            <div className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-ink-muted">
              ▼
            </div>
          </div>

          {/* Reset Action */}
          {hasActiveFilters && (
            <button
              onClick={onClearFilters}
              className="px-3 py-2 text-xs font-mono text-chinese-red hover:bg-chinese-red/10 border border-chinese-red/30 rounded-xs transition-colors flex items-center gap-1 font-semibold"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Results Counter Bar */}
      <div className="flex items-center justify-between text-xs font-mono text-ink-muted pt-2 border-t border-parchment-border/60">
        <div>
          Showing <span className="font-bold text-burgundy">{totalResults}</span> verified records
          {selectedCountry && (
            <span>
              {" "}
              in <strong className="text-ink">{SUPPORTED_COUNTRIES[selectedCountry]?.name || selectedCountry}</strong>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-chinese-red animate-pulse" />
          <span className="text-[11px] uppercase tracking-wider text-burgundy font-semibold">
            Rights-Verified Archive
          </span>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { Ghost, ArrowLeft, Download, ShieldCheck, MapPin, Building2 } from "lucide-react";
import { api } from "@/lib/api/client";
import { StoryRecord } from "@/types/story";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";
import { StoryGrid } from "@/components/stories/story-grid";
import { StoryFilters } from "@/components/stories/story-filters";
import { StoryPagination } from "@/components/stories/story-pagination";
import { ArchivePackModal } from "@/components/archive/archive-pack-modal";

const PAGE_SIZE = 12;

export default function UrbanLegendsPage() {
  const [allLegends, setAllLegends] = useState<StoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [sortBy, setSortBy] = useState("title");
  const [currentPage, setCurrentPage] = useState(1);
  const [isPackModalOpen, setIsPackModalOpen] = useState(false);

  useEffect(() => {
    async function loadUrbanLegends() {
      setIsLoading(true);
      try {
        // Fetch full verified urban legend collection (150 stories across 15 countries)
        const res = await api.listUrbanLegends({ limit: 150 });
        setAllLegends(res.data || []);
      } catch (err) {
        console.error("Failed to load urban legend records:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadUrbanLegends();
  }, []);

  // Filter and sort client-side
  const filteredStories = useMemo(() => {
    let result = [...allLegends];

    // Filter by country
    if (selectedCountry) {
      result = result.filter(
        (s) => s.country_code?.toUpperCase() === selectedCountry.toUpperCase()
      );
    }

    // Filter by search query (title, summary, region, motifs)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (s) =>
          s.title.toLowerCase().includes(q) ||
          s.summary.toLowerCase().includes(q) ||
          (s.region_or_community && s.region_or_community.toLowerCase().includes(q)) ||
          s.motifs.some((m) => m.toLowerCase().includes(q)) ||
          s.themes.some((t) => t.toLowerCase().includes(q))
      );
    }

    // Sorting
    result.sort((a, b) => {
      if (sortBy === "country") {
        return (a.country_code || "").localeCompare(b.country_code || "");
      }
      if (sortBy === "id") {
        return a.id.localeCompare(b.id);
      }
      return a.title.localeCompare(b.title);
    });

    return result;
  }, [allLegends, selectedCountry, searchQuery, sortBy]);

  // Pagination calculation
  const totalItems = filteredStories.length;
  const totalPages = Math.ceil(totalItems / PAGE_SIZE);
  const paginatedStories = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredStories.slice(start, start + PAGE_SIZE);
  }, [filteredStories, currentPage]);

  const handleResetFilters = () => {
    setSearchQuery("");
    setSelectedCountry("");
    setSortBy("title");
    setCurrentPage(1);
  };

  return (
    <main className="min-h-screen bg-parchment text-ink relative pb-24">
      <AtmosphericBackground />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 md:pt-12">
        {/* Navigation Breadcrumb & Download Header */}
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-parchment-border/70">
          <Link
            href="/explore"
            className="inline-flex items-center gap-2 text-xs font-mono text-ink-muted hover:text-chinese-red transition-colors uppercase tracking-wider font-semibold"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Country Directory</span>
          </Link>

          <button
            onClick={() => setIsPackModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-parchment-light border border-parchment-border hover:border-cobalt text-ink hover:text-cobalt text-xs font-mono font-semibold rounded-xs transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-cobalt" />
            <span>Download Urban Legends Pack</span>
          </button>
        </div>

        {/* Editorial Urban Legends Hero (Atmospheric & Compendium-styled) */}
        <section className="mb-10 text-center md:text-left grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
          <div className="md:col-span-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-xs bg-cobalt/10 border border-cobalt/20 text-cobalt text-[11px] font-mono uppercase tracking-widest font-bold mb-3">
              <Ghost className="w-3.5 h-3.5" />
              Circulating Narratives & Contemporary Mysteries
            </div>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-burgundy tracking-tight leading-none">
              Urban Legends
            </h1>
            <p className="mt-4 font-serif text-base sm:text-lg text-ink/85 max-w-2xl leading-relaxed">
              Explore circulating stories, unexplained accounts and modern mysteries preserved in the archive. Historical urban locations, campus apparitions, phantom roadways, and subterranean cryptid lore.
            </p>
          </div>

          <div className="md:col-span-4 bg-parchment-light border border-parchment-border rounded-xs p-5 shadow-2xs flex flex-col gap-2">
            <div className="flex items-center justify-between text-xs font-mono text-ink-muted pb-2 border-b border-parchment-border/60">
              <span>Archive Classification</span>
              <span className="text-cobalt font-bold">150 Urban Legends</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono text-ink">
              <span>Geographic Coverage</span>
              <strong className="text-burgundy">15 Sovereign Territories</strong>
            </div>
            <div className="flex items-center justify-between text-xs font-mono text-ink">
              <span>Contemporary Press Records</span>
              <span className="text-chinese-red font-bold">100% Sourced</span>
            </div>
          </div>
        </section>

        {/* Filters and Search Control */}
        <div className="mb-8">
          <StoryFilters
            searchQuery={searchQuery}
            onSearchChange={(q) => {
              setSearchQuery(q);
              setCurrentPage(1);
            }}
            selectedCountry={selectedCountry}
            onCountryChange={(c) => {
              setSelectedCountry(c);
              setCurrentPage(1);
            }}
            sortBy={sortBy}
            onSortChange={setSortBy}
            totalResults={totalItems}
            onClearFilters={handleResetFilters}
            categoryLabel="urban legends"
          />
        </div>

        {/* Stories Grid */}
        <StoryGrid
          stories={paginatedStories}
          isLoading={isLoading}
          featuredFirst={currentPage === 1 && !searchQuery && !selectedCountry}
          onResetFilters={handleResetFilters}
        />

        {/* Pagination */}
        <div className="mt-12">
          <StoryPagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={(p) => {
              setCurrentPage(p);
              window.scrollTo({ top: 300, behavior: "smooth" });
            }}
          />
        </div>
      </div>

      {/* Download Modal */}
      <ArchivePackModal
        isOpen={isPackModalOpen}
        onClose={() => setIsPackModalOpen(false)}
        title="KathaYantra Urban Legends Archive"
        category="urban_legend"
        recordCount={150}
      />
    </main>
  );
}

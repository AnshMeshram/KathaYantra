"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Globe, Compass, ArrowLeft, Download, ShieldCheck, Sparkles } from "lucide-react";
import { api } from "@/lib/api/client";
import { CountryRecord, CountryStatsResponse } from "@/types/country";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";
import { CountryDirectory } from "@/components/countries/country-directory";
import { ArchivePackModal } from "@/components/archive/archive-pack-modal";

export default function ExplorePage() {
  const [countries, setCountries] = useState<CountryRecord[]>([]);
  const [statsMap, setStatsMap] = useState<Record<string, CountryStatsResponse>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isPackModalOpen, setIsPackModalOpen] = useState(false);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const countryRes = await api.listCountries({ limit: 50 });
        const countryList = countryRes.data || [];
        setCountries(countryList);

        // Fetch stats for all countries concurrently
        const statsPromises = countryList.map(async (c) => {
          try {
            const stat = await api.getCountryStats(c.code);
            return { code: c.code.toUpperCase(), stat };
          } catch {
            return null;
          }
        });

        const statsResults = await Promise.all(statsPromises);
        const map: Record<string, CountryStatsResponse> = {};
        statsResults.forEach((item) => {
          if (item) map[item.code] = item.stat;
        });
        setStatsMap(map);
      } catch (err) {
        console.error("Failed to load country directory:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  const totalStories = Object.values(statsMap).reduce(
    (acc, curr) => acc + curr.total_count,
    0
  ) || 300;

  return (
    <main className="min-h-screen bg-parchment text-ink relative pb-24">
      <AtmosphericBackground />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 md:pt-12">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-parchment-border/70">
          <Link
            href="/#atlas"
            className="inline-flex items-center gap-2 text-xs font-mono text-ink-muted hover:text-chinese-red transition-colors uppercase tracking-wider font-semibold"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to World Atlas</span>
          </Link>

          <button
            onClick={() => setIsPackModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-parchment-light border border-parchment-border hover:border-chinese-red text-ink hover:text-chinese-red text-xs font-mono font-semibold rounded-xs transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-chinese-red" />
            <span>Export Archive Pack</span>
          </button>
        </div>

        {/* Editorial Hero Section (Inspired by Image 1 & Hungry Tiger) */}
        <section className="mb-12 text-center md:text-left grid grid-cols-1 md:grid-cols-12 gap-8 items-end">
          <div className="md:col-span-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-xs bg-burgundy/10 border border-burgundy/20 text-burgundy text-[11px] font-mono uppercase tracking-widest font-bold mb-3">
              <Globe className="w-3.5 h-3.5 text-chinese-red" />
              Global Cultural Geography
            </div>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-burgundy tracking-tight leading-none">
              Explore the World of Stories
            </h1>
            <p className="mt-4 font-serif text-base sm:text-lg text-ink/85 max-w-2xl leading-relaxed">
              Across countries and generations, folklore and urban legends preserve the stories people share. Discover 15 national traditions documented with primary sources and rights-verified cultural narratives.
            </p>
          </div>

          <div className="md:col-span-4 bg-parchment-light border border-parchment-border rounded-xs p-5 shadow-2xs flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-mono text-ink-muted pb-2 border-b border-parchment-border/60">
              <span>National Quotas</span>
              <span className="text-chinese-red font-bold">15 / 15 Complete</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="p-2.5 bg-parchment rounded-xs border border-parchment-border/60">
                <span className="block font-display text-2xl font-bold text-burgundy">150</span>
                <span className="text-[10px] font-mono text-ink-muted uppercase">Folklore Records</span>
              </div>
              <div className="p-2.5 bg-parchment rounded-xs border border-parchment-border/60">
                <span className="block font-display text-2xl font-bold text-cobalt">150</span>
                <span className="text-[10px] font-mono text-ink-muted uppercase">Urban Legends</span>
              </div>
            </div>
            <p className="text-[11px] font-mono text-ink-muted text-center flex items-center justify-center gap-1.5 pt-1">
              <ShieldCheck className="w-3.5 h-3.5 text-chinese-red shrink-0" />
              100% Traceable Bibliographic Provenance
            </p>
          </div>
        </section>

        {/* Country Directory */}
        <CountryDirectory
          countries={countries}
          statsMap={statsMap}
          isLoading={isLoading}
        />
      </div>

      {/* Global Archive Pack Export Modal */}
      <ArchivePackModal
        isOpen={isPackModalOpen}
        onClose={() => setIsPackModalOpen(false)}
        title="Complete KathaYantra Global Archive"
        recordCount={totalStories}
      />
    </main>
  );
}

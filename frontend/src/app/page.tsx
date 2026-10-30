"use client";

import { useState } from "react";
import Link from "next/link";
import { Compass, BookOpen, Skull, Sparkles, MapPin, ArrowRight, ShieldCheck, Globe } from "lucide-react";
import { MapContainer } from "@/components/map/map-container";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { useCountries } from "@/lib/queries/use-countries";

export default function HomePage() {
  const [selectedCountryCode, setSelectedCountryCode] = useState<string | null>(null);
  const { data: countriesData, isError } = useCountries();
  const supportedList = Object.values(SUPPORTED_COUNTRIES);

  return (
    <div className="relative min-h-[calc(100vh-60px)] flex flex-col justify-between">
      <AtmosphericBackground />

      {/* Main Content Area */}
      <div className="relative z-10 max-w-[1720px] mx-auto w-full px-3 sm:px-6 lg:px-8 py-3 space-y-4">
        {/* Compact Editorial Header Bar (Restrained so Map Dominates 80%) */}
        <section className="flex flex-col md:flex-row items-start md:items-end justify-between gap-3 border-b border-charcoal-wine/60 pb-3">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-plum/90 border border-gold/40 text-[10px] font-mono text-gold tracking-widest uppercase shadow-gold-glow">
              <Sparkles className="w-3 h-3 text-gold" />
              <span>Gothic Archival Cartography</span>
            </div>
            <h1 className="font-gothic text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-gold-gradient">
              Stories Never Die.
            </h1>
            <p className="font-serif text-xs sm:text-sm text-ash max-w-2xl leading-relaxed italic">
              Explore the folklore, myths, and urban legends that shape cultures across the world through verified historical cartography.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center gap-3 font-mono text-xs text-ash">
            <div className="px-3 py-1.5 rounded bg-plum border border-charcoal-wine flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-gold shadow-[0_0_6px_#C78B42]" />
              <span>15 Sovereign Nations</span>
            </div>
            <div className="hidden sm:flex px-3 py-1.5 rounded bg-plum border border-charcoal-wine items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blood shadow-[0_0_6px_#E52D35]" />
              <span>300 Verified Records</span>
            </div>
            <div className="hidden lg:flex px-3 py-1.5 rounded bg-plum border border-charcoal-wine items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>0% AI Hallucination</span>
            </div>
          </div>
        </section>

        {/* MAP-FIRST HERO: Occupies 75-85% of Viewport */}
        <section id="atlas-section" className="relative w-full">
          <MapContainer
            selectedCountry={selectedCountryCode}
            onSelectCountry={(code) => setSelectedCountryCode(code)}
          />
        </section>

        {/* Accessible Country Selection Strip & Footer Metrics */}
        <section id="countries-section" className="pt-2 pb-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-mono text-xs uppercase tracking-wider text-gold flex items-center gap-2">
              <Globe className="w-3.5 h-3.5 text-gold" />
              <span>Accessible National Archive Directory (Select a Sovereign Nation)</span>
            </h2>
            <span className="font-serif text-xs text-ash/80 italic hidden sm:inline">
              Click any territory to center camera and inspect regional tales
            </span>
          </div>

          {/* 15 Country Quick Selector Pills */}
          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-8 lg:grid-cols-15 gap-2">
            {supportedList.map((country) => {
              const isSelected = selectedCountryCode?.toUpperCase() === country.code;
              return (
                <button
                  key={country.code}
                  type="button"
                  onClick={() => setSelectedCountryCode(country.code)}
                  className={`p-2 rounded border text-left transition-all ${
                    isSelected
                      ? "bg-plum border-ember shadow-gold-glow scale-[1.02]"
                      : "bg-plum/60 border-charcoal-wine hover:border-gold/50 hover:bg-plum"
                  }`}
                  aria-label={`Select ${country.name} folklore archive`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] font-bold text-gold">
                      {country.code}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-blood shadow-[0_0_4px_#E52D35]" />
                  </div>
                  <div className="font-gothic text-xs text-ivory font-bold truncate mt-1">
                    {country.name}
                  </div>
                  <div className="font-mono text-[9px] text-ash/70 truncate">
                    20 Records
                  </div>
                </button>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { Compass, BookOpen, Skull, Shield, Sparkles, MapPin, ArrowRight } from "lucide-react";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { CountryTooltip } from "@/components/map/country-tooltip";

// Sample other world nations for demonstrating the unsupported hover state
const UNSUPPORTED_SAMPLE_COUNTRIES = [
  { code: "CA", name: "Canada", region: "North America" },
  { code: "AU", name: "Australia", region: "Oceania" },
  { code: "FR", name: "France", region: "Western Europe" },
  { code: "IT", name: "Italy", region: "Southern Europe" },
  { code: "RU", name: "Russia", region: "Eurasia" },
  { code: "ZA", name: "South Africa", region: "Southern Africa" },
  { code: "AR", name: "Argentina", region: "South America" },
  { code: "NO", name: "Norway", region: "Northern Europe" },
];

export default function HomePage() {
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null);
  const supportedList = Object.values(SUPPORTED_COUNTRIES);

  return (
    <div className="relative min-h-screen px-4 lg:px-8 py-12 max-w-7xl mx-auto space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-8 pb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-plum border border-gold/40 text-xs font-mono text-gold tracking-widest uppercase shadow-gold-glow">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Gothic Archival Cartography</span>
        </div>

        <h1 className="font-gothic text-5xl md:text-7xl font-bold tracking-tight text-gold-gradient max-w-4xl mx-auto leading-tight">
          A Haunted Atlas of World Folklore
        </h1>

        <p className="font-serif text-lg md:text-xl text-ash max-w-2xl mx-auto leading-relaxed italic">
          Step into a digital museum of spectral myths, sacred demons, and modern urban legends—preserved from 15 sovereign nations with zero synthetic AI hallucination.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4 font-gothic text-lg">
          <Link
            href="/atlas"
            className="flex items-center gap-2 px-6 py-3 rounded bg-gold hover:bg-gold-hover text-obsidian font-bold transition-all shadow-gold-glow"
          >
            <Compass className="w-5 h-5" />
            <span>Enter the Atlas</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            href="/folklore"
            className="flex items-center gap-2 px-6 py-3 rounded bg-plum hover:bg-plum-hover border border-charcoal-wine text-ivory transition-colors"
          >
            <BookOpen className="w-5 h-5 text-gold" />
            <span>Explore 150 Folk Tales</span>
          </Link>

          <Link
            href="/urban-legends"
            className="flex items-center gap-2 px-6 py-3 rounded bg-plum hover:bg-plum-hover border border-blood/40 text-ivory transition-colors"
          >
            <Skull className="w-5 h-5 text-blood" />
            <span>150 Urban Legends</span>
          </Link>
        </div>

        {/* Archival Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8 max-w-4xl mx-auto text-left">
          <div className="p-4 rounded bg-plum border border-charcoal-wine">
            <div className="font-mono text-2xl font-bold text-gold">15</div>
            <div className="font-serif text-xs text-ash">Sovereign Nations</div>
          </div>
          <div className="p-4 rounded bg-plum border border-charcoal-wine">
            <div className="font-mono text-2xl font-bold text-ivory">300</div>
            <div className="font-serif text-xs text-ash">Documented Legends</div>
          </div>
          <div className="p-4 rounded bg-plum border border-charcoal-wine">
            <div className="font-mono text-2xl font-bold text-ember">3,000</div>
            <div className="font-serif text-xs text-ash">Museum & Archival Images</div>
          </div>
          <div className="p-4 rounded bg-plum border border-charcoal-wine">
            <div className="font-mono text-2xl font-bold text-emerald-400">0%</div>
            <div className="font-serif text-xs text-ash">AI-Generated Art (Pure Authenticity)</div>
          </div>
        </div>
      </section>

      {/* Interactive Country Exploration Section (Demonstrates Supported vs Unsupported States) */}
      <section className="space-y-8">
        <div className="border-b border-charcoal-wine pb-4 flex flex-col sm:flex-row sm:items-end justify-between gap-2">
          <div>
            <h2 className="font-gothic text-3xl font-bold text-ivory">
              Archival Nations & Global Coverage
            </h2>
            <p className="font-serif text-sm text-ash italic">
              Hover over any country to inspect archival readiness or planned territorial coverage.
            </p>
          </div>
          <div className="font-mono text-xs text-gold flex items-center gap-2">
            <MapPin className="w-4 h-4 text-gold" />
            <span>Interactive Country Cards</span>
          </div>
        </div>

        {/* Supported Countries Grid */}
        <div>
          <h3 className="font-mono text-xs uppercase tracking-wider text-gold mb-4">
            Active Archival Nations (15 Supported — 20 Verified Stories Each)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {supportedList.map((country) => (
              <div
                key={country.code}
                onMouseEnter={() => setHoveredCountry(country.code)}
                className="group relative p-3 rounded bg-plum/70 hover:bg-plum border border-charcoal-wine hover:border-gold/50 cursor-pointer transition-all"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-gothic text-lg font-bold text-ivory group-hover:text-gold transition-colors">
                    {country.name}
                  </span>
                  <span className="font-mono text-xs text-ash/80 px-1 rounded bg-obsidian border border-charcoal-wine">
                    {country.code}
                  </span>
                </div>
                <div className="font-serif text-[11px] text-ash truncate">
                  {country.region}
                </div>
                <div className="font-mono text-[10px] text-gold/80 mt-2 flex items-center justify-between">
                  <span>10 Folk</span>
                  <span>10 Urban</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Unsupported Countries Preview Section */}
        <div>
          <h3 className="font-mono text-xs uppercase tracking-wider text-ash/70 mb-4">
            Expanding Frontiers (Hover to view &quot;Stories Coming Soon&quot; notification)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {UNSUPPORTED_SAMPLE_COUNTRIES.map((country) => (
              <div
                key={country.code}
                onMouseEnter={() => setHoveredCountry(country.code)}
                className="group p-3 rounded bg-obsidian/60 hover:bg-plum/40 border border-charcoal-wine/60 hover:border-ash/40 cursor-help transition-all"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-gothic text-base text-ash group-hover:text-ivory/80 transition-colors">
                    {country.name}
                  </span>
                  <span className="font-mono text-[10px] text-ash/60 px-1 rounded bg-obsidian">
                    {country.code}
                  </span>
                </div>
                <div className="font-serif text-[10px] text-ash/60">
                  {country.region}
                </div>
                <div className="font-mono text-[10px] text-amber-500/70 mt-2">
                  Coming Soon
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Hover Tooltip Display Preview */}
        {hoveredCountry && (
          <div className="p-4 rounded bg-obsidian border border-gold/30 shadow-gold-glow flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="font-mono text-xs text-gold uppercase tracking-wider mb-1">
                Active Map Hover State Inspector
              </div>
              <div className="font-serif text-xs text-ash">
                Demonstrating dynamic cartographic tooltip response for code: <strong className="text-ivory font-mono">{hoveredCountry}</strong>
              </div>
            </div>
            <CountryTooltip countryCode={hoveredCountry} />
          </div>
        )}
      </section>

      {/* Archival Integrity Pillar */}
      <section className="p-6 md:p-8 rounded bg-plum/60 border border-gold/30 shadow-gold-glow space-y-4">
        <div className="flex items-center gap-3 text-gold">
          <Shield className="w-6 h-6 text-gold" />
          <h3 className="font-gothic text-2xl font-bold uppercase tracking-wider">
            Archival Sourcing Safeguards
          </h3>
        </div>
        <p className="font-serif text-sm text-ash leading-relaxed max-w-3xl">
          Every narrative in KathaYantra is linked to verifiable bibliographic citations from institutions such as the Archaeological Survey of India, Tokyo National Museum, National Library of Brazil, Library of Congress, and Europeana. Synthetic AI content is strictly quarantined to fiction generation and cannot enter our historical archive.
        </p>
      </section>
    </div>
  );
}

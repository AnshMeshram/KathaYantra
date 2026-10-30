"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Compass,
  BookOpen,
  Ghost,
  MapPin,
  ArrowRight,
  Globe,
  Scroll,
} from "lucide-react";
import { MapContainer } from "@/components/map/map-container";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { useCountries } from "@/lib/queries/use-countries";

export default function HomePage() {
  const [selectedCountryCode, setSelectedCountryCode] = useState<string | null>(null);
  const { data: countriesData } = useCountries();
  const supportedList = Object.values(SUPPORTED_COUNTRIES);

  return (
    <div className="relative min-h-screen flex flex-col justify-between">
      <AtmosphericBackground />

      {/* SECTION B: BRAND INTRODUCTION (Asymmetric 2-Column Editorial Layout) */}
      <section className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 sm:pt-20 sm:pb-24 border-b border-parchment-border/70">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Left Column: Typographic Narrative */}
          <div className="lg:col-span-7 space-y-6 text-left">
            {/* Hanko Archival Seal */}
            <div className="inline-flex items-center gap-2">
              <span className="hanko-seal">民話・怪異</span>
              <span className="font-mono text-[11px] tracking-widest text-ink-muted uppercase">
                KathaYantra Cultural Archive
              </span>
            </div>

            {/* Main Title & Supporting Line */}
            <div className="space-y-2">
              <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-burgundy leading-[1.08]">
                Stories Never Die.
              </h1>
              <p className="font-display text-xl sm:text-2xl text-chinese-red italic tracking-wide">
                An Atlas of Folklore, Myths and Urban Legends.
              </p>
            </div>

            {/* Short Readable Description */}
            <p className="font-serif text-sm sm:text-base text-ink-muted leading-relaxed max-w-xl">
              Explore the stories, traditions and mysteries preserved across different cultures.
              From ancient ancestral spirits to modern urban hauntings, documented across 15 sovereign nations.
            </p>

            {/* Authentic Historical Timeline Bar (Inspired by Japanese Museum Reference) */}
            <div className="pt-2 pb-2 space-y-2 max-w-lg">
              <div className="h-1.5 w-full bg-parchment-deep rounded-full overflow-hidden flex">
                <div className="w-1/4 bg-burgundy/80" />
                <div className="w-1/4 bg-satsuma/80" />
                <div className="w-1/4 bg-lunar-yellow" />
                <div className="w-1/4 bg-cobalt/80" />
              </div>
              <div className="flex justify-between text-[10px] font-mono text-ink-faint">
                <span>Antiquity</span>
                <span>Oral Era</span>
                <span>1765 Woodblock</span>
                <span>20th Century</span>
                <span>Contemporary</span>
              </div>
            </div>

            {/* Primary & Secondary Call to Action Buttons */}
            <div className="pt-2 flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <a
                href="#atlas"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-sm bg-chinese-red hover:bg-chinese-red-dark text-parchment-light font-display text-sm font-bold tracking-wider transition-colors shadow-seal uppercase"
              >
                <span>Explore the World Atlas</span>
                <ArrowRight className="w-4 h-4" />
              </a>
              <a
                href="#archive-collections"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-sm bg-parchment-light hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-burgundy font-display text-sm font-semibold tracking-wider transition-colors uppercase"
              >
                <span>Discover the Archive</span>
              </a>
            </div>
          </div>

          {/* Right Column: Genuine Museum Visual Presentation */}
          <div className="lg:col-span-5 flex flex-col items-center">
            <div className="relative w-full max-w-md p-3 bg-parchment-light border border-parchment-border shadow-panel rounded-sm">
              <div className="relative w-full aspect-[4/5] overflow-hidden rounded-sm bg-parchment-deep">
                <Image
                  src="/images/editorial-woodblock.jpg"
                  alt="Traditional Japanese woodblock print artwork"
                  fill
                  sizes="(max-width: 768px) 100vw, 420px"
                  priority
                  className="object-cover object-center"
                />
              </div>
              <div className="pt-3 px-1 flex items-start justify-between gap-3 text-left">
                <p className="font-serif text-[11px] text-ink-muted italic leading-snug">
                  Nishiki-e polychrome woodblock print tradition (c. 1765) depicting the cultural interplay of landscape, mythology, and folklore.
                </p>
                <span className="font-mono text-[9px] px-1.5 py-0.5 rounded-sm bg-parchment-deep border border-parchment-border text-burgundy shrink-0">
                  Ukiyo-e
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION C & D: FULL-SCREEN INTERACTIVE WORLD ATLAS */}
      <section id="atlas" className="relative z-10 w-full max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 space-y-5">
        {/* SECTION C: MAP INTRODUCTION */}
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-3 border-b border-parchment-border pb-3">
          <div className="space-y-1">
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-burgundy flex items-center gap-2.5">
              <Globe className="w-5 h-5 text-chinese-red" />
              <span>Explore the World Atlas</span>
            </h2>
            <p className="font-serif text-xs sm:text-sm text-ink-muted italic">
              Select any illuminated sovereign territory to inspect verified local folklore traditions and urban hauntings.
            </p>
          </div>
          <div className="font-mono text-xs text-ink-faint">
            Natural Earth 1:110m Sovereign Boundaries
          </div>
        </div>

        {/* SECTION D: FULL-SCREEN WORLD MAP */}
        <div className="relative w-full">
          <MapContainer
            selectedCountry={selectedCountryCode}
            onSelectCountry={(code) => setSelectedCountryCode(code)}
          />
        </div>

        {/* Accessible Country Quick-Selection Ribbon (Zero Horizontal Overflow) */}
        <div id="countries-index" className="pt-2 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-mono text-xs uppercase tracking-widest text-burgundy font-semibold flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-chinese-red" />
              <span>Sovereign Nations Index (Select to Navigate)</span>
            </h3>
            <span className="font-serif text-xs text-ink-faint italic hidden sm:inline">
              Quota: 10 Folklore + 10 Urban Legends per country
            </span>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-8 lg:grid-cols-15 gap-2">
            {supportedList.map((country) => {
              const isSelected = selectedCountryCode?.toUpperCase() === country.code;
              return (
                <button
                  key={country.code}
                  type="button"
                  onClick={() => setSelectedCountryCode(country.code)}
                  className={`p-2 rounded-sm border text-left transition-all ${
                    isSelected
                      ? "bg-lunar-yellow/40 border-chinese-red shadow-editorial scale-[1.02]"
                      : "bg-parchment-light border-parchment-border hover:border-burgundy"
                  }`}
                  aria-label={`Select ${country.name} folklore archive`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] font-bold text-burgundy">
                      {country.code}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-chinese-red" />
                  </div>
                  <div className="font-display text-xs text-ink font-semibold truncate mt-1">
                    {country.name}
                  </div>
                  <div className="font-mono text-[9px] text-ink-faint truncate">
                    20 Stories
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* SECTION E: ARCHIVAL COLLECTIONS INTRODUCTION */}
      <section id="archive-collections" className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-parchment-border space-y-12">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="hanko-seal">COLLECTIONS</span>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-burgundy">
            Two Dualities of Cultural Lore
          </h2>
          <p className="font-serif text-sm text-ink-muted leading-relaxed">
            The KathaYantra archive balances ancestral oral traditions with contemporary societal accounts.
          </p>
        </div>

        {/* Dual Collection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* COLLECTION ONE: FOLKLORE */}
          <div id="folklore-collection" className="editorial-card p-6 sm:p-8 rounded-sm space-y-5">
            <div className="flex items-center justify-between border-b border-parchment-border pb-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-sm bg-parchment-deep border border-burgundy/30 flex items-center justify-center text-burgundy">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-chinese-red font-semibold">
                    Collection One
                  </span>
                  <h3 className="font-display text-2xl font-bold text-burgundy">
                    Traditional Folklore
                  </h3>
                </div>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded-sm bg-parchment-deep border border-parchment-border text-burgundy font-bold">
                150 Records
              </span>
            </div>

            <p className="font-serif text-sm text-ink-muted leading-relaxed">
              Narratives handed down through generations, chronicling mythological encounters, moral fables,
              shapeshifting entities, and supernatural protectors rooted in regional cultural heritage.
            </p>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedCountryCode("JP");
                  const elem = document.getElementById("atlas");
                  if (elem) elem.scrollIntoView({ behavior: "smooth" });
                }}
                className="w-full py-2.5 px-4 rounded-sm bg-parchment-deep hover:bg-parchment border border-parchment-border hover:border-burgundy text-burgundy font-display text-sm font-bold tracking-wider transition-colors flex items-center justify-center gap-2 uppercase"
              >
                <span>View Folklore on Atlas</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* COLLECTION TWO: URBAN LEGENDS */}
          <div id="urban-legends-collection" className="editorial-card p-6 sm:p-8 rounded-sm space-y-5">
            <div className="flex items-center justify-between border-b border-parchment-border pb-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-sm bg-parchment-deep border border-cobalt/30 flex items-center justify-center text-cobalt">
                  <Ghost className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-cobalt font-semibold">
                    Collection Two
                  </span>
                  <h3 className="font-display text-2xl font-bold text-burgundy">
                    Urban Legends
                  </h3>
                </div>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded-sm bg-parchment-deep border border-parchment-border text-cobalt font-bold">
                150 Records
              </span>
            </div>

            <p className="font-serif text-sm text-ink-muted leading-relaxed">
              Modern folklore circulating in contemporary cities and communities, reflecting modern anxieties:
              haunted infrastructure, mysterious apparitions, and documented regional cryptids.
            </p>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedCountryCode("US");
                  const elem = document.getElementById("atlas");
                  if (elem) elem.scrollIntoView({ behavior: "smooth" });
                }}
                className="w-full py-2.5 px-4 rounded-sm bg-parchment-deep hover:bg-parchment border border-parchment-border hover:border-cobalt text-cobalt font-display text-sm font-bold tracking-wider transition-colors flex items-center justify-center gap-2 uppercase"
              >
                <span>View Urban Legends on Atlas</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION F: ARCHIVE PROVENANCE & METHODOLOGY */}
      <section id="about-project" className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 border-t border-parchment-border space-y-6">
        <div className="max-w-2xl space-y-2">
          <span className="hanko-seal">PROVENANCE</span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-burgundy">
            Institutional Heritage & Editorial Standards
          </h2>
          <p className="font-serif text-xs sm:text-sm text-ink-muted leading-relaxed">
            Every entry in KathaYantra is catalogued from authoritative institutional archives, academic collections,
            and verified historical documentation. AI tools serve solely as retrieval archivist assistants and are strictly
            bound to ground truth, never permitted to hallucinate folklore or invent historical origins.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 font-serif text-xs">
          <div className="p-4 rounded-sm bg-parchment-light border border-parchment-border space-y-1.5">
            <h4 className="font-display text-sm font-bold text-burgundy">
              1. Institutional Heritage
            </h4>
            <p className="text-ink-muted leading-relaxed">
              Primary texts and historical artwork verified through Wikimedia Commons, the Met Museum, and Library of Congress.
            </p>
          </div>

          <div className="p-4 rounded-sm bg-parchment-light border border-parchment-border space-y-1.5">
            <h4 className="font-display text-sm font-bold text-burgundy">
              2. Sovereign Quotas
            </h4>
            <p className="text-ink-muted leading-relaxed">
              Exact balance: 10 traditional folklore narratives and 10 urban legends per country across all 15 catalogued sovereign nations.
            </p>
          </div>

          <div className="p-4 rounded-sm bg-parchment-light border border-parchment-border space-y-1.5">
            <h4 className="font-display text-sm font-bold text-burgundy">
              3. Zero Synthetic Artwork
            </h4>
            <p className="text-ink-muted leading-relaxed">
              All visual assets are authentic historical artifacts and museum open-access items with zero AI diffusion generation.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

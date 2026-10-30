"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Compass,
  BookOpen,
  Ghost,
  MapPin,
  ArrowRight,
  ShieldCheck,
  Globe,
  Scroll,
  Layers,
  ChevronDown,
} from "lucide-react";
import { MapContainer } from "@/components/map/map-container";
import { AtmosphericBackground } from "@/components/effects/atmospheric-background";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { useCountries } from "@/lib/queries/use-countries";

export default function HomePage() {
  const [selectedCountryCode, setSelectedCountryCode] = useState<string | null>(
    null,
  );
  const { data: countriesData } = useCountries();
  const supportedList = Object.values(SUPPORTED_COUNTRIES);

  return (
    <div className="relative min-h-screen flex flex-col justify-between">
      <AtmosphericBackground />

      {/* 1. BRAND HERO SECTION */}
      <section className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 sm:pt-24 sm:pb-28 border-b border-stone/50">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          {/* Archival Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-parchment border border-stone text-xs font-mono text-brass tracking-widest uppercase">
            <Compass className="w-3.5 h-3.5 text-brass" />
            <span>Digital Folklore Museum & Supernatural Atlas</span>
          </div>

          {/* Brand Wordmark & Dominant Display Headline */}
          <div className="space-y-3">
            <h1 className="font-display text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-linen leading-[1.08]">
              Stories Never Die.
            </h1>
            <p className="font-display text-xl sm:text-2xl text-brass italic tracking-wide">
              An Atlas of Folklore, Myths and Urban Legends.
            </p>
          </div>

          {/* Restrained Editorial Subtitle */}
          <p className="font-serif text-sm sm:text-base text-linen-muted max-w-2xl mx-auto leading-relaxed">
            Across borders, generations and forgotten places, stories remain.
            Explore 300 authenticated traditional narratives, mythic spirits,
            and contemporary urban mysteries catalogued across 15 sovereign
            nations.
          </p>

          {/* Primary & Secondary Call to Action Buttons */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#atlas"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-sm bg-brass hover:bg-brass-light text-ink font-display text-sm font-bold tracking-wider transition-colors shadow-editorial uppercase"
            >
              <span>Explore the Atlas</span>
              <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="#archive-collections"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-sm bg-parchment hover:bg-parchment-elevated border border-stone hover:border-brass/40 text-linen font-display text-sm font-semibold tracking-wider transition-colors uppercase"
            >
              <span>Discover the Archive</span>
            </a>
          </div>

          {/* Archival Quotas Summary Bar */}
          <div className="pt-10 flex flex-wrap items-center justify-center gap-6 sm:gap-10 font-mono text-xs text-linen-muted border-t border-stone/40 max-w-2xl mx-auto">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-brass" />
              <span>15 Sovereign Nations</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cinnabar" />
              <span>300 Documented Records</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. FULL-SCREEN INTERACTIVE ATLAS SECTION */}
      <section
        id="atlas"
        className="relative z-10 w-full max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 space-y-4"
      >
        {/* Section Intro */}
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-3 border-b border-stone/50 pb-3">
          <div className="space-y-1">
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-linen flex items-center gap-2.5">
              <Globe className="w-5 h-5 text-brass" />
              <span>The Cartographic Archive</span>
            </h2>
            <p className="font-serif text-xs sm:text-sm text-linen-muted italic">
              Select any illuminated territory to reveal its regional folklore
              traditions, creature accounts, and urban hauntings.
            </p>
          </div>
          <div className="font-mono text-xs text-linen-faint">
            Natural Earth 1:110m Sovereign Boundaries
          </div>
        </div>

        {/* 80-90vh Leaflet Map Viewport */}
        <div className="relative w-full">
          <MapContainer
            selectedCountry={selectedCountryCode}
            onSelectCountry={(code) => setSelectedCountryCode(code)}
          />
        </div>

        {/* Accessible Country Quick Selector Ribbon */}
        <div id="countries-index" className="pt-2 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-mono text-xs uppercase tracking-widest text-brass flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-brass" />
              <span>Sovereign Nations Index (Select to Navigate)</span>
            </h3>
            <span className="font-serif text-xs text-linen-faint italic hidden sm:inline">
              Exact quota: 10 Folklore + 10 Urban Legends per country
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 md:grid-cols-8 lg:grid-cols-15 gap-2">
            {supportedList.map((country) => {
              const isSelected =
                selectedCountryCode?.toUpperCase() === country.code;
              return (
                <button
                  key={country.code}
                  type="button"
                  onClick={() => setSelectedCountryCode(country.code)}
                  className={`p-2 rounded-sm border text-left transition-all ${
                    isSelected
                      ? "bg-parchment-elevated border-brass shadow-editorial scale-[1.02]"
                      : "bg-parchment border-stone hover:border-brass/40"
                  }`}
                  aria-label={`Select ${country.name} folklore archive`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] font-bold text-brass">
                      {country.code}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-cinnabar" />
                  </div>
                  <div className="font-display text-xs text-linen font-semibold truncate mt-1">
                    {country.name}
                  </div>
                  <div className="font-mono text-[9px] text-linen-faint truncate">
                    20 Stories
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* 3. ARCHIVAL COLLECTIONS STORYTELLING SECTION */}
      <section
        id="archive-collections"
        className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-stone/50 space-y-16"
      >
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="font-mono text-xs uppercase tracking-widest text-brass">
            Curated Heritage
          </span>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-linen">
            Two Dualities of Human Mystery
          </h2>
          <p className="font-serif text-sm text-linen-muted leading-relaxed">
            The KathaYantra archive balances ancestral oral traditions with
            contemporary societal fears, documenting how folklore shifts from
            sacred myth to modern urban legend.
          </p>
        </div>

        {/* DUAL COLLECTION EDITORIAL CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* COLLECTION ONE: FOLKLORE */}
          <div
            id="folklore-collection"
            className="editorial-card p-6 sm:p-8 rounded-sm space-y-6"
          >
            <div className="flex items-center justify-between border-b border-stone/60 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-sm bg-parchment-elevated border border-brass/30 flex items-center justify-center text-brass">
                  <BookOpen className="w-5 h-5" />
                </div>
                <div>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-brass">
                    Collection One
                  </span>
                  <h3 className="font-display text-2xl font-bold text-linen">
                    Traditional Folklore
                  </h3>
                </div>
              </div>
              <span className="font-mono text-sm px-2.5 py-1 rounded-sm bg-ink border border-stone text-brass font-bold">
                150 Records
              </span>
            </div>

            <p className="font-serif text-sm text-linen-muted leading-relaxed">
              Narratives handed down through generations, chronicling
              mythological encounters, moral cautions, shapeshifting entities,
              and supernatural protectors deeply woven into indigenous and
              national traditions.
            </p>

            <div className="space-y-3 font-serif text-xs text-linen-muted border-t border-stone/40 pt-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">
                  Documented Motifs:
                </span>
                <span className="font-mono text-[11px] text-linen-faint">
                  Ancestral Spirits, Demons, Shapeshifters
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">Temporal Origin:</span>
                <span className="font-mono text-[11px] text-linen-faint">
                  Ancient Antiquity – 19th Century
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">
                  Catalogued Provenance:
                </span>
                <span className="font-mono text-[11px] text-brass">
                  Wikimedia Commons & Met Museum
                </span>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedCountryCode("JP");
                  const elem = document.getElementById("atlas");
                  if (elem) elem.scrollIntoView({ behavior: "smooth" });
                }}
                className="w-full py-2.5 px-4 rounded-sm bg-parchment hover:bg-parchment-elevated border border-stone hover:border-brass/40 text-brass font-display text-sm font-semibold tracking-wider transition-colors flex items-center justify-center gap-2 uppercase"
              >
                <span>Browse Folklore on Atlas</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* COLLECTION TWO: URBAN LEGENDS */}
          <div
            id="urban-legends-collection"
            className="editorial-card p-6 sm:p-8 rounded-sm space-y-6"
          >
            <div className="flex items-center justify-between border-b border-stone/60 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-sm bg-parchment-elevated border border-cinnabar/30 flex items-center justify-center text-cinnabar">
                  <Ghost className="w-5 h-5" />
                </div>
                <div>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-cinnabar">
                    Collection Two
                  </span>
                  <h3 className="font-display text-2xl font-bold text-linen">
                    Urban Legends
                  </h3>
                </div>
              </div>
              <span className="font-mono text-sm px-2.5 py-1 rounded-sm bg-ink border border-stone text-cinnabar font-bold">
                150 Records
              </span>
            </div>

            <p className="font-serif text-sm text-linen-muted leading-relaxed">
              Modern folklore circulating in contemporary cities and towns.
              These stories reflect modern anxieties: haunted highways, phantom
              phone calls, mysterious abandoned structures, and cryptid
              sightings.
            </p>

            <div className="space-y-3 font-serif text-xs text-linen-muted border-t border-stone/40 pt-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">
                  Documented Motifs:
                </span>
                <span className="font-mono text-[11px] text-linen-faint">
                  Phantom Travelers, Cryptids, Cursed Sites
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">Temporal Origin:</span>
                <span className="font-mono text-[11px] text-linen-faint">
                  Early 20th Century – Contemporary
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-linen">
                  Catalogued Provenance:
                </span>
                <span className="font-mono text-[11px] text-cinnabar">
                  Library of Congress & Regional Press
                </span>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedCountryCode("US");
                  const elem = document.getElementById("atlas");
                  if (elem) elem.scrollIntoView({ behavior: "smooth" });
                }}
                className="w-full py-2.5 px-4 rounded-sm bg-parchment hover:bg-parchment-elevated border border-stone hover:border-cinnabar/40 text-cinnabar font-display text-sm font-semibold tracking-wider transition-colors flex items-center justify-center gap-2 uppercase"
              >
                <span>Browse Urban Legends on Atlas</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 4. METHODOLOGY & PROVENANCE OVERVIEW */}
      <section
        id="about-project"
        className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-stone/50 space-y-8"
      >
        <div className="max-w-3xl space-y-3">
          <span className="font-mono text-xs uppercase tracking-widest text-brass">
            Archival Principles
          </span>
          <h2 className="font-display text-3xl font-bold text-linen">
            Rigorous Provenance, Zero Fabrication
          </h2>
          <p className="font-serif text-sm text-linen-muted leading-relaxed">
            Every entry in KathaYantra is catalogued from authoritative
            institutional archives, academic collections, and verified
            historical documentation. AI tools serve solely as retrieval
            archivist assistants and are strictly bound to ground truth, never
            permitted to hallucinate folklore or invent historical origins.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4 font-serif text-xs">
          <div className="p-4 rounded-sm bg-parchment border border-stone space-y-2">
            <h4 className="font-display text-base font-semibold text-brass">
              1. Institutional Heritage
            </h4>
            <p className="text-linen-muted leading-relaxed">
              Historical imagery and primary texts verified via Wikimedia
              Commons, the Metropolitan Museum of Art, and the Library of
              Congress.
            </p>
          </div>

          <div className="p-4 rounded-sm bg-parchment border border-stone space-y-2">
            <h4 className="font-display text-base font-semibold text-brass">
              2. Sovereign Quotas
            </h4>
            <p className="text-linen-muted leading-relaxed">
              Strict balance: exactly 10 traditional folklore narratives and 10
              urban legends per country across all 15 catalogued sovereign
              nations.
            </p>
          </div>

          <div className="p-4 rounded-sm bg-parchment border border-stone space-y-2">
            <h4 className="font-display text-base font-semibold text-brass">
              3. Transparent Licensing
            </h4>
            <p className="text-linen-muted leading-relaxed">
              Every asset carries explicit public domain or Creative Commons
              licensing attribution with zero synthetic diffusion artwork.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

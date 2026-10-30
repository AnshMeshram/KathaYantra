"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  BookOpen,
  Skull,
  Sparkles,
  ChevronDown,
  Menu,
  X,
  Globe2,
  MapPin,
  ShieldCheck,
  Cpu,
  Database,
} from "lucide-react";
import { SearchControl } from "@/components/ui/search-control";

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [exploreOpen, setExploreOpen] = useState(false);
  const [storiesOpen, setStoriesOpen] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-obsidian/95 backdrop-blur-md border-b border-charcoal-wine/80 px-4 lg:px-8 py-2.5 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Left: Brand Logo */}
        <Link href="/" className="group flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-full bg-plum border border-gold/40 flex items-center justify-center shadow-gold-glow group-hover:border-gold transition-colors">
            <Compass className="w-4 h-4 text-gold group-hover:rotate-45 transition-transform duration-500" />
          </div>
          <div className="flex flex-col">
            <span className="font-gothic text-xl font-bold tracking-widest text-gold-gradient group-hover:text-gold transition-colors uppercase">
              KathaYantra
            </span>
            <span className="font-mono text-[9px] tracking-wider text-ash -mt-1 uppercase">
              The Haunted Atlas
            </span>
          </div>
        </Link>

        {/* Center: Exactly 5 Main Navigation Items */}
        <nav className="hidden md:flex items-center gap-1 lg:gap-2 font-gothic text-base">
          {/* 1. HOME */}
          <Link
            href="/"
            className={`px-3 py-1.5 rounded transition-colors ${
              pathname === "/"
                ? "text-gold font-bold bg-plum/60 border border-gold/30"
                : "text-ivory/80 hover:text-gold hover:bg-plum/30"
            }`}
          >
            HOME
          </Link>

          {/* 2. EXPLORE (Dropdown) */}
          <div
            className="relative"
            onMouseEnter={() => setExploreOpen(true)}
            onMouseLeave={() => setExploreOpen(false)}
          >
            <button
              type="button"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-colors ${
                exploreOpen ? "text-gold bg-plum/60" : "text-ivory/80 hover:text-gold hover:bg-plum/30"
              }`}
            >
              <span>EXPLORE</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {exploreOpen && (
              <div className="absolute top-full left-0 w-60 py-2 bg-plum border border-charcoal-wine rounded-md shadow-gothic-card animate-fadeIn z-50">
                <Link
                  href="/#atlas-section"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <Globe2 className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">Interactive World Map</div>
                    <div className="text-[10px] text-ash">75% hero cartography</div>
                  </div>
                </Link>
                <Link
                  href="/#countries-section"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <MapPin className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">All 15 Countries</div>
                    <div className="text-[10px] text-ash">Active national archives</div>
                  </div>
                </Link>
                <Link
                  href="/#regional-section"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <Compass className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">Regional Exploration</div>
                    <div className="text-[10px] text-ash">Asia, Americas, Europe, Africa</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 3. STORIES (Dropdown) */}
          <div
            className="relative"
            onMouseEnter={() => setStoriesOpen(true)}
            onMouseLeave={() => setStoriesOpen(false)}
          >
            <button
              type="button"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-colors ${
                storiesOpen ? "text-gold bg-plum/60" : "text-ivory/80 hover:text-gold hover:bg-plum/30"
              }`}
            >
              <span>STORIES</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {storiesOpen && (
              <div className="absolute top-full left-0 w-60 py-2 bg-plum border border-charcoal-wine rounded-md shadow-gothic-card animate-fadeIn z-50">
                <Link
                  href="/folklore"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <BookOpen className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">Folklore & Myths</div>
                    <div className="text-[10px] text-ash">150 traditional narratives</div>
                  </div>
                </Link>
                <Link
                  href="/urban-legends"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-blood hover:bg-charcoal-wine/50 transition-colors"
                >
                  <Skull className="w-4 h-4 text-blood/80" />
                  <div>
                    <div className="font-semibold">Urban Legends</div>
                    <div className="text-[10px] text-ash">150 modern hauntings</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 4. ARCHIVIST */}
          <Link
            href="/archivist"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-colors ${
              pathname === "/archivist"
                ? "text-spectral font-bold bg-plum/60 border border-spectral/30"
                : "text-ivory/80 hover:text-spectral hover:bg-plum/30"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-spectral/70" />
            <span>ARCHIVIST</span>
          </Link>

          {/* 5. ABOUT (Dropdown) */}
          <div
            className="relative"
            onMouseEnter={() => setAboutOpen(true)}
            onMouseLeave={() => setAboutOpen(false)}
          >
            <button
              type="button"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-colors ${
                aboutOpen ? "text-gold bg-plum/60" : "text-ivory/80 hover:text-gold hover:bg-plum/30"
              }`}
            >
              <span>ABOUT</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {aboutOpen && (
              <div className="absolute top-full right-0 w-64 py-2 bg-plum border border-charcoal-wine rounded-md shadow-gothic-card animate-fadeIn z-50">
                <Link
                  href="/about"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <ShieldCheck className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">About KathaYantra</div>
                    <div className="text-[10px] text-ash">Cultural heritage & anti-hallucination</div>
                  </div>
                </Link>
                <Link
                  href="/about#archive"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <Database className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">Data Governance</div>
                    <div className="text-[10px] text-ash">300 stories · 3,000 museum assets</div>
                  </div>
                </Link>
                <Link
                  href="/about#technology"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2 text-xs font-serif text-ivory/90 hover:text-gold hover:bg-charcoal-wine/50 transition-colors"
                >
                  <Cpu className="w-4 h-4 text-gold/80" />
                  <div>
                    <div className="font-semibold">Architecture & Technology</div>
                    <div className="text-[10px] text-ash">FastAPI · Next.js · Gemma 2 RAG</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* Right: Search Control & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <SearchControl />

          {/* Mobile hamburger button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded bg-plum border border-charcoal-wine text-ash hover:text-gold transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-3 pt-3 border-t border-charcoal-wine font-gothic text-lg space-y-2 animate-fadeIn">
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 text-ivory hover:text-gold"
          >
            1. HOME
          </Link>
          <div className="px-3 py-1">
            <span className="text-gold font-bold text-sm">2. EXPLORE</span>
            <div className="pl-4 mt-1 space-y-1 text-sm font-serif text-ash">
              <Link href="/#atlas-section" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • Interactive World Map
              </Link>
              <Link href="/#countries-section" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • All 15 Countries
              </Link>
            </div>
          </div>
          <div className="px-3 py-1">
            <span className="text-gold font-bold text-sm">3. STORIES</span>
            <div className="pl-4 mt-1 space-y-1 text-sm font-serif text-ash">
              <Link href="/folklore" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • Folklore & Myths (150)
              </Link>
              <Link href="/urban-legends" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • Urban Legends (150)
              </Link>
            </div>
          </div>
          <Link
            href="/archivist"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 text-spectral"
          >
            4. ARCHIVIST (AI RAG)
          </Link>
          <div className="px-3 py-1">
            <span className="text-gold font-bold text-sm">5. ABOUT</span>
            <div className="pl-4 mt-1 space-y-1 text-sm font-serif text-ash">
              <Link href="/about" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • About KathaYantra
              </Link>
              <Link href="/about#archive" onClick={() => setMobileMenuOpen(false)} className="block hover:text-ivory">
                • Archival Governance
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

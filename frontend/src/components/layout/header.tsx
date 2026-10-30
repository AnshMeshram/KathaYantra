"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  ChevronDown,
  Menu,
  X,
  Globe,
  MapPin,
  Layers,
  Scroll,
  BookOpen,
  Ghost,
  Library,
  FileCode,
} from "lucide-react";
import { SearchControl } from "@/components/ui/search-control";

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [exploreOpen, setExploreOpen] = useState(false);
  const [storiesOpen, setStoriesOpen] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  const exploreRef = useRef<HTMLDivElement>(null);
  const storiesRef = useRef<HTMLDivElement>(null);
  const aboutRef = useRef<HTMLDivElement>(null);

  // Scroll detection for clean sticky transition
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close dropdowns on outside click or escape key
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (exploreRef.current && !exploreRef.current.contains(e.target as Node)) {
        setExploreOpen(false);
      }
      if (storiesRef.current && !storiesRef.current.contains(e.target as Node)) {
        setStoriesOpen(false);
      }
      if (aboutRef.current && !aboutRef.current.contains(e.target as Node)) {
        setAboutOpen(false);
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setExploreOpen(false);
        setStoriesOpen(false);
        setAboutOpen(false);
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setExploreOpen(false);
    setStoriesOpen(false);
    setAboutOpen(false);
  }, [pathname]);

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        isScrolled
          ? "bg-parchment/95 backdrop-blur-md border-b border-parchment-border shadow-sm py-2.5"
          : "bg-parchment/85 backdrop-blur-sm border-b border-parchment-border/70 py-3.5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-6">
        {/* Left: Brand Identity & Wordmark */}
        <Link
          href="/"
          className="group flex items-center gap-3 shrink-0 focus:outline-none focus-visible:ring-1 focus-visible:ring-burgundy"
          aria-label="KathaYantra Home"
        >
          {/* Hanko-inspired Archival Seal */}
          <div className="w-8 h-8 rounded-sm bg-burgundy text-parchment-light flex items-center justify-center font-display font-bold text-sm tracking-wider shadow-seal group-hover:bg-chinese-red transition-colors">
            KY
          </div>
          <div className="flex flex-col">
            <span className="font-display text-xl font-bold tracking-[0.16em] text-burgundy group-hover:text-chinese-red transition-colors uppercase">
              KathaYantra
            </span>
            <span className="font-mono text-[9px] tracking-widest text-ink-muted -mt-0.5 uppercase">
              The Haunted Atlas
            </span>
          </div>
        </Link>

        {/* Center: Exactly Five Primary Navigation Items */}
        <nav
          className="hidden md:flex items-center gap-1 lg:gap-2 text-sm font-display tracking-wider"
          aria-label="Primary Navigation"
        >
          {/* 1. HOME */}
          <Link
            href="/"
            className={`px-3 py-1.5 rounded-sm transition-colors uppercase ${
              pathname === "/"
                ? "text-chinese-red font-bold border-b-2 border-chinese-red"
                : "text-ink/80 hover:text-burgundy hover:bg-parchment-deep/40"
            }`}
          >
            Home
          </Link>

          {/* 2. EXPLORE (Dropdown) */}
          <div
            ref={exploreRef}
            className="relative"
            onMouseEnter={() => setExploreOpen(true)}
            onMouseLeave={() => setExploreOpen(false)}
          >
            <button
              type="button"
              onClick={() => setExploreOpen((prev) => !prev)}
              aria-expanded={exploreOpen}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-sm transition-colors uppercase ${
                exploreOpen || pathname.startsWith("/explore")
                  ? "text-chinese-red font-bold"
                  : "text-ink/80 hover:text-burgundy hover:bg-parchment-deep/40"
              }`}
            >
              <span>Explore</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  exploreOpen ? "rotate-180 text-chinese-red" : ""
                }`}
              />
            </button>

            {exploreOpen && (
              <div className="absolute top-full left-0 w-64 py-2 mt-1 bg-parchment-light border border-parchment-border rounded-sm shadow-panel z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-faint border-b border-parchment-border/60 mb-1">
                  Cartographic Navigation
                </div>
                <Link
                  href="/explore"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <MapPin className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Country Directory</div>
                    <div className="text-[10px] text-ink-muted">15 sovereign archives</div>
                  </div>
                </Link>
                <Link
                  href="/#atlas"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <Globe className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">World Atlas</div>
                    <div className="text-[10px] text-ink-muted">Interactive global map</div>
                  </div>
                </Link>
                <Link
                  href="/#archive-collections"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <Layers className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Regional Archive</div>
                    <div className="text-[10px] text-ink-muted">Geographical distribution</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 3. STORIES (Dropdown) */}
          <div
            ref={storiesRef}
            className="relative"
            onMouseEnter={() => setStoriesOpen(true)}
            onMouseLeave={() => setStoriesOpen(false)}
          >
            <button
              type="button"
              onClick={() => setStoriesOpen((prev) => !prev)}
              aria-expanded={storiesOpen}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-sm transition-colors uppercase ${
                storiesOpen || pathname.startsWith("/stories")
                  ? "text-chinese-red font-bold"
                  : "text-ink/80 hover:text-burgundy hover:bg-parchment-deep/40"
              }`}
            >
              <span>Stories</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  storiesOpen ? "rotate-180 text-chinese-red" : ""
                }`}
              />
            </button>

            {storiesOpen && (
              <div className="absolute top-full left-0 w-64 py-2 mt-1 bg-parchment-light border border-parchment-border rounded-sm shadow-panel z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-faint border-b border-parchment-border/60 mb-1">
                  Archival Records
                </div>
                <Link
                  href="/folklore"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <BookOpen className="w-4 h-4 text-chinese-red shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Folklore</div>
                    <div className="text-[10px] text-ink-muted">150 traditional narratives</div>
                  </div>
                </Link>
                <Link
                  href="/urban-legends"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-cobalt hover:bg-parchment transition-colors"
                >
                  <Ghost className="w-4 h-4 text-cobalt shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Urban Legends</div>
                    <div className="text-[10px] text-ink-muted">150 modern eerie accounts</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 4. ARCHIVIST (Direct Link) */}
          <Link
            href="/archivist"
            className={`px-3 py-1.5 rounded-sm transition-colors uppercase ${
              pathname === "/archivist"
                ? "text-chinese-red font-bold border-b-2 border-chinese-red"
                : "text-ink/80 hover:text-burgundy hover:bg-parchment-deep/40"
            }`}
          >
            Archivist
          </Link>

          {/* 5. ABOUT (Dropdown) */}
          <div
            ref={aboutRef}
            className="relative"
            onMouseEnter={() => setAboutOpen(true)}
            onMouseLeave={() => setAboutOpen(false)}
          >
            <button
              type="button"
              onClick={() => setAboutOpen((prev) => !prev)}
              aria-expanded={aboutOpen}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-sm transition-colors uppercase ${
                aboutOpen || pathname.startsWith("/about")
                  ? "text-chinese-red font-bold"
                  : "text-ink/80 hover:text-burgundy hover:bg-parchment-deep/40"
              }`}
            >
              <span>About</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  aboutOpen ? "rotate-180 text-chinese-red" : ""
                }`}
              />
            </button>

            {aboutOpen && (
              <div className="absolute top-full right-0 w-64 py-2 mt-1 bg-parchment-light border border-parchment-border rounded-sm shadow-panel z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-faint border-b border-parchment-border/60 mb-1">
                  Project Governance
                </div>
                <Link
                  href="/#about-project"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <Library className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">About KathaYantra</div>
                    <div className="text-[10px] text-ink-muted">The Haunted Atlas mission</div>
                  </div>
                </Link>
                <Link
                  href="/#archive-provenance"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <Scroll className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Archive Provenance</div>
                    <div className="text-[10px] text-ink-muted">Institutional collections</div>
                  </div>
                </Link>
                <Link
                  href="/#technology-stack"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-ink hover:text-chinese-red hover:bg-parchment transition-colors"
                >
                  <FileCode className="w-4 h-4 text-burgundy shrink-0" />
                  <div>
                    <div className="font-display font-semibold text-sm">Technology</div>
                    <div className="text-[10px] text-ink-muted">FastAPI, Next.js & Leaflet</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* Right: Search Control & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <SearchControl />

          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2 rounded-sm text-ink-muted hover:text-burgundy hover:bg-parchment-deep border border-parchment-border"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Accordion Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-x-0 top-full bg-parchment-light border-b border-parchment-border shadow-panel z-40 p-5 space-y-3 animate-fadeIn max-h-[85vh] overflow-y-auto">
          {/* 1. HOME */}
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-display font-bold text-burgundy border-b border-parchment-border/50 uppercase"
          >
            Home
          </Link>

          {/* 2. EXPLORE */}
          <div className="border-b border-parchment-border/50 pb-2">
            <button
              type="button"
              onClick={() => setExploreOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-bold text-ink hover:text-chinese-red uppercase"
            >
              <span>Explore</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${exploreOpen ? "rotate-180 text-chinese-red" : ""}`}
              />
            </button>
            {exploreOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/#atlas"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  World Atlas (Interactive Map)
                </Link>
                <Link
                  href="/explore"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  Country Directory (15 Sovereign Archives)
                </Link>
                <Link
                  href="/#atlas"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  World Atlas (Interactive Map)
                </Link>
              </div>
            )}
          </div>

          {/* 3. STORIES */}
          <div className="border-b border-parchment-border/50 pb-2">
            <button
              type="button"
              onClick={() => setStoriesOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-bold text-ink hover:text-chinese-red uppercase"
            >
              <span>Stories</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${storiesOpen ? "rotate-180 text-chinese-red" : ""}`}
              />
            </button>
            {storiesOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/folklore"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  Folklore (150 Records)
                </Link>
                <Link
                  href="/urban-legends"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-cobalt py-1"
                >
                  Urban Legends (150 Records)
                </Link>
              </div>
            )}
          </div>

          {/* 4. ARCHIVIST */}
          <Link
            href="/archivist"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-display font-bold text-ink hover:text-chinese-red border-b border-parchment-border/50 uppercase"
          >
            Archivist
          </Link>

          {/* 5. ABOUT */}
          <div className="border-b border-parchment-border/50 pb-2">
            <button
              type="button"
              onClick={() => setAboutOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-bold text-ink hover:text-chinese-red uppercase"
            >
              <span>About</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${aboutOpen ? "rotate-180 text-chinese-red" : ""}`}
              />
            </button>
            {aboutOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/#about-project"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  About KathaYantra
                </Link>
                <Link
                  href="/#archive-provenance"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  Archive Provenance
                </Link>
                <Link
                  href="/#technology-stack"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-ink-muted hover:text-chinese-red py-1"
                >
                  Technology
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

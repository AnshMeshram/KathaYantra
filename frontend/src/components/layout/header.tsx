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
  ShieldCheck,
  Search,
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

  // Scroll detection for sticky header refinement
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close dropdowns on outside click or escape
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

  // Close mobile drawer on route change
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
          ? "bg-ink/95 backdrop-blur-md border-b border-stone shadow-editorial py-2.5"
          : "bg-ink/80 backdrop-blur-sm border-b border-stone/50 py-3"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-6">
        {/* Left: Brand Identity / Wordmark */}
        <Link
          href="/"
          className="group flex items-center gap-3 shrink-0 focus:outline-none focus-visible:ring-1 focus-visible:ring-brass"
          aria-label="KathaYantra Home"
        >
          <div className="w-8 h-8 rounded-sm bg-parchment border border-brass/40 flex items-center justify-center transition-colors group-hover:border-brass">
            <Compass className="w-4 h-4 text-brass transition-transform duration-500 group-hover:rotate-45" />
          </div>
          <div className="flex flex-col">
            <span className="font-display text-xl font-bold tracking-[0.18em] text-linen group-hover:text-brass transition-colors uppercase">
              KathaYantra
            </span>
            <span className="font-mono text-[9px] tracking-widest text-linen-muted -mt-0.5 uppercase">
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
                ? "text-brass font-semibold border-b border-brass"
                : "text-linen-muted hover:text-linen hover:bg-parchment/60"
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
                  ? "text-brass font-semibold"
                  : "text-linen-muted hover:text-linen hover:bg-parchment/60"
              }`}
            >
              <span>Explore</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  exploreOpen ? "rotate-180 text-brass" : ""
                }`}
              />
            </button>

            {exploreOpen && (
              <div className="absolute top-full left-0 w-64 py-2 mt-1 bg-parchment-elevated border border-stone rounded-sm shadow-overlay z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-linen-faint border-b border-stone/50 mb-1">
                  Cartographic Exploration
                </div>
                <Link
                  href="/#atlas"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <Globe className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">World Atlas</div>
                    <div className="text-[10px] text-linen-muted">Interactive global map</div>
                  </div>
                </Link>
                <Link
                  href="/#countries-index"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <MapPin className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">All Countries</div>
                    <div className="text-[10px] text-linen-muted">15 verified national collections</div>
                  </div>
                </Link>
                <Link
                  href="/#archive-collections"
                  onClick={() => setExploreOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <Layers className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">Regional Archive</div>
                    <div className="text-[10px] text-linen-muted">Geographical distribution</div>
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
                  ? "text-brass font-semibold"
                  : "text-linen-muted hover:text-linen hover:bg-parchment/60"
              }`}
            >
              <span>Stories</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  storiesOpen ? "rotate-180 text-brass" : ""
                }`}
              />
            </button>

            {storiesOpen && (
              <div className="absolute top-full left-0 w-64 py-2 mt-1 bg-parchment-elevated border border-stone rounded-sm shadow-overlay z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-linen-faint border-b border-stone/50 mb-1">
                  Archival Collections
                </div>
                <Link
                  href="/#folklore-collection"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <BookOpen className="w-4 h-4 text-cinnabar/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">Folklore</div>
                    <div className="text-[10px] text-linen-muted">150 traditional & mythic tales</div>
                  </div>
                </Link>
                <Link
                  href="/#urban-legends-collection"
                  onClick={() => setStoriesOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <Ghost className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">Urban Legends</div>
                    <div className="text-[10px] text-linen-muted">150 modern eerie accounts</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 4. ARCHIVIST (Direct link) */}
          <Link
            href="/archivist"
            className={`px-3 py-1.5 rounded-sm transition-colors uppercase ${
              pathname === "/archivist"
                ? "text-brass font-semibold border-b border-brass"
                : "text-linen-muted hover:text-linen hover:bg-parchment/60"
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
                  ? "text-brass font-semibold"
                  : "text-linen-muted hover:text-linen hover:bg-parchment/60"
              }`}
            >
              <span>About</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  aboutOpen ? "rotate-180 text-brass" : ""
                }`}
              />
            </button>

            {aboutOpen && (
              <div className="absolute top-full right-0 w-64 py-2 mt-1 bg-parchment-elevated border border-stone rounded-sm shadow-overlay z-50 animate-fadeIn">
                <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-linen-faint border-b border-stone/50 mb-1">
                  Project Documentation
                </div>
                <Link
                  href="/#about-project"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <Library className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">About KathaYantra</div>
                    <div className="text-[10px] text-linen-muted">The Haunted Atlas mission</div>
                  </div>
                </Link>
                <Link
                  href="/#archive-provenance"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <Scroll className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">Archive Provenance</div>
                    <div className="text-[10px] text-linen-muted">Institutional collections</div>
                  </div>
                </Link>
                <Link
                  href="/#technology-stack"
                  onClick={() => setAboutOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 text-xs font-serif text-linen/90 hover:text-brass hover:bg-parchment-overlay transition-colors"
                >
                  <FileCode className="w-4 h-4 text-brass/80 shrink-0" />
                  <div>
                    <div className="font-display font-medium text-sm">Technology</div>
                    <div className="text-[10px] text-linen-muted">FastAPI, Next.js & Leaflet</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* Right: Expandable Search Control & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <SearchControl />

          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2 rounded-sm text-linen-muted hover:text-linen hover:bg-parchment border border-stone"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer (Accordion-driven) */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-x-0 top-full bg-ink border-b border-stone shadow-overlay z-40 p-5 space-y-4 animate-fadeIn max-h-[85vh] overflow-y-auto">
          {/* 1. HOME */}
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-display font-semibold text-linen hover:text-brass border-b border-stone/40"
          >
            HOME
          </Link>

          {/* 2. EXPLORE Accordion */}
          <div className="border-b border-stone/40 pb-2">
            <button
              type="button"
              onClick={() => setExploreOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-semibold text-linen hover:text-brass"
            >
              <span>EXPLORE</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${exploreOpen ? "rotate-180 text-brass" : ""}`}
              />
            </button>
            {exploreOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/#atlas"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  World Atlas (Interactive Map)
                </Link>
                <Link
                  href="/#countries-index"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  All 15 Countries
                </Link>
                <Link
                  href="/#archive-collections"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  Regional Archive Distribution
                </Link>
              </div>
            )}
          </div>

          {/* 3. STORIES Accordion */}
          <div className="border-b border-stone/40 pb-2">
            <button
              type="button"
              onClick={() => setStoriesOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-semibold text-linen hover:text-brass"
            >
              <span>STORIES</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${storiesOpen ? "rotate-180 text-brass" : ""}`}
              />
            </button>
            {storiesOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/#folklore-collection"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  Folklore (150 Records)
                </Link>
                <Link
                  href="/#urban-legends-collection"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
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
            className="block py-2 text-base font-display font-semibold text-linen hover:text-brass border-b border-stone/40"
          >
            ARCHIVIST
          </Link>

          {/* 5. ABOUT Accordion */}
          <div className="border-b border-stone/40 pb-2">
            <button
              type="button"
              onClick={() => setAboutOpen((prev) => !prev)}
              className="w-full flex items-center justify-between py-2 text-base font-display font-semibold text-linen hover:text-brass"
            >
              <span>ABOUT</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${aboutOpen ? "rotate-180 text-brass" : ""}`}
              />
            </button>
            {aboutOpen && (
              <div className="pl-4 space-y-2 py-2 text-sm font-serif">
                <Link
                  href="/#about-project"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  About KathaYantra
                </Link>
                <Link
                  href="/#archive-provenance"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  Archive Provenance & Rights
                </Link>
                <Link
                  href="/#technology-stack"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-linen-muted hover:text-brass py-1"
                >
                  Technology & Architecture
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

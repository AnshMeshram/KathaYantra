"use client";

import Link from "next/link";
import { Compass, BookOpen, Skull, Sparkles, Database } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full bg-obsidian/90 backdrop-blur-md border-b border-charcoal-wine/80 px-4 lg:px-8 py-3 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand / Logo */}
        <Link href="/" className="group flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-plum border border-gold/40 flex items-center justify-center shadow-gold-glow group-hover:border-gold transition-colors">
            <Compass className="w-5 h-5 text-gold group-hover:rotate-45 transition-transform duration-500" />
          </div>
          <div className="flex flex-col">
            <span className="font-gothic text-2xl font-bold tracking-widest text-gold-gradient group-hover:text-gold transition-colors uppercase">
              KathaYantra
            </span>
            <span className="font-mono text-[10px] tracking-wider text-ash -mt-1 uppercase">
              The Haunted Atlas
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 font-gothic text-lg">
          <Link
            href="/atlas"
            className="flex items-center gap-2 text-ivory/80 hover:text-gold transition-colors"
          >
            <Compass className="w-4 h-4 text-gold/70" />
            <span>The Atlas</span>
          </Link>

          <Link
            href="/folklore"
            className="flex items-center gap-2 text-ivory/80 hover:text-gold transition-colors"
          >
            <BookOpen className="w-4 h-4 text-gold/70" />
            <span>Folklore</span>
          </Link>

          <Link
            href="/urban-legends"
            className="flex items-center gap-2 text-ivory/80 hover:text-blood transition-colors"
          >
            <Skull className="w-4 h-4 text-blood/70" />
            <span>Urban Legends</span>
          </Link>

          <Link
            href="/archivist"
            className="flex items-center gap-2 text-ivory/80 hover:text-spectral transition-colors"
          >
            <Sparkles className="w-4 h-4 text-spectral/70" />
            <span>AI Archivist</span>
          </Link>

          <Link
            href="/archive"
            className="flex items-center gap-2 text-ivory/80 hover:text-gold transition-colors"
          >
            <Database className="w-4 h-4 text-gold/70" />
            <span>Archive</span>
          </Link>
        </nav>

        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-plum border border-charcoal-wine text-xs font-mono text-ash">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>15 Nations · 300 Records</span>
          </div>
        </div>
      </div>
    </header>
  );
}


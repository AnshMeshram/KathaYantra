"use client";

import {
  isCountrySupported,
  SUPPORTED_COUNTRIES,
  UNSUPPORTED_COUNTRY_NOTICE,
} from "@/constants/countries";
import { BookOpen, Skull, AlertCircle } from "lucide-react";

interface CountryTooltipProps {
  countryCode: string;
  countryName?: string;
  folkloreCount?: number;
  urbanLegendCount?: number;
}

export function CountryTooltip({
  countryCode,
  countryName,
  folkloreCount = 10,
  urbanLegendCount = 10,
}: CountryTooltipProps) {
  const code = countryCode.toUpperCase();
  const supported = isCountrySupported(code);
  const meta = supported ? SUPPORTED_COUNTRIES[code] : null;
  const displayName = countryName || meta?.name || code;

  if (!supported) {
    return (
      <div className="bg-plum/95 backdrop-blur-md border border-charcoal-wine p-3 rounded-md shadow-gothic-card max-w-xs text-left animate-fadeIn">
        <div className="flex items-center gap-2 mb-1.5">
          <AlertCircle className="w-4 h-4 text-ash" />
          <h4 className="font-gothic text-base font-bold text-ivory/80">
            {displayName}
          </h4>
        </div>
        <div className="inline-block px-2 py-0.5 rounded bg-charcoal-wine/60 text-[10px] font-mono text-gold mb-2 uppercase tracking-wider">
          {UNSUPPORTED_COUNTRY_NOTICE.badge}
        </div>
        <p className="font-serif text-xs text-ash leading-relaxed">
          {UNSUPPORTED_COUNTRY_NOTICE.message}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-plum/95 backdrop-blur-md border border-gold/40 p-4 rounded-md shadow-gold-glow max-w-xs text-left">
      <div className="flex items-center justify-between mb-1">
        <h4 className="font-gothic text-lg font-bold text-gold">
          {meta?.name || displayName}
        </h4>
        <span className="font-mono text-xs px-1.5 py-0.5 bg-obsidian border border-gold/30 rounded text-gold">
          {code}
        </span>
      </div>
      <p className="font-mono text-[10px] text-ash/80 mb-3 uppercase tracking-wider">
        {meta?.region}
      </p>

      {/* Story Counts */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-obsidian/70 border border-charcoal-wine p-2 rounded flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5 text-gold" />
          <div>
            <div className="font-mono text-xs font-bold text-ivory">
              {folkloreCount}
            </div>
            <div className="font-serif text-[10px] text-ash">
              Folklore Tales
            </div>
          </div>
        </div>

        <div className="bg-obsidian/70 border border-charcoal-wine p-2 rounded flex items-center gap-2">
          <Skull className="w-3.5 h-3.5 text-blood" />
          <div>
            <div className="font-mono text-xs font-bold text-ivory">
              {urbanLegendCount}
            </div>
            <div className="font-serif text-[10px] text-ash">Urban Legends</div>
          </div>
        </div>
      </div>

      {/* Featured Legend */}
      <div className="text-[11px] font-serif border-t border-charcoal-wine/80 pt-2 text-ivory/90">
        <span className="text-gold font-semibold">Key Tradition: </span>
        {meta?.primary_folklore_creature}
      </div>
    </div>
  );
}

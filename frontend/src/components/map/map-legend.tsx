"use client";

import { useState } from "react";
import { Info, ChevronUp, ChevronDown } from "lucide-react";

export function MapLegend() {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="absolute bottom-4 left-4 z-[400] bg-parchment/90 backdrop-blur-md border border-stone rounded-sm shadow-editorial p-3 max-w-xs transition-all">
      <div
        className="flex items-center justify-between gap-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-brass" />
          <span className="font-display text-xs font-semibold uppercase tracking-wider text-brass">
            Cartographic Legend
          </span>
        </div>
        <button
          type="button"
          className="text-linen-muted hover:text-linen"
          aria-label={isExpanded ? "Collapse legend" : "Expand legend"}
        >
          {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-2.5 pt-2 border-t border-stone/60 space-y-2 text-[11px] font-serif">
          {/* Active Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#171822] border border-[#D1A75C] shrink-0" />
            <span className="text-linen/90">
              <strong className="text-brass font-semibold">Antique Brass:</strong> 15 Supported Nations
            </span>
          </div>

          {/* Selected Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#222533] border border-[#E8C88B] shrink-0" />
            <span className="text-linen/90">
              <strong className="text-brass-light font-semibold">Gilded Accent:</strong> Selected Territory
            </span>
          </div>

          {/* Archive Presence Dot */}
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#BA382E] border border-linen/30 shrink-0" />
            <span className="text-linen/90">
              <strong className="text-cinnabar font-semibold">Cinnabar Seal:</strong> National Collection
            </span>
          </div>

          {/* Inactive Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#0D0E14] border border-[#262937] shrink-0" />
            <span className="text-linen-muted">
              <strong className="text-linen-faint font-medium">Weathered Stone:</strong> Stories Coming Soon
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

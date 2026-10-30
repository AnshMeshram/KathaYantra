"use client";

import { useState } from "react";
import { Info, ChevronUp, ChevronDown } from "lucide-react";

export function MapLegend() {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="absolute bottom-4 left-4 z-[400] bg-plum/90 backdrop-blur-md border border-charcoal-wine rounded-md shadow-gothic-card p-3 max-w-xs transition-all">
      <div
        className="flex items-center justify-between gap-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-gold" />
          <span className="font-gothic text-xs font-bold uppercase tracking-wider text-gold">
            Cartographic Legend
          </span>
        </div>
        <button
          type="button"
          className="text-ash hover:text-ivory"
          aria-label={isExpanded ? "Collapse legend" : "Expand legend"}
        >
          {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-2.5 pt-2 border-t border-charcoal-wine space-y-2 text-[11px] font-serif">
          {/* Active Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2.5 rounded-sm bg-[#251820] border border-[#C78B42] shadow-[0_0_8px_rgba(199,139,66,0.5)] shrink-0" />
            <span className="text-ivory/90">
              <strong className="text-gold font-semibold">Gold Border:</strong> 15 Archival Nations
            </span>
          </div>

          {/* Selected Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2.5 rounded-sm bg-[#251820] border border-[#FF713B] shadow-[0_0_8px_rgba(255,113,59,0.6)] shrink-0" />
            <span className="text-ivory/90">
              <strong className="text-ember font-semibold">Ember Glow:</strong> Selected Territory
            </span>
          </div>

          {/* Archive Presence Dot */}
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E52D35] border border-ivory/40 shadow-[0_0_6px_rgba(229,45,53,0.8)] shrink-0" />
            <span className="text-ivory/90">
              <strong className="text-blood font-semibold">Red Marker:</strong> Archive Presence
            </span>
          </div>

          {/* Inactive Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2.5 rounded-sm bg-[#1C1920] border border-[#37303A] shrink-0" />
            <span className="text-ash/70">
              <strong className="text-ash font-medium">Muted Grey:</strong> Stories Coming Soon
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

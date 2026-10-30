"use client";

import { useState } from "react";
import { Info, ChevronUp, ChevronDown } from "lucide-react";

export function MapLegend() {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="absolute bottom-4 left-4 z-[400] bg-parchment-light/95 backdrop-blur-md border border-parchment-border rounded-sm shadow-editorial p-3 max-w-xs transition-all">
      <div
        className="flex items-center justify-between gap-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-burgundy" />
          <span className="font-display text-xs font-bold uppercase tracking-wider text-burgundy">
            Atlas Legend
          </span>
        </div>
        <button
          type="button"
          className="text-ink-muted hover:text-burgundy"
          aria-label={isExpanded ? "Collapse legend" : "Expand legend"}
        >
          {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-2.5 pt-2 border-t border-parchment-border/70 space-y-2 text-[11px] font-serif">
          {/* Active Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#EDE2D0] border border-[#70191D] shrink-0" />
            <span className="text-ink">
              <strong className="text-burgundy font-semibold">Burgundy:</strong> 15 Supported Nations
            </span>
          </div>

          {/* Selected Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#FECD6D] border border-[#970A12] shrink-0" />
            <span className="text-ink">
              <strong className="text-chinese-red font-semibold">Lunar Yellow:</strong> Selected Territory
            </span>
          </div>

          {/* Archive Presence Dot */}
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#970A12] border border-[#FAF4EC] shrink-0" />
            <span className="text-ink">
              <strong className="text-chinese-red font-semibold">Chinese Red:</strong> National Archive
            </span>
          </div>

          {/* Inactive Country */}
          <div className="flex items-center gap-2.5">
            <span className="w-4 h-2 rounded-sm bg-[#FAF4EC] border border-[#D8C7B0] shrink-0" />
            <span className="text-ink-muted">
              <strong className="text-ink-faint font-medium">Parchment:</strong> Stories Coming Soon
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

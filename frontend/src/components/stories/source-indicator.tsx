"use client";

import React from "react";
import { ShieldCheck, BookOpen, ExternalLink } from "lucide-react";
import { StorySource } from "@/types/story";

interface SourceIndicatorProps {
  sources?: StorySource[];
  className?: string;
  compact?: boolean;
}

export function SourceIndicator({
  sources = [],
  className = "",
  compact = false,
}: SourceIndicatorProps) {
  if (!sources || sources.length === 0) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 text-[11px] font-mono text-ink-muted ${className}`}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-parchment-border" />
        <span>KathaYantra Curated Archive</span>
      </div>
    );
  }

  const primary = sources[0];
  const count = sources.length;
  const label =
    primary.publisher || primary.title || primary.name || "Historical Record";

  if (compact) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 text-[11px] font-mono text-ink-muted ${className}`}
        title={`Verified via ${label} (${count} documented citation${count > 1 ? "s" : ""})`}
      >
        <ShieldCheck className="w-3.5 h-3.5 text-chinese-red shrink-0" />
        <span className="truncate max-w-[180px]">{label}</span>
        {count > 1 && (
          <span className="text-[10px] px-1 py-0.2 bg-parchment-deep border border-parchment-border rounded-xs">
            +{count - 1}
          </span>
        )}
      </div>
    );
  }

  return (
    <div
      className={`p-3 bg-parchment/60 rounded-xs border border-parchment-border/80 flex flex-col gap-1.5 ${className}`}
    >
      <div className="flex items-center justify-between text-xs">
        <span className="inline-flex items-center gap-1.5 font-mono text-[11px] text-burgundy font-semibold uppercase tracking-wider">
          <ShieldCheck className="w-3.5 h-3.5 text-chinese-red" />
          Documented Provenance
        </span>
        <span className="text-[11px] font-mono text-ink-muted">
          {count} Source{count > 1 ? "s" : ""}
        </span>
      </div>
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs text-ink font-serif italic leading-relaxed">
          {primary.citation || primary.title || primary.name}
          {primary.publisher && (
            <span className="block text-[11px] font-mono text-ink-muted not-italic mt-0.5">
              Published by {primary.publisher}
            </span>
          )}
        </p>
        {primary.url && (
          <a
            href={primary.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-chinese-red hover:text-burgundy transition-colors shrink-0 p-1"
            title="Inspect Primary Archival Document"
            aria-label="Inspect Primary Archival Document"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>
    </div>
  );
}

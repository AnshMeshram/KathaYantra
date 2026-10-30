"use client";

import React from "react";
import { StoryRecord } from "@/types/story";
import { StoryCard } from "@/components/stories/story-card";
import { BookOpen, SearchX, Loader2 } from "lucide-react";

interface StoryGridProps {
  stories: StoryRecord[];
  isLoading?: boolean;
  featuredFirst?: boolean;
  onResetFilters?: () => void;
  className?: string;
}

export function StoryGrid({
  stories,
  isLoading = false,
  featuredFirst = true,
  onResetFilters,
  className = "",
}: StoryGridProps) {
  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center gap-4 text-center">
        <Loader2 className="w-8 h-8 text-chinese-red animate-spin" />
        <p className="font-display text-lg text-burgundy tracking-wide">
          Consulting the KathaYantra Archive...
        </p>
        <span className="text-xs font-mono text-ink-muted">
          Retrieving verified cultural folklore and rights-checked narratives
        </span>
      </div>
    );
  }

  if (!stories || stories.length === 0) {
    return (
      <div className="py-16 px-6 bg-parchment-light border border-parchment-border rounded-xs text-center max-w-xl mx-auto my-8">
        <div className="w-12 h-12 rounded-full bg-parchment-deep border border-parchment-border flex items-center justify-center mx-auto mb-4 text-ink-muted">
          <SearchX className="w-6 h-6 text-chinese-red" />
        </div>
        <h3 className="font-display text-xl font-bold text-burgundy mb-2">
          No Stories Found
        </h3>
        <p className="font-serif text-sm text-ink-muted leading-relaxed mb-6">
          No folklore or urban legend narratives match your current query or
          filter criteria in the verified archive.
        </p>
        {onResetFilters && (
          <button
            onClick={onResetFilters}
            className="px-5 py-2.5 bg-chinese-red text-white hover:bg-burgundy transition-colors text-xs font-mono font-semibold uppercase tracking-wider rounded-xs"
          >
            Clear All Filters
          </button>
        )}
      </div>
    );
  }

  const hasFeatured = featuredFirst && stories.length > 0;
  const featuredStory = hasFeatured ? stories[0] : null;
  const gridStories = hasFeatured ? stories.slice(1) : stories;

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Featured Header Entry */}
      {featuredStory && (
        <div className="mb-8">
          <StoryCard story={featuredStory} variant="featured" />
        </div>
      )}

      {/* Asymmetric Editorial Grid */}
      {gridStories.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gridStories.map((story) => (
            <StoryCard key={story.id} story={story} variant="standard" />
          ))}
        </div>
      )}
    </div>
  );
}

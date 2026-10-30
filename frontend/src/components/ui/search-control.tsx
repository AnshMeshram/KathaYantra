"use client";

import { useEffect, useRef, useState } from "react";
import { Search, X, Loader2, BookOpen, Skull, MapPin } from "lucide-react";
import { api } from "@/lib/api/client";
import { SearchSuggestion } from "@/types/api";
import { StoryRecord } from "@/types/story";
import Link from "next/link";

interface SearchControlProps {
  onSelectStory?: (storyId: string) => void;
  onSelectCountry?: (countryCode: string) => void;
}

export function SearchControl({
  onSelectStory,
  onSelectCountry,
}: SearchControlProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [searchResults, setSearchResults] = useState<StoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut Ctrl+K or Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
      setSuggestions([]);
      setSearchResults([]);
    }
  }, [isOpen]);

  // Live query fetching
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const [suggestData, searchData] = await Promise.all([
          api.suggest(query, 5).catch(() => []),
          api.search(query, { limit: 5 }).catch(() => ({ data: [] })),
        ]);
        setSuggestions(suggestData);
        setSearchResults(searchData.data || []);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <>
      {/* Search trigger button */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-plum/80 hover:bg-plum border border-charcoal-wine text-ash hover:text-gold transition-colors text-xs font-mono"
        aria-label="Search folklore archive (Press Ctrl+K)"
      >
        <Search className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Search archive...</span>
        <kbd className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-obsidian text-[10px] text-ash/70 border border-charcoal-wine/60">
          ⌘K
        </kbd>
      </button>

      {/* Modal Dialog */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[100] bg-obsidian/80 backdrop-blur-sm flex items-start justify-center pt-20 px-4 animate-fadeIn"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="w-full max-w-2xl bg-plum border border-gold/40 rounded-lg shadow-gothic-card overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Input Bar */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-charcoal-wine">
              <Search className="w-5 h-5 text-gold shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search 300 folklore tales, urban legends, motifs, creatures..."
                className="w-full bg-transparent text-ivory placeholder:text-ash/60 text-sm font-serif focus:outline-none"
              />
              {isLoading && (
                <Loader2 className="w-4 h-4 text-gold animate-spin" />
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 text-ash hover:text-ivory rounded"
                aria-label="Close search"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Results Area */}
            <div className="max-h-96 overflow-y-auto p-4 space-y-4">
              {query.length < 2 && (
                <div className="text-center py-6 text-ash/60 text-xs font-serif">
                  Type at least 2 characters to search by title, creature, motif
                  (e.g. Betal, Kappa, La Llorona, Mothman), or region.
                </div>
              )}

              {/* Suggestions */}
              {suggestions.length > 0 && (
                <div>
                  <div className="font-mono text-[10px] text-gold uppercase tracking-wider mb-2">
                    Quick Suggestions
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((s, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setQuery(s.text);
                          if (s.country_code && onSelectCountry) {
                            onSelectCountry(s.country_code);
                            setIsOpen(false);
                          }
                        }}
                        className="px-2.5 py-1 rounded bg-obsidian border border-charcoal-wine hover:border-gold/50 text-xs font-serif text-ivory/90 hover:text-gold flex items-center gap-1.5 transition-colors"
                      >
                        {s.suggestion_type === "region" && (
                          <MapPin className="w-3 h-3 text-gold/70" />
                        )}
                        {s.suggestion_type === "motif" && (
                          <span className="font-mono text-gold text-[10px]">
                            #
                          </span>
                        )}
                        <span>{s.text}</span>
                        {s.country_code && (
                          <span className="font-mono text-[9px] text-ash/60">
                            ({s.country_code})
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Story Search Results */}
              {searchResults.length > 0 && (
                <div className="space-y-2">
                  <div className="font-mono text-[10px] text-gold uppercase tracking-wider mb-1">
                    Archival Records Found ({searchResults.length})
                  </div>
                  {searchResults.map((story) => (
                    <div
                      key={story.id}
                      onClick={() => {
                        if (onSelectStory) onSelectStory(story.id);
                        if (onSelectCountry)
                          onSelectCountry(story.country_code);
                        setIsOpen(false);
                      }}
                      className="p-3 rounded bg-obsidian/70 hover:bg-obsidian border border-charcoal-wine hover:border-gold/50 cursor-pointer transition-all flex items-start justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {story.category === "folklore" ? (
                            <BookOpen className="w-3.5 h-3.5 text-gold shrink-0" />
                          ) : (
                            <Skull className="w-3.5 h-3.5 text-blood shrink-0" />
                          )}
                          <span className="font-gothic text-base font-bold text-ivory hover:text-gold transition-colors">
                            {story.title}
                          </span>
                        </div>
                        <p className="font-serif text-xs text-ash line-clamp-2">
                          {story.summary}
                        </p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-plum border border-charcoal-wine text-gold">
                          {story.country_code}
                        </span>
                        <div className="font-mono text-[9px] text-ash/60 mt-1">
                          {story.id}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {query.length >= 2 &&
                !isLoading &&
                searchResults.length === 0 &&
                suggestions.length === 0 && (
                  <div className="text-center py-6 text-ash text-xs font-serif italic">
                    No documented folklore records matching &quot;{query}&quot;.
                  </div>
                )}
            </div>

            {/* Footer helper */}
            <div className="px-4 py-2 bg-obsidian/90 border-t border-charcoal-wine text-[10px] font-mono text-ash/60 flex items-center justify-between">
              <span>Press ESC to close</span>
              <span>FastAPI FTS5 Catalog Search</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

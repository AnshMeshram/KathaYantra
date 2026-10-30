"use client";

import { useEffect, useRef, useState } from "react";
import { Search, X, Loader2, BookOpen, Ghost, MapPin } from "lucide-react";
import { api } from "@/lib/api/client";
import { SearchSuggestion } from "@/types/api";
import { StoryRecord } from "@/types/story";

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
        const [suggestionsData, searchRes] = await Promise.all([
          api.suggest(query).catch(() => []),
          api.search(query, { limit: 12 }).catch(() => ({ data: [] })),
        ]);
        setSuggestions(suggestionsData || []);
        setSearchResults(searchRes.data || []);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setIsLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <>
      {/* Search Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-sm bg-parchment-light hover:bg-parchment-deep border border-parchment-border text-ink-muted hover:text-burgundy transition-colors text-xs font-serif shadow-sm group"
        aria-label="Search folklore archive (Cmd+K)"
      >
        <Search className="w-3.5 h-3.5 text-burgundy group-hover:scale-105 transition-transform" />
        <span className="hidden sm:inline">Search archive...</span>
        <kbd className="hidden sm:inline-block font-mono text-[9px] px-1.5 py-0.5 rounded-sm bg-parchment-deep border border-parchment-border text-ink-faint">
          ⌘K
        </kbd>
      </button>

      {/* Modal Dialog */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[100] bg-ink/60 backdrop-blur-sm flex items-start justify-center pt-20 px-4 animate-fadeIn"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="w-full max-w-2xl bg-parchment-light border border-parchment-border rounded-sm shadow-panel overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Input Bar */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-parchment-border bg-parchment">
              <Search className="w-4 h-4 text-burgundy shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search 300 folklore tales, urban legends, creatures, regions..."
                className="w-full bg-transparent text-ink placeholder:text-ink-faint text-sm font-serif focus:outline-none"
              />
              {isLoading && (
                <Loader2 className="w-4 h-4 text-burgundy animate-spin" />
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 text-ink-muted hover:text-burgundy rounded-sm"
                aria-label="Close search"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Results Area */}
            <div className="max-h-96 overflow-y-auto p-4 space-y-4">
              {query.length < 2 && (
                <div className="text-center py-6 text-ink-faint text-xs font-serif">
                  Type at least 2 characters to search by title, creature, motif (e.g. Betal, Kappa, La Llorona, Mothman), or region.
                </div>
              )}

              {/* Suggestions */}
              {suggestions.length > 0 && (
                <div>
                  <div className="font-mono text-[10px] text-burgundy uppercase tracking-widest mb-2 font-semibold">
                    Suggestions
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
                        className="px-2.5 py-1 rounded-sm bg-parchment border border-parchment-border hover:border-chinese-red text-xs font-serif text-ink hover:text-chinese-red flex items-center gap-1.5 transition-colors"
                      >
                        {s.suggestion_type === "region" && (
                          <MapPin className="w-3 h-3 text-burgundy" />
                        )}
                        {s.suggestion_type === "motif" && (
                          <span className="font-mono text-satsuma text-[10px]">
                            #
                          </span>
                        )}
                        <span>{s.text}</span>
                        {s.country_code && (
                          <span className="font-mono text-[9px] text-ink-faint">
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
                  <div className="font-mono text-[10px] text-burgundy uppercase tracking-widest mb-1 font-semibold">
                    Records Found ({searchResults.length})
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
                      className="p-3 rounded-sm bg-parchment hover:bg-parchment-deep border border-parchment-border hover:border-chinese-red cursor-pointer transition-all flex items-start justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {story.category === "folklore" ? (
                            <BookOpen className="w-3.5 h-3.5 text-chinese-red shrink-0" />
                          ) : (
                            <Ghost className="w-3.5 h-3.5 text-cobalt shrink-0" />
                          )}
                          <span className="font-display text-sm font-bold text-burgundy hover:text-chinese-red transition-colors">
                            {story.title}
                          </span>
                        </div>
                        <p className="font-serif text-xs text-ink-muted line-clamp-2">
                          {story.summary}
                        </p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded-sm bg-parchment-light border border-parchment-border text-burgundy font-bold">
                          {story.country_code}
                        </span>
                        <div className="font-mono text-[9px] text-ink-faint mt-1">
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
                  <div className="text-center py-6 text-ink-muted text-xs font-serif italic">
                    No documented folklore records matching &quot;{query}&quot;.
                  </div>
                )}
            </div>

            {/* Footer helper */}
            <div className="px-4 py-2 bg-parchment border-t border-parchment-border text-[10px] font-mono text-ink-faint flex items-center justify-between">
              <span>Press ESC to close</span>
              <span>FastAPI Full-Text Catalog Search</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

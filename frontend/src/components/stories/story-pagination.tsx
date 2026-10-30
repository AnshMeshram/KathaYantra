"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface StoryPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function StoryPagination({
  currentPage,
  totalPages,
  onPageChange,
  className = "",
}: StoryPaginationProps) {
  if (totalPages <= 1) return null;

  const pages = [];
  const maxVisible = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage + 1 < maxVisible) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return (
    <nav
      className={`flex items-center justify-center gap-1.5 font-mono text-xs ${className}`}
      aria-label="Story collection pagination"
    >
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="px-3 py-2 border border-parchment-border bg-parchment-light rounded-xs text-ink hover:border-chinese-red disabled:opacity-40 disabled:hover:border-parchment-border disabled:cursor-not-allowed transition-colors flex items-center gap-1"
        aria-label="Previous Page"
      >
        <ChevronLeft className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Previous</span>
      </button>

      {startPage > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            className="w-9 h-9 border border-parchment-border bg-parchment-light rounded-xs hover:border-chinese-red transition-colors"
          >
            1
          </button>
          {startPage > 2 && <span className="px-1 text-ink-muted">...</span>}
        </>
      )}

      {pages.map((p) => {
        const isActive = p === currentPage;
        return (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            aria-current={isActive ? "page" : undefined}
            className={`w-9 h-9 rounded-xs font-semibold transition-all ${
              isActive
                ? "bg-chinese-red text-white border border-chinese-red shadow-xs"
                : "border border-parchment-border bg-parchment-light text-ink hover:border-chinese-red"
            }`}
          >
            {p}
          </button>
        );
      })}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="px-1 text-ink-muted">...</span>}
          <button
            onClick={() => onPageChange(totalPages)}
            className="w-9 h-9 border border-parchment-border bg-parchment-light rounded-xs hover:border-chinese-red transition-colors"
          >
            {totalPages}
          </button>
        </>
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="px-3 py-2 border border-parchment-border bg-parchment-light rounded-xs text-ink hover:border-chinese-red disabled:opacity-40 disabled:hover:border-parchment-border disabled:cursor-not-allowed transition-colors flex items-center gap-1"
        aria-label="Next Page"
      >
        <span className="hidden sm:inline">Next</span>
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    </nav>
  );
}

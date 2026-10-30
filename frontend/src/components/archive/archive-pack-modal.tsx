"use client";

import React, { useState } from "react";
import { Download, X, ShieldCheck, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api/client";

interface ArchivePackModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  category?: string;
  countryCode?: string;
  recordCount: number;
}

export function ArchivePackModal({
  isOpen,
  onClose,
  title,
  category,
  countryCode,
  recordCount,
}: ArchivePackModalProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);

    try {
      await api.downloadArchivePack({
        category: category || undefined,
        country_code: countryCode || undefined,
      });
      setDownloadSuccess(true);
    } catch (err: any) {
      setDownloadError(err?.message || "Failed to generate archival pack. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-ink/60 backdrop-blur-xs animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="archive-pack-title"
    >
      <div className="relative w-full max-w-lg bg-parchment-light border-2 border-parchment-border rounded-xs shadow-2xl p-6 md:p-8 flex flex-col gap-5 text-ink">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1.5 text-ink-muted hover:text-chinese-red transition-colors"
          aria-label="Close download dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-xs text-[11px] font-mono text-chinese-red bg-chinese-red/10 border border-chinese-red/20 mb-2 font-bold uppercase tracking-wider">
            <Download className="w-3.5 h-3.5" />
            Rights-Compliant Export Bundle
          </div>
          <h3 id="archive-pack-title" className="font-display text-2xl font-bold text-burgundy tracking-tight">
            {title}
          </h3>
          <p className="font-serif text-xs text-ink/80 mt-1">
            Curated export bundle containing <strong className="text-burgundy font-bold">{recordCount}</strong> verified cultural records.
          </p>
        </div>

        {/* Included Formats Manifest */}
        <div className="bg-parchment p-4 rounded-xs border border-parchment-border/80 flex flex-col gap-2.5 text-xs font-mono">
          <span className="font-bold text-burgundy uppercase text-[11px] tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-chinese-red" />
            Included Archival Package Manifest:
          </span>
          <ul className="space-y-1.5 text-[11px] text-ink/80 pl-1">
            <li>• <strong className="text-ink">README.md</strong> — Scope, version, and ethical attribution instructions.</li>
            <li>• <strong className="text-ink">archive-manifest.json</strong> — Integrity metadata and filter specifications.</li>
            <li>• <strong className="text-ink">stories.json</strong> — Full structured records with cultural motifs and themes.</li>
            <li>• <strong className="text-ink">stories.csv</strong> — Universal research spreadsheet for digital humanities.</li>
            <li>• <strong className="text-ink">sources/source-manifest.json</strong> — Primary bibliographic and academic citations.</li>
            <li>• <strong className="text-ink">images/image-attribution.json</strong> — Public Domain / CC0 license attribution log.</li>
          </ul>
        </div>

        {/* Rights & Licensing Disclosure */}
        <div className="p-3.5 bg-lunar-yellow/15 border border-lunar-yellow/30 rounded-xs text-[11px] font-serif text-ink leading-relaxed flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-chinese-red shrink-0 mt-0.5" />
          <p>
            <strong>Licensing & Redistribution Policy:</strong> In compliance with cultural preservation guidelines, actual image binaries are bundled only when explicit Public Domain or CC0 terms permit. For other entries, verified permanent source URLs and attribution metadata are included.
          </p>
        </div>

        {/* Status Alerts */}
        {downloadSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xs text-xs font-mono flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Archive pack generated successfully! Download started.</span>
          </div>
        )}

        {downloadError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xs text-xs font-mono flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{downloadError}</span>
          </div>
        )}

        {/* Modal Actions */}
        <div className="pt-3 border-t border-parchment-border flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-parchment-border bg-parchment hover:bg-parchment-deep rounded-xs text-xs font-mono text-ink transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="px-5 py-2.5 bg-chinese-red text-white hover:bg-burgundy disabled:opacity-50 transition-colors text-xs font-mono font-bold uppercase tracking-wider rounded-xs flex items-center gap-2 shadow-xs"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Compiling ZIP...</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Download Archive Pack</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

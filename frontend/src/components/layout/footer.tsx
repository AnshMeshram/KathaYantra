import Link from "next/link";
import { ShieldCheck, Compass, BookOpen, Layers } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full bg-ink-deep border-t border-stone px-4 sm:px-6 lg:px-8 py-12 mt-20 text-linen-muted font-serif text-sm">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
        {/* Col 1: Project Identity */}
        <div className="space-y-3 md:col-span-2">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-sm bg-parchment border border-brass/40 flex items-center justify-center">
              <Compass className="w-3.5 h-3.5 text-brass" />
            </div>
            <h3 className="font-display text-xl text-linen font-bold uppercase tracking-[0.16em]">
              KathaYantra
            </h3>
          </div>
          <p className="text-linen-muted text-xs leading-relaxed max-w-md">
            An open-access digital folklore museum and geographical atlas preserving 300 verified
            traditional narratives and urban legends across 15 nations with verifiable institutional provenance.
          </p>
          <div className="flex items-center gap-2 text-xs font-mono text-brass/90 pt-1">
            <ShieldCheck className="w-4 h-4 text-brass shrink-0" />
            <span>Ethical Heritage Safeguard: Zero synthetic AI artwork. Authentic cultural documentation.</span>
          </div>
        </div>

        {/* Col 2: Archival Quotas */}
        <div className="space-y-2">
          <h4 className="font-mono text-xs text-linen uppercase tracking-widest font-semibold border-b border-stone/60 pb-1">
            Archival Quotas
          </h4>
          <ul className="space-y-1.5 text-xs font-mono text-linen-muted">
            <li className="flex items-center justify-between">
              <span>Sovereign Nations</span>
              <span className="text-brass">15</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Folklore Narratives</span>
              <span className="text-brass">150</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Urban Legends</span>
              <span className="text-brass">150</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Total Catalogued</span>
              <span className="text-brass font-bold">300</span>
            </li>
          </ul>
        </div>

        {/* Col 3: Research Provenance */}
        <div className="space-y-2">
          <h4 className="font-mono text-xs text-linen uppercase tracking-widest font-semibold border-b border-stone/60 pb-1">
            Institutional Provenance
          </h4>
          <ul className="space-y-1.5 text-xs text-linen-muted">
            <li>Wikimedia Commons Cultural Heritage</li>
            <li>Library of Congress Prints & Photographs</li>
            <li>Metropolitan Museum of Art Open Access</li>
            <li>Rijksmuseum & Wellcome Collection</li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-stone/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-linen-faint">
        <p>© 2026 KathaYantra. Curated Cultural Heritage.</p>
        <p className="italic font-serif text-linen-muted">
          Preserve the story. Trace the source. Respect the culture.
        </p>
      </div>
    </footer>
  );
}

import Link from "next/link";
import { Shield, Sparkles, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full bg-obsidian border-t border-charcoal-wine/80 px-4 lg:px-8 py-8 mt-16 text-ash font-serif text-sm">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        {/* Col 1: Project Identity */}
        <div className="space-y-3 md:col-span-2">
          <h3 className="font-gothic text-xl text-gold font-bold uppercase tracking-wider">
            KathaYantra
          </h3>
          <p className="text-ash/80 text-xs leading-relaxed max-w-md">
            A local-first, rights-aware digital archive and supernatural atlas
            preserving 300 traditional folklore narratives and modern urban
            legends across 15 nations with verified bibliographic provenance and
            zero synthetic hallucination.
          </p>
          <div className="flex items-center gap-2 text-xs font-mono text-gold/80">
            <Shield className="w-4 h-4 text-gold" />
            <span>
              Ethical Heritage Safeguard: Zero AI-generated artwork. Genuine
              cultural documentation.
            </span>
          </div>
        </div>

        {/* Col 2: Nations & Archives */}
        <div className="space-y-2">
          <h4 className="font-mono text-xs text-ivory uppercase tracking-wider font-semibold">
            Archival Quotas
          </h4>
          <ul className="space-y-1 text-xs">
            <li>15 Sovereign Target Nations</li>
            <li>150 Verified Folklore Tales</li>
            <li>150 Documented Urban Legends</li>
            <li>3,000 Historical Museum Images</li>
          </ul>
        </div>

        {/* Col 3: Research Provenance */}
        <div className="space-y-2">
          <h4 className="font-mono text-xs text-ivory uppercase tracking-wider font-semibold">
            Sources & Governance
          </h4>
          <ul className="space-y-1 text-xs">
            <li>Wikimedia Commons Cultural Heritage</li>
            <li>Library of Congress Prints & Photos</li>
            <li>Metropolitan Museum of Art Open Access</li>
            <li>Europeana & National Diet Library</li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-charcoal-wine/50 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-ash/60">
        <p>
          © 2026 KathaYantra Archive. Public domain and openly licensed cultural
          heritage.
        </p>
        <p className="italic font-serif">
          Preserve the story. Trace the source. Respect the culture. Keep the AI
          honest.
        </p>
      </div>
    </footer>
  );
}

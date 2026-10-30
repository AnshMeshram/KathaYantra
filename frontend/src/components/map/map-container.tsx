"use client";

import dynamic from "next/dynamic";
import { Loader2 } from "lucide-react";

interface MapContainerProps {
  onSelectCountry?: (code: string) => void;
  selectedCountry?: string | null;
}

// Dynamically import WorldMap with SSR disabled to prevent browser window reference errors
const DynamicWorldMap = dynamic(() => import("@/components/map/world-map"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[75vh] md:h-[82vh] rounded-xl overflow-hidden border border-charcoal-wine bg-[#101016] flex flex-col items-center justify-center gap-3">
      <Loader2 className="w-8 h-8 text-gold animate-spin" />
      <span className="font-gothic text-base text-gold uppercase tracking-widest">
        Loading The Haunted Atlas...
      </span>
    </div>
  ),
});

export function MapContainer(props: MapContainerProps) {
  return <DynamicWorldMap {...props} />;
}


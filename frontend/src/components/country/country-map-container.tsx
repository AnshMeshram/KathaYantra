"use client";

import dynamic from "next/dynamic";
import { StoryRecord } from "@/types/story";
import { StoryLocationRecord } from "@/components/country/country-map-explorer";

interface CountryMapContainerProps {
  countryCode: string;
  countryName: string;
  stories: StoryRecord[];
  locations: StoryLocationRecord[];
}

const DynamicCountryMapExplorer = dynamic(
  () => import("@/components/country/country-map-explorer"),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[600px] bg-parchment-deep rounded-sm border border-parchment-border flex flex-col items-center justify-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-parchment-border border-t-chinese-red animate-spin" />
        <span className="font-display text-sm text-burgundy tracking-widest uppercase">
          Loading Regional Cartography...
        </span>
      </div>
    ),
  }
);

export function CountryMapContainer(props: CountryMapContainerProps) {
  return <DynamicCountryMapExplorer {...props} />;
}

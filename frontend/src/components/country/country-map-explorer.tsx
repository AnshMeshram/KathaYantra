"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";
import Link from "next/link";
import {
  Compass,
  BookOpen,
  Ghost,
  MapPin,
  ExternalLink,
  ShieldCheck,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Info,
} from "lucide-react";
import { SUPPORTED_COUNTRIES } from "@/constants/countries";
import { StoryRecord } from "@/types/story";
import { getStoryRoute } from "@/lib/routes";

export interface StoryLocationRecord {
  story_id: string;
  story_title: string;
  country_code: string;
  category: "folklore" | "urban_legend";
  place_name: string;
  administrative_region: string;
  latitude: number | null;
  longitude: number | null;
  coordinate_precision: string;
  verification_status: string;
  supporting_source: string;
  evidence: string;
  has_coordinates: boolean;
}

interface CountryMapExplorerProps {
  countryCode: string;
  countryName: string;
  stories: StoryRecord[];
  locations: StoryLocationRecord[];
}

interface ConnectorPoint {
  id: string;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  category: "folklore" | "urban_legend";
}

export default function CountryMapExplorer({
  countryCode,
  countryName,
  stories,
  locations,
}: CountryMapExplorerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const cardRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  const [activeStoryId, setActiveStoryId] = useState<string | null>(null);
  const [hoveredStoryId, setHoveredStoryId] = useState<string | null>(null);
  const [connectors, setConnectors] = useState<ConnectorPoint[]>([]);
  const [filterCategory, setFilterCategory] = useState<"all" | "folklore" | "urban_legend">("all");

  const meta = SUPPORTED_COUNTRIES[countryCode.toUpperCase()];
  const mappedLocations = locations.filter(
    (l) => l.has_coordinates && l.latitude !== null && l.longitude !== null
  );

  const displayedLocations = mappedLocations.filter((l) => {
    if (filterCategory === "all") return true;
    return l.category === filterCategory;
  });

  // Top 3 primary cards to display alongside the map on desktop
  const activeCards = (
    activeStoryId
      ? [
          ...displayedLocations.filter((l) => l.story_id === activeStoryId),
          ...displayedLocations.filter((l) => l.story_id !== activeStoryId),
        ]
      : displayedLocations
  ).slice(0, 3);

  // Function to re-calculate SVG spider-silk connectors
  const updateConnectors = useCallback(() => {
    const map = mapInstanceRef.current;
    const container = containerRef.current;
    if (!map || !container) return;

    const containerRect = container.getBoundingClientRect();
    const newConnectors: ConnectorPoint[] = [];

    activeCards.forEach((loc) => {
      if (loc.latitude === null || loc.longitude === null) return;

      // 1. Convert marker LatLng to pixel coordinate relative to map container
      const markerPoint = map.latLngToContainerPoint([loc.latitude, loc.longitude]);

      // 2. Get card DOM anchor element position
      const cardEl = cardRefs.current.get(loc.story_id);
      if (!cardEl) return;

      const cardRect = cardEl.getBoundingClientRect();

      // Start: Marker position relative to outer explorer container
      const mapRect = mapContainerRef.current?.getBoundingClientRect();
      if (!mapRect) return;

      const startX = mapRect.left - containerRect.left + markerPoint.x;
      const startY = mapRect.top - containerRect.top + markerPoint.y;

      // End: Left-center anchor of the card
      const endX = cardRect.left - containerRect.left;
      const endY = cardRect.top - containerRect.top + cardRect.height / 2;

      newConnectors.push({
        id: loc.story_id,
        startX,
        startY,
        endX,
        endY,
        category: loc.category,
      });
    });

    setConnectors(newConnectors);
  }, [activeCards]);

  // Initialize Country Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const defaultCenter: [number, number] = meta
      ? [meta.lat, meta.lng]
      : [20.0, 78.0];
    const defaultZoom = meta ? meta.zoom : 5;

    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: defaultZoom,
      minZoom: 3,
      maxZoom: 11,
      zoomControl: false,
      attributionControl: true,
    });

    mapInstanceRef.current = map;

    // Load GeoJSON for Country Boundary & Fit Bounds
    fetch("/data/geo/countries.geojson")
      .then((res) => (res.ok ? res.json() : null))
      .then((geoData) => {
        if (!geoData) return;
        const countryFeature = geoData.features?.find((f: any) => {
          const props = f.properties || {};
          const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
          return code === countryCode.toUpperCase();
        });

        if (countryFeature) {
          const layer = L.geoJSON(countryFeature, {
            style: {
              fillColor: "#FAF4EC",
              fillOpacity: 0.7,
              color: "#70191D", // Burgundy boundary
              weight: 2,
              dashArray: "",
            },
          }).addTo(map);

          try {
            map.fitBounds(layer.getBounds(), { padding: [40, 40], maxZoom: 6.5 });
          } catch {
            // fallback to default center
          }
        }
      })
      .catch((err) => console.error("Error loading country boundary:", err));

    // Map Event Listeners for smooth connector line tracking
    map.on("move", updateConnectors);
    map.on("zoom", updateConnectors);
    map.on("resize", updateConnectors);

    setTimeout(() => {
      map.invalidateSize();
      updateConnectors();
    }, 300);

    return () => {
      map.off("move", updateConnectors);
      map.off("zoom", updateConnectors);
      map.off("resize", updateConnectors);
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [countryCode, meta, updateConnectors]);

  // Render Markers on Map
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const markersGroup = L.layerGroup().addTo(map);

    displayedLocations.forEach((loc) => {
      if (loc.latitude === null || loc.longitude === null) return;

      const isFolklore = loc.category === "folklore";
      const isSelected = activeStoryId === loc.story_id;
      const isHovered = hoveredStoryId === loc.story_id;

      const marker = L.circleMarker([loc.latitude, loc.longitude], {
        radius: isSelected || isHovered ? 7.5 : 5.5,
        fillColor: isFolklore ? "#970A12" : "#5686BB",
        color: isSelected ? "#FECD6D" : "#FAF4EC",
        weight: isSelected ? 2.5 : 1.5,
        opacity: 1,
        fillOpacity: 0.95,
      });

      marker.bindTooltip(
        `<div style="font-family: serif; font-size: 11px; padding: 3px 6px; color: #251D1B;">
          <strong style="color: ${isFolklore ? "#70191D" : "#5686BB"};">${loc.place_name}</strong>
          <div style="font-size: 10px; color: #766B62;">${loc.story_title}</div>
        </div>`,
        { direction: "top", offset: [0, -6] }
      );

      marker.on("mouseover", () => setHoveredStoryId(loc.story_id));
      marker.on("mouseout", () => setHoveredStoryId(null));
      marker.on("click", () => {
        setActiveStoryId(loc.story_id);
      });

      marker.addTo(markersGroup);
    });

    updateConnectors();

    return () => {
      map.removeLayer(markersGroup);
    };
  }, [displayedLocations, activeStoryId, hoveredStoryId, updateConnectors]);

  // Window resize handler
  useEffect(() => {
    window.addEventListener("resize", updateConnectors);
    return () => window.removeEventListener("resize", updateConnectors);
  }, [updateConnectors]);

  const handleResetMap = () => {
    if (mapInstanceRef.current && meta) {
      mapInstanceRef.current.flyTo([meta.lat, meta.lng], meta.zoom, { duration: 0.8 });
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full rounded-sm border border-parchment-border bg-parchment-light shadow-panel overflow-hidden"
    >
      {/* Editorial Country Map Toolbar */}
      <div className="p-4 sm:p-5 border-b border-parchment-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-parchment">
        <div>
          <div className="flex items-center gap-2">
            <span className="hanko-seal">{countryCode.toUpperCase()}</span>
            <span className="font-mono text-xs uppercase tracking-widest text-ink-muted">
              Regional Topographical Exploration
            </span>
          </div>
          <h3 className="font-display text-2xl sm:text-3xl font-bold text-burgundy mt-1">
            {countryName} Cartographic Archives
          </h3>
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-1.5 bg-parchment-deep p-1 rounded-sm border border-parchment-border text-xs font-mono">
          {(["all", "folklore", "urban_legend"] as const).map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1 rounded-sm uppercase tracking-wider transition-colors ${
                filterCategory === cat
                  ? "bg-burgundy text-parchment-light font-bold"
                  : "text-ink-muted hover:text-burgundy"
              }`}
            >
              {cat === "all" ? "All" : cat === "folklore" ? "Folklore" : "Urban"}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: 2D Country Map (Left) + Connected Story Cards (Right) */}
      <div className="relative grid grid-cols-1 lg:grid-cols-12 min-h-[580px] lg:min-h-[640px]">
        {/* Left Column: Interactive 2D Leaflet Country Map */}
        <div className="relative lg:col-span-7 h-[420px] lg:h-auto border-b lg:border-b-0 lg:border-r border-parchment-border bg-[#E8DDCB]">
          <div ref={mapContainerRef} className="w-full h-full z-0" />

          {/* Map Controls */}
          <div className="absolute top-4 left-4 z-[400] flex flex-col gap-1.5">
            <button
              type="button"
              onClick={() => mapInstanceRef.current?.zoomIn()}
              className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
              aria-label="Zoom in"
            >
              <ZoomIn className="w-4 h-4 text-burgundy" />
            </button>
            <button
              type="button"
              onClick={() => mapInstanceRef.current?.zoomOut()}
              className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
              aria-label="Zoom out"
            >
              <ZoomOut className="w-4 h-4 text-burgundy" />
            </button>
            <button
              type="button"
              onClick={handleResetMap}
              className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
              title="Reset View"
              aria-label="Reset view"
            >
              <RotateCcw className="w-3.5 h-3.5 text-burgundy" />
            </button>
          </div>

          {/* Map Legend */}
          <div className="absolute bottom-4 left-4 z-[400] bg-parchment-light/95 backdrop-blur-md border border-parchment-border rounded-sm shadow-sm px-3 py-2 text-[11px] font-serif space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#970A12] border border-[#FAF4EC]" />
              <span className="text-ink">Traditional Folklore</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#5686BB] border border-[#FAF4EC]" />
              <span className="text-ink">Urban Legends</span>
            </div>
          </div>
        </div>

        {/* Right Column: Illustrated Folklore Archive Plates (Story Cards) */}
        <div className="lg:col-span-5 p-4 sm:p-6 bg-parchment-light flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-parchment-border/70 pb-2">
              <span className="font-mono text-xs uppercase tracking-widest text-burgundy font-semibold">
                Illustrated Archival Plates ({activeCards.length} in Focus)
              </span>
              <span className="font-serif text-[11px] text-ink-faint italic">
                {mappedLocations.length} Geographically Mapped
              </span>
            </div>

            {/* Render Active Archival Story Cards */}
            <div className="space-y-3.5">
              {activeCards.map((loc) => {
                const story = stories.find((s) => s.id === loc.story_id);
                const isSelected = activeStoryId === loc.story_id;
                const isHovered = hoveredStoryId === loc.story_id;
                const isFolklore = loc.category === "folklore";

                return (
                  <div
                    key={loc.story_id}
                    ref={(el) => {
                      if (el) cardRefs.current.set(loc.story_id, el);
                      else cardRefs.current.delete(loc.story_id);
                    }}
                    onMouseEnter={() => setHoveredStoryId(loc.story_id)}
                    onMouseLeave={() => setHoveredStoryId(null)}
                    onClick={() => setActiveStoryId(loc.story_id)}
                    className={`editorial-card p-4 rounded-sm cursor-pointer transition-all space-y-2 text-left ${
                      isSelected
                        ? "border-chinese-red bg-parchment shadow-panel scale-[1.01]"
                        : isHovered
                        ? "border-burgundy bg-parchment"
                        : "border-parchment-border bg-parchment-light hover:border-burgundy"
                    }`}
                  >
                    {/* Header line: Place & Category */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 text-xs font-mono">
                        <MapPin
                          className={`w-3.5 h-3.5 ${
                            isFolklore ? "text-chinese-red" : "text-cobalt"
                          }`}
                        />
                        <span className="font-semibold text-ink">
                          {loc.place_name}
                        </span>
                        <span className="text-ink-faint text-[10px]">
                          ({loc.coordinate_precision})
                        </span>
                      </div>
                      <span
                        className={`font-mono text-[9px] px-1.5 py-0.5 rounded-sm uppercase tracking-wider font-bold ${
                          isFolklore
                            ? "bg-burgundy text-parchment-light"
                            : "bg-cobalt text-parchment-light"
                        }`}
                      >
                        {isFolklore ? "Folklore" : "Urban Legend"}
                      </span>
                    </div>

                    {/* Story Title */}
                    <h4 className="font-display text-lg font-bold text-burgundy hover:text-chinese-red transition-colors leading-snug">
                      {loc.story_title}
                    </h4>

                    {/* Summary Excerpt */}
                    <p className="font-serif text-xs text-ink-muted line-clamp-2 leading-relaxed">
                      {story?.summary || loc.evidence}
                    </p>

                    {/* Provenance Footer */}
                    <div className="pt-2 border-t border-parchment-border/60 flex items-center justify-between text-[10px] font-mono text-ink-faint">
                      <span className="truncate max-w-[200px]">
                        Ref: {loc.supporting_source}
                      </span>
                      <span className="text-chinese-red font-semibold hover:underline">
                        Plate #{loc.story_id} →
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-2 text-center text-xs font-serif text-ink-muted italic border-t border-parchment-border/70">
            Click any regional marker or card to pin its geographical spider-silk connection.
          </div>
        </div>

        {/* Spider-Silk SVG Connector Layer (Desktop Only, Pointer-Events None) */}
        <svg
          className="pointer-events-none absolute inset-0 w-full h-full z-20 hidden lg:block"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <marker
              id="dot-folklore"
              viewBox="0 0 6 6"
              refX="3"
              refY="3"
              markerWidth="4"
              markerHeight="4"
            >
              <circle cx="3" cy="3" r="2.5" fill="#970A12" />
            </marker>
            <marker
              id="dot-urban"
              viewBox="0 0 6 6"
              refX="3"
              refY="3"
              markerWidth="4"
              markerHeight="4"
            >
              <circle cx="3" cy="3" r="2.5" fill="#5686BB" />
            </marker>
          </defs>

          {connectors.map((c) => {
            const isHovered = hoveredStoryId === c.id;
            const isSelected = activeStoryId === c.id;
            const isFolklore = c.category === "folklore";

            const strokeColor = isFolklore ? "#970A12" : "#5686BB";
            const strokeWidth = isSelected || isHovered ? 2.2 : 1.1;
            const strokeOpacity = isSelected || isHovered ? 0.95 : 0.45;

            // Deterministic cubic Bézier curve calculation
            const dx = Math.abs(c.endX - c.startX);
            const cx1 = c.startX + dx * 0.45;
            const cy1 = c.startY;
            const cx2 = c.endX - dx * 0.45;
            const cy2 = c.endY;

            const pathD = `M ${c.startX} ${c.startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${c.endX} ${c.endY}`;

            return (
              <g key={c.id}>
                {/* Spider-Silk Path */}
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeOpacity={strokeOpacity}
                  markerEnd={isFolklore ? "url(#dot-folklore)" : "url(#dot-urban)"}
                  className="transition-all duration-300"
                />
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

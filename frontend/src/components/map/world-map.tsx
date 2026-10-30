"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { SUPPORTED_COUNTRIES, isCountrySupported, UNSUPPORTED_COUNTRY_NOTICE } from "@/constants/countries";
import { MapLegend } from "@/components/map/map-legend";
import { CountryInformationDrawer } from "@/components/map/country-information-drawer";
import { RotateCcw, ZoomIn, ZoomOut } from "lucide-react";

interface WorldMapProps {
  onSelectCountry?: (code: string) => void;
  selectedCountry?: string | null;
}

export default function WorldMap({ onSelectCountry, selectedCountry }: WorldMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geojsonLayerRef = useRef<L.GeoJSON | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  const [geoData, setGeoData] = useState<any | null>(null);
  const [activeCountry, setActiveCountry] = useState<string | null>(selectedCountry || null);
  const [hoveredCountryInfo, setHoveredCountryInfo] = useState<{
    code: string;
    name: string;
    isSupported: boolean;
  } | null>(null);
  const [isLoadingGeo, setIsLoadingGeo] = useState(true);

  // Load GeoJSON dataset from static public route
  useEffect(() => {
    fetch("/data/geo/countries.geojson")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load GeoJSON");
        return res.json();
      })
      .then((data) => {
        setGeoData(data);
      })
      .catch((err) => {
        console.error("Error loading countries.geojson:", err);
      })
      .finally(() => {
        setIsLoadingGeo(false);
      });
  }, []);

  // Update active country when external selectedCountry prop changes
  useEffect(() => {
    if (selectedCountry) {
      setActiveCountry(selectedCountry);
      const meta = SUPPORTED_COUNTRIES[selectedCountry.toUpperCase()];
      if (meta && mapInstanceRef.current) {
        mapInstanceRef.current.flyTo([meta.lat, meta.lng], meta.zoom, {
          duration: 1.2,
        });
      }
    }
  }, [selectedCountry]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20.0, 10.0],
      zoom: 2.5,
      minZoom: 1.8,
      maxZoom: 9,
      zoomControl: false,
      attributionControl: true,
      maxBounds: [
        [-85, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 0.8,
    });

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Render GeoJSON and markers when geoData or activeCountry changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !geoData) return;

    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }
    if (markersLayerRef.current) {
      markersLayerRef.current.clearLayers();
    }

    // Polygon Style Evaluator using editorial design tokens
    const styleFeature = (feature: any) => {
      const props = feature.properties || {};
      const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
      const isSupported = isCountrySupported(code);
      const isSelected = activeCountry?.toUpperCase() === code;

      if (isSelected) {
        return {
          fillColor: "#222533",
          fillOpacity: 0.9,
          color: "#E8C88B", // Illuminated Brass Light
          weight: 2.2,
          dashArray: "",
        };
      }

      if (isSupported) {
        return {
          fillColor: "#171822",
          fillOpacity: 0.85,
          color: "#D1A75C", // Antique Brass Primary
          weight: 1.5,
          dashArray: "",
        };
      }

      // Unsupported Country
      return {
        fillColor: "#0D0E14",
        fillOpacity: 0.65,
        color: "#262937", // Weathered Stone
        weight: 0.75,
        dashArray: "2, 3",
      };
    };

    // Attach Interactions to Polygons
    const onEachFeature = (feature: any, layer: L.Layer) => {
      const props = feature.properties || {};
      const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
      const name = props.name || props.NAME || code;
      const isSupported = isCountrySupported(code);

      let tooltipContent = "";
      if (isSupported) {
        const meta = SUPPORTED_COUNTRIES[code];
        tooltipContent = `
          <div style="font-family: serif; padding: 6px; min-width: 170px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <strong style="color: #D1A75C; font-size: 14px; text-transform: uppercase;">${name}</strong>
              <span style="font-family: monospace; font-size: 10px; background: #0C0D12; padding: 1px 4px; border: 1px solid #D1A75C; border-radius: 2px; color: #D1A75C;">${code}</span>
            </div>
            <div style="font-size: 11px; color: #EDE5D8; margin-bottom: 6px;">
              <div>• Folklore Tales: <strong style="color: #D1A75C;">10</strong></div>
              <div>• Urban Legends: <strong style="color: #BA382E;">10</strong></div>
              <div>• Total Records: <strong style="color: #EDE5D8;">20</strong></div>
            </div>
            <div style="font-size: 10px; color: #A39C90; border-top: 1px solid #262937; padding-top: 4px;">
              Tradition: ${meta?.primary_folklore_creature || "Documented Folklore"}
            </div>
          </div>
        `;
      } else {
        tooltipContent = `
          <div style="font-family: serif; padding: 6px; max-width: 200px;">
            <div style="color: #EDE5D8; font-size: 13px; font-weight: bold; margin-bottom: 2px;">${name}</div>
            <div style="display: inline-block; font-family: monospace; font-size: 9px; background: #1B1D27; color: #D1A75C; padding: 2px 5px; border-radius: 2px; text-transform: uppercase; margin-bottom: 4px;">
              ${UNSUPPORTED_COUNTRY_NOTICE.badge}
            </div>
            <div style="font-size: 10px; color: #A39C90; line-height: 1.3;">
              ${UNSUPPORTED_COUNTRY_NOTICE.message}
            </div>
          </div>
        `;
      }

      layer.bindTooltip(tooltipContent, {
        sticky: true,
        direction: "auto",
        className: "custom-gothic-tooltip",
        opacity: 0.95,
      });

      layer.on({
        mouseover: (e) => {
          const target = e.target;
          target.setStyle({
            weight: isSupported ? 2.5 : 1.2,
            color: isSupported ? "#E8C88B" : "#A39C90",
            fillOpacity: isSupported ? 0.95 : 0.75,
          });
          target.bringToFront();
          setHoveredCountryInfo({ code, name, isSupported });
        },
        mouseout: (e) => {
          if (geojsonLayerRef.current) {
            geojsonLayerRef.current.resetStyle(e.target);
          }
          setHoveredCountryInfo(null);
        },
        click: () => {
          if (isSupported) {
            setActiveCountry(code);
            if (onSelectCountry) onSelectCountry(code);
            const meta = SUPPORTED_COUNTRIES[code];
            if (meta) {
              map.flyTo([meta.lat, meta.lng], meta.zoom, { duration: 1.0 });
            }
          } else {
            setActiveCountry(code);
          }
        },
      });
    };

    const geoLayer = L.geoJSON(geoData, {
      style: styleFeature,
      onEachFeature: onEachFeature,
    }).addTo(map);

    geojsonLayerRef.current = geoLayer;

    // Render Cinnabar Archive Presence Markers for Supported Countries
    if (markersLayerRef.current) {
      Object.entries(SUPPORTED_COUNTRIES).forEach(([code, meta]) => {
        const marker = L.circleMarker([meta.lat, meta.lng], {
          radius: 4.5,
          fillColor: "#BA382E", // Cinnabar Lacquer Seal
          color: "#EDE5D8",
          weight: 1,
          opacity: 0.9,
          fillOpacity: 1,
        });

        marker.bindTooltip(
          `<div style="font-family: monospace; font-size: 10px; color: #EDE5D8;"><strong>${meta.name} Archive</strong> (20 stories)</div>`,
          { direction: "top", offset: [0, -5] }
        );

        marker.on("click", () => {
          setActiveCountry(code);
          if (onSelectCountry) onSelectCountry(code);
          map.flyTo([meta.lat, meta.lng], meta.zoom, { duration: 1.0 });
        });

        marker.addTo(markersLayerRef.current!);
      });
    }
  }, [geoData, activeCountry, onSelectCountry]);

  // Reset World Map View
  const handleResetView = () => {
    setActiveCountry(null);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([20.0, 10.0], 2.5, { duration: 1.0 });
    }
  };

  return (
    <div className="relative w-full h-[75vh] md:h-[82vh] rounded-sm overflow-hidden border border-stone shadow-editorial bg-[#0E1016]">
      {/* Loading Overlay */}
      {isLoadingGeo && (
        <div className="absolute inset-0 z-[500] bg-ink/90 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-stone border-t-brass animate-spin" />
          <span className="font-display text-sm text-brass tracking-widest uppercase">
            Loading Archival Cartography...
          </span>
        </div>
      )}

      {/* Leaflet Map Div */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Map Navigation Controls */}
      <div className="absolute top-4 left-4 z-[400] flex flex-col gap-1.5">
        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomIn()}
          className="w-8 h-8 rounded-sm bg-parchment/90 hover:bg-parchment border border-stone hover:border-brass/50 text-linen flex items-center justify-center transition-colors shadow-sm"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-4 h-4 text-brass" />
        </button>

        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomOut()}
          className="w-8 h-8 rounded-sm bg-parchment/90 hover:bg-parchment border border-stone hover:border-brass/50 text-linen flex items-center justify-center transition-colors shadow-sm"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-4 h-4 text-brass" />
        </button>

        <button
          type="button"
          onClick={handleResetView}
          className="w-8 h-8 rounded-sm bg-parchment/90 hover:bg-parchment border border-stone hover:border-brass/50 text-linen flex items-center justify-center transition-colors shadow-sm"
          title="Reset World View"
          aria-label="Reset world view"
        >
          <RotateCcw className="w-3.5 h-3.5 text-brass" />
        </button>
      </div>

      {/* Dynamic Hover Status Pill (Top Right) */}
      {hoveredCountryInfo && (
        <div className="absolute top-4 right-4 z-[400] hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-sm bg-parchment/90 backdrop-blur-md border border-stone shadow-editorial font-serif text-xs animate-fadeIn">
          <span
            className={`w-2 h-2 rounded-full ${
              hoveredCountryInfo.isSupported
                ? "bg-brass shadow-[0_0_6px_#D1A75C]"
                : "bg-linen-muted"
            }`}
          />
          <span className="font-display font-bold text-linen">
            {hoveredCountryInfo.name} ({hoveredCountryInfo.code})
          </span>
          <span className="text-linen-muted font-mono text-[10px]">
            {hoveredCountryInfo.isSupported
              ? "20 Verified Records"
              : "Stories coming soon"}
          </span>
        </div>
      )}

      {/* Map Legend (Bottom Left) */}
      <MapLegend />

      {/* Country Information Drawer (Slide-In on selection) */}
      <CountryInformationDrawer
        countryCode={activeCountry}
        onClose={() => setActiveCountry(null)}
      />
    </div>
  );
}

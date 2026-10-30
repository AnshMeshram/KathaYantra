"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import L from "leaflet";
import { SUPPORTED_COUNTRIES, isCountrySupported, UNSUPPORTED_COUNTRY_NOTICE } from "@/constants/countries";
import { MapLegend } from "@/components/map/map-legend";
import { CountryInformationDrawer } from "@/components/map/country-information-drawer";
import { RotateCcw, ZoomIn, ZoomOut, Compass } from "lucide-react";

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
      // Pan to country if map ready
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

    // Create map centered on global view
    const map = L.map(mapContainerRef.current, {
      center: [20.0, 10.0],
      zoom: 2.5,
      minZoom: 1.8,
      maxZoom: 9,
      zoomControl: false, // Custom gothic controls
      attributionControl: true,
      maxBounds: [
        [-85, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 0.8,
    });

    // Dark cartographic background / ocean color
    map.attributionControl.setPrefix(
      '<span class="font-mono text-[9px] text-ash/60">Natural Earth &copy; KathaYantra Cartography</span>'
    );

    mapInstanceRef.current = map;
    markersLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Render GeoJSON and markers when geoData or activeCountry changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !geoData) return;

    // Clean existing layers
    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }
    if (markersLayerRef.current) {
      markersLayerRef.current.clearLayers();
    }

    // Polygon Style Evaluator
    const styleFeature = (feature: any) => {
      const props = feature.properties || {};
      const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
      const isSupported = isCountrySupported(code);
      const isSelected = activeCountry?.toUpperCase() === code;

      if (isSelected) {
        return {
          fillColor: "#361F2C",
          fillOpacity: 0.9,
          color: "#FF713B", // Ember Orange
          weight: 2.5,
          dashArray: "",
        };
      }

      if (isSupported) {
        return {
          fillColor: "#251820", // Charcoal Wine
          fillOpacity: 0.8,
          color: "#C78B42", // Antique Gold
          weight: 1.6,
          dashArray: "",
        };
      }

      // Inactive / Unsupported Country
      return {
        fillColor: "#1C1920",
        fillOpacity: 0.65,
        color: "#37303A", // Muted Grey
        weight: 0.8,
        dashArray: "2, 3",
      };
    };

    // Attach Interactions to Polygons
    const onEachFeature = (feature: any, layer: L.Layer) => {
      const props = feature.properties || {};
      const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
      const name = props.name || props.NAME || code;
      const isSupported = isCountrySupported(code);

      // Tooltip HTML formatting
      let tooltipContent = "";
      if (isSupported) {
        const meta = SUPPORTED_COUNTRIES[code];
        tooltipContent = `
          <div style="font-family: serif; padding: 6px; min-width: 170px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <strong style="color: #C78B42; font-size: 14px; text-transform: uppercase;">${name}</strong>
              <span style="font-family: monospace; font-size: 10px; background: #09090D; padding: 1px 4px; border: 1px solid #C78B42; border-radius: 2px; color: #C78B42;">${code}</span>
            </div>
            <div style="font-size: 11px; color: #E9DCC5; margin-bottom: 6px;">
              <div>• Folklore Tales: <strong style="color: #FF713B;">10</strong></div>
              <div>• Urban Legends: <strong style="color: #E52D35;">10</strong></div>
              <div>• Total Records: <strong style="color: #C78B42;">20</strong></div>
            </div>
            <div style="font-size: 10px; color: #A59AA0; border-top: 1px solid #251820; padding-top: 4px;">
              Tradition: ${meta?.primary_folklore_creature || "Documented Folklore"}
            </div>
          </div>
        `;
      } else {
        tooltipContent = `
          <div style="font-family: serif; padding: 6px; max-width: 200px;">
            <div style="color: #E9DCC5; font-size: 13px; font-weight: bold; margin-bottom: 2px;">${name}</div>
            <div style="display: inline-block; font-family: monospace; font-size: 9px; background: #251820; color: #C78B42; padding: 2px 5px; border-radius: 2px; text-transform: uppercase; margin-bottom: 4px;">
              ${UNSUPPORTED_COUNTRY_NOTICE.badge}
            </div>
            <div style="font-size: 10px; color: #A59AA0; line-height: 1.3;">
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

      // Events
      layer.on({
        mouseover: (e) => {
          const target = e.target;
          target.setStyle({
            weight: isSupported ? 2.8 : 1.4,
            color: isSupported ? "#FF713B" : "#A59AA0",
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

    // Render Red Archive Presence Markers for Supported Countries
    if (markersLayerRef.current) {
      Object.entries(SUPPORTED_COUNTRIES).forEach(([code, meta]) => {
        const marker = L.circleMarker([meta.lat, meta.lng], {
          radius: 4.5,
          fillColor: "#E52D35", // Blood Red
          color: "#E9DCC5",
          weight: 1,
          opacity: 0.9,
          fillOpacity: 1,
        });

        marker.bindTooltip(
          `<div style="font-family: monospace; font-size: 10px; color: #E9DCC5;"><strong>${meta.name} Archive</strong> (20 stories)</div>`,
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
    <div className="relative w-full h-[75vh] md:h-[82vh] rounded-xl overflow-hidden border border-charcoal-wine shadow-gothic-card bg-[#101016]">
      {/* Loading Overlay */}
      {isLoadingGeo && (
        <div className="absolute inset-0 z-[500] bg-obsidian/90 flex flex-col items-center justify-center gap-3">
          <div className="w-9 h-9 rounded-full border-2 border-gold/30 border-t-gold animate-spin" />
          <span className="font-gothic text-base text-gold tracking-widest uppercase">
            Illuminating World Cartography...
          </span>
        </div>
      )}

      {/* Leaflet Map Div */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Custom Gothic Map Controls */}
      <div className="absolute top-4 left-4 z-[400] flex flex-col gap-2">
        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomIn()}
          className="w-8 h-8 rounded bg-plum/90 hover:bg-plum border border-charcoal-wine hover:border-gold/50 text-ivory flex items-center justify-center transition-colors shadow-md"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-4 h-4 text-gold" />
        </button>

        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomOut()}
          className="w-8 h-8 rounded bg-plum/90 hover:bg-plum border border-charcoal-wine hover:border-gold/50 text-ivory flex items-center justify-center transition-colors shadow-md"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-4 h-4 text-gold" />
        </button>

        <button
          type="button"
          onClick={handleResetView}
          className="w-8 h-8 rounded bg-plum/90 hover:bg-plum border border-charcoal-wine hover:border-gold/50 text-ivory flex items-center justify-center transition-colors shadow-md"
          title="Reset World View"
          aria-label="Reset world view"
        >
          <RotateCcw className="w-3.5 h-3.5 text-gold" />
        </button>
      </div>

      {/* Dynamic Hover Status Pill (Top Right) */}
      {hoveredCountryInfo && (
        <div className="absolute top-4 right-4 z-[400] hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-plum/90 backdrop-blur-md border border-charcoal-wine shadow-md font-serif text-xs animate-fadeIn">
          <span
            className={`w-2 h-2 rounded-full ${
              hoveredCountryInfo.isSupported
                ? "bg-gold shadow-[0_0_8px_#C78B42]"
                : "bg-ash"
            }`}
          />
          <span className="font-gothic font-bold text-ivory">
            {hoveredCountryInfo.name} ({hoveredCountryInfo.code})
          </span>
          <span className="text-ash font-mono text-[10px]">
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


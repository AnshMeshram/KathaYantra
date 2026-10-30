"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { SUPPORTED_COUNTRIES, isCountrySupported, UNSUPPORTED_COUNTRY_NOTICE } from "@/constants/countries";
import { MapLegend } from "@/components/map/map-legend";
import { CountryInformationDrawer } from "@/components/map/country-information-drawer";
import { RotateCcw, ZoomIn, ZoomOut, ArrowRight } from "lucide-react";
import Link from "next/link";
import { getCountryRoute } from "@/lib/routes";

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
          duration: 1.0,
        });
      }
    }
  }, [selectedCountry]);

  // Initialize Leaflet Map with correct initial framing
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [24.0, 15.0],
      zoom: 2.1,
      minZoom: 1.8,
      maxZoom: 8,
      zoomControl: false,
      attributionControl: true,
      maxBounds: [
        [-80, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 0.85,
    });

    // Guard against mid-event or unmount teardown where _mapPane is accessed
    const origGetMapPanePos = (map as any)._getMapPanePos;
    (map as any)._getMapPanePos = function () {
      if (!this._mapPane) return new L.Point(0, 0);
      return origGetMapPanePos ? origGetMapPanePos.call(this) : new L.Point(0, 0);
    };

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    // Handle container resize cleanly
    const handleResize = () => {
      if (mapInstanceRef.current && (mapInstanceRef.current as any)._mapPane) {
        mapInstanceRef.current.invalidateSize();
      }
    };
    window.addEventListener("resize", handleResize);

    const timer = setTimeout(() => {
      if (mapInstanceRef.current && (mapInstanceRef.current as any)._mapPane) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 200);

    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", handleResize);
      try {
        map.stop();
        map.remove();
      } catch {
        // ignore
      }
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

    // Polygon Style Evaluator using the exact 5-color Japanese editorial palette
    const styleFeature = (feature: any) => {
      const props = feature.properties || {};
      const code = (props.iso_a2 || props.ISO_A2 || "").toUpperCase();
      const isSupported = isCountrySupported(code);
      const isSelected = activeCountry?.toUpperCase() === code;

      if (isSelected) {
        return {
          fillColor: "#FECD6D", // Lunar Yellow
          fillOpacity: 0.75,
          color: "#970A12", // Chinese Red
          weight: 2.4,
          dashArray: "",
        };
      }

      if (isSupported) {
        return {
          fillColor: "#EDE2D0",
          fillOpacity: 0.85,
          color: "#70191D", // Burgundy
          weight: 1.5,
          dashArray: "",
        };
      }

      // Unsupported Country
      return {
        fillColor: "#FAF4EC",
        fillOpacity: 0.6,
        color: "#D8C7B0", // Soft Parchment Border
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
              <strong style="color: #70191D; font-size: 14px; text-transform: uppercase;">${name}</strong>
              <span style="font-family: monospace; font-size: 10px; background: #970A12; padding: 1px 4px; border-radius: 2px; color: #FAF4EC;">${code}</span>
            </div>
            <div style="font-size: 11px; color: #251D1B; margin-bottom: 6px;">
              <div>• Folklore Tales: <strong style="color: #70191D;">10</strong></div>
              <div>• Urban Legends: <strong style="color: #5686BB;">10</strong></div>
              <div>• Total Records: <strong style="color: #970A12;">20</strong></div>
            </div>
            <div style="font-size: 10px; color: #766B62; border-top: 1px solid #D8C7B0; padding-top: 4px;">
              Tradition: ${meta?.primary_folklore_creature || "Documented Folklore"}
            </div>
          </div>
        `;
      } else {
        tooltipContent = `
          <div style="font-family: serif; padding: 6px; max-width: 200px;">
            <div style="color: #251D1B; font-size: 13px; font-weight: bold; margin-bottom: 2px;">${name}</div>
            <div style="display: inline-block; font-family: monospace; font-size: 9px; background: #D1601F; color: #FAF4EC; padding: 2px 5px; border-radius: 2px; text-transform: uppercase; margin-bottom: 4px;">
              ${UNSUPPORTED_COUNTRY_NOTICE.badge}
            </div>
            <div style="font-size: 10px; color: #766B62; line-height: 1.3;">
              ${UNSUPPORTED_COUNTRY_NOTICE.message}
            </div>
          </div>
        `;
      }

      layer.bindTooltip(tooltipContent, {
        sticky: true,
        direction: "auto",
        className: "custom-gothic-tooltip",
        opacity: 0.98,
      });

      layer.on({
        mouseover: (e) => {
          const target = e.target;
          target.setStyle({
            weight: isSupported ? 2.5 : 1.2,
            color: isSupported ? "#970A12" : "#766B62",
            fillColor: isSupported ? "#FECD6D" : "#FAF4EC",
            fillOpacity: isSupported ? 0.85 : 0.7,
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

    // Render Chinese Red Hanko-Style Presence Markers for Supported Countries
    if (markersLayerRef.current) {
      Object.entries(SUPPORTED_COUNTRIES).forEach(([code, meta]) => {
        const marker = L.circleMarker([meta.lat, meta.lng], {
          radius: 4.5,
          fillColor: "#970A12", // Chinese Red
          color: "#FAF4EC",
          weight: 1.5,
          opacity: 1,
          fillOpacity: 1,
        });

        marker.bindTooltip(
          `<div style="font-family: monospace; font-size: 10px; color: #251D1B;"><strong>${meta.name} Archive</strong> (20 stories)</div>`,
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
    if (mapInstanceRef.current && (mapInstanceRef.current as any)._mapPane) {
      mapInstanceRef.current.flyTo([24.0, 15.0], 2.1, { duration: 1.0 });
    }
  };

  return (
    <div className="relative w-full h-[75vh] md:h-[84vh] rounded-sm overflow-hidden border border-parchment-border shadow-panel bg-[#E8DDCB]">
      {/* Loading Overlay */}
      {isLoadingGeo && (
        <div className="absolute inset-0 z-[500] bg-parchment/90 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-parchment-border border-t-chinese-red animate-spin" />
          <span className="font-display text-sm text-burgundy tracking-widest uppercase">
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
          onClick={() => {
            if (mapInstanceRef.current && (mapInstanceRef.current as any)._mapPane) {
              mapInstanceRef.current.zoomIn();
            }
          }}
          className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-4 h-4 text-burgundy" />
        </button>

        <button
          type="button"
          onClick={() => {
            if (mapInstanceRef.current && (mapInstanceRef.current as any)._mapPane) {
              mapInstanceRef.current.zoomOut();
            }
          }}
          className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-4 h-4 text-burgundy" />
        </button>

        <button
          type="button"
          onClick={handleResetView}
          className="w-8 h-8 rounded-sm bg-parchment-light/95 hover:bg-parchment-deep border border-parchment-border hover:border-burgundy text-ink flex items-center justify-center transition-colors shadow-sm"
          title="Reset World View"
          aria-label="Reset world view"
        >
          <RotateCcw className="w-3.5 h-3.5 text-burgundy" />
        </button>
      </div>

      {/* Dynamic Hover Status Dropdown (Top Right) */}
      {hoveredCountryInfo && (
        <div
          onMouseEnter={() => {}}
          onMouseLeave={() => setHoveredCountryInfo(null)}
          className="absolute top-4 right-4 z-[400] bg-parchment-light/95 backdrop-blur-md border border-parchment-border shadow-panel p-3.5 rounded-sm w-64 animate-fadeIn text-left"
        >
          <div className="flex items-center justify-between gap-2 border-b border-parchment-border/70 pb-2 mb-2">
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  hoveredCountryInfo.isSupported ? "bg-chinese-red" : "bg-ink-faint"
                }`}
              />
              <h4 className="font-display font-bold text-base text-burgundy uppercase tracking-wide truncate">
                {hoveredCountryInfo.name}
              </h4>
            </div>
            <span className="font-mono text-xs px-1.5 py-0.5 rounded-sm bg-parchment-deep border border-parchment-border text-burgundy font-bold shrink-0">
              {hoveredCountryInfo.code}
            </span>
          </div>

          {hoveredCountryInfo.isSupported ? (
            <div className="space-y-2 text-xs font-serif">
              <div className="flex justify-between items-center text-ink-muted">
                <span>Folklore Tales:</span>
                <strong className="text-burgundy font-mono">10</strong>
              </div>
              <div className="flex justify-between items-center text-ink-muted">
                <span>Urban Legends:</span>
                <strong className="text-cobalt font-mono">10</strong>
              </div>
              <div className="pt-2 border-t border-parchment-border/70">
                <Link
                  href={getCountryRoute(hoveredCountryInfo.code)}
                  className="w-full inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-sm bg-chinese-red hover:bg-chinese-red-dark text-parchment-light font-display text-xs font-bold uppercase tracking-wider transition-colors shadow-seal"
                >
                  <span>Explore {hoveredCountryInfo.name}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-1.5 text-xs font-serif">
              <span className="font-mono text-[9px] px-1.5 py-0.5 rounded-sm bg-satsuma text-parchment-light uppercase tracking-wider font-semibold">
                Stories Coming Soon
              </span>
              <p className="text-ink-muted text-[11px] leading-relaxed pt-1">
                Our archive is still growing. Folklore and urban legends from this country will be available soon.
              </p>
            </div>
          )}
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

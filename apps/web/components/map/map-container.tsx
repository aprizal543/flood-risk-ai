"use client";

import { useRef, useEffect, useCallback, useState, useMemo, memo, type ElementType } from "react";
import { createRoot, type Root } from "react-dom/client";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Plus, Minus, Crosshair, Maximize2, RotateCcw, Trash2, Globe, MapPin } from "lucide-react";
import { MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM, STORAGE_KEYS } from "@/lib/constants";
import { SearchBar } from "@/components/map/search-bar";
import { addPolygonLayer } from "@/components/map/PolygonLayer";
import { attachPolygonHover, syncPolygonStates, featureBounds } from "@/components/map/PolygonInteraction";
import { SOURCE_ID, FILL_LAYER_ID, BORDER_LAYER_ID } from "@/components/map/GeoSource";
import { addLabelsLayer, LABELS_LAYER_ID } from "@/components/map/MapLabels";
import { LayerManager, useLayerVisibility } from "@/components/map/LayerManager";
import { FloodRiskLegend } from "@/components/map/FloodRiskLegend";
import { SpatialStatistics } from "@/components/map/SpatialStatistics";
import { MapStatusBar } from "@/components/map/MapStatusBar";
import { PolygonFilter, usePolygonFilter } from "@/components/map/PolygonFilter";
import { buildRegionPopupHTML } from "@/components/map/RegionPopup";
import { findPolygon } from "@/components/map/PointInPolygon";
import { useGeolocation } from "@/hooks/use-geolocation";
import { useLocalStorage } from "@/hooks/use-local-storage";
import type { HistoryEntry } from "@/hooks/use-search-history";
import type { Feature } from "geojson";

interface MapContainerProps {
  wilayah: string | null;
  fri?: number;
  latitude?: number;
  longitude?: number;
  history: HistoryEntry[];
  onSearch: (wilayah: string) => void;
  onMarkerClick: (wilayah: string) => void;
  onClearHistory: () => void;
  onRemoveCity: (wilayah: string) => void;
}

interface MarkerEntry {
  marker: maplibregl.Marker;
  el: HTMLDivElement;
  root: Root;
}

const RISK_COLORS: Record<string, string> = {
  "Risiko Rendah": "#22c55e",
  "Risiko Sedang": "#f59e0b",
  "Risiko Tinggi": "#ef4444",
};

const BASE_LAYERS: Record<string, { name: string; tiles: string[] }> = {
  streets: { name: "Streets", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"] },
  satellite: { name: "Satelit", tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"] },
};

export const MapContainer = memo(function MapContainer({
  wilayah,
  fri,
  latitude,
  longitude,
  history,
  onSearch,
  onMarkerClick,
  onClearHistory,
  onRemoveCity,
}: MapContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<Map<string, MarkerEntry>>(new Map());
  const popupsRef = useRef<Map<string, maplibregl.Popup>>(new Map());
  const createdRootsRef = useRef<Set<Root>>(new Set());
  const hoverCleanupRef = useRef<(() => void) | null>(null);
  const [activeLayer, setActiveLayer] = useLocalStorage(STORAGE_KEYS.mapLayer, "streets");
  const initialLayerRef = useRef(activeLayer);
  const { locate, loading: geoLoading } = useGeolocation(onSearch);
  const [layerVis, setLayerVis] = useLayerVisibility();
  const [riskFilter, setRiskFilter] = usePolygonFilter();
  const [polygonMap, setPolygonMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    let cancelled = false;

    async function compute() {
      const newMap = new Map<string, string>();
      for (const h of history) {
        const result = await findPolygon(h.latitude, h.longitude);
        if (result) newMap.set(h.wilayah, result.nama);
      }
      if (!cancelled) setPolygonMap(newMap);
    }

    void compute();

    return () => {
      cancelled = true;
    };
  }, [history]);

  const visiblePolygons = useMemo(() => new Set(polygonMap.values()), [polygonMap]);

  const openPopup = useCallback((w: string) => {
    const map = mapRef.current;
    if (!map) return;

    const popup = popupsRef.current.get(w);
    if (popup && !popup.isOpen()) {
      popup.addTo(map);
    }
  }, []);

  const openAllPopups = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    popupsRef.current.forEach((popup) => {
      if (!popup.isOpen()) {
        popup.addTo(map);
      }
    });
  }, []);

  const mountMarker = useCallback((entry: MarkerEntry, color: string, isActive: boolean) => {
    entry.root.render(<MarkerPin color={color} isActive={isActive} visible={layerVis.markers} />);
  }, [layerVis.markers]);

  useEffect(() => {
    const win = window as unknown as Record<string, unknown>;
    win.__regionPopupDetail__ = (w: string) => onMarkerClick(w);
    win.__regionPopupRemove__ = (w: string) => onRemoveCity(w);

    return () => {
      delete win.__regionPopupDetail__;
      delete win.__regionPopupRemove__;
    };
  }, [onMarkerClick, onRemoveCity]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const markerEntries = markersRef.current;
    const roots = createdRootsRef.current;
    const popups = popupsRef.current;

    const tiles = BASE_LAYERS[initialLayerRef.current]?.tiles ?? BASE_LAYERS.streets.tiles;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          basemap: { type: "raster", tiles, tileSize: 256, attribution: "&copy; OpenStreetMap" },
        },
        layers: [{ id: "basemap", type: "raster", source: "basemap" }],
      },
      center: MAP_DEFAULT_CENTER,
      zoom: MAP_DEFAULT_ZOOM,
      attributionControl: false,
    });

    map.addControl(new maplibregl.AttributionControl(), "bottom-right");
    mapRef.current = map;

    map.on("load", () => {
      void addPolygonLayer(map).then(() => {
        addLabelsLayer(map);
        hoverCleanupRef.current = attachPolygonHover(map);
      });
    });

    return () => {
  hoverCleanupRef.current?.();
  hoverCleanupRef.current = null;

  markerEntries.forEach(({ marker }) => {
    marker.remove();
  });

  // Salin dulu semua root
  const rootsToUnmount = Array.from(roots);

  markerEntries.clear();
  roots.clear();

  popups.forEach((popup) => {
    popup.remove();
  });
  popups.clear();

  map.remove();
  mapRef.current = null;

  // Tunda unmount sampai frame berikutnya
  requestAnimationFrame(() => {
    rootsToUnmount.forEach((root) => {
      try {
        root.unmount();
      } catch (error) {
        console.warn("Failed to unmount marker root:", error);
      }
    });
  });
};
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const obs = new ResizeObserver(() => mapRef.current?.resize());
    obs.observe(containerRef.current);

    return () => {
      obs.disconnect();
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const setVis = (id: string, visible: boolean) => {
      if (map.getLayer(id)) {
        map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
      }
    };

    setVis(FILL_LAYER_ID, layerVis.polygons);
    setVis(BORDER_LAYER_ID, layerVis.borders);
    setVis("riau-active-glow", layerVis.polygons);
    setVis(LABELS_LAYER_ID, layerVis.labels);

    markersRef.current.forEach(({ el }) => {
      el.style.display = layerVis.markers ? "" : "none";
    });
  }, [layerVis]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const update = () => {
      const activePolygonNama = wilayah ? polygonMap.get(wilayah) ?? null : null;
      const polygonPredictions = new Map<string, { nama: string; fri: number; risiko: string }>();

      for (const h of history) {
        const pNama = polygonMap.get(h.wilayah);
        if (!pNama) continue;
        if (h.tingkatRisiko === "Risiko Rendah" && !riskFilter.rendah) continue;
        if (h.tingkatRisiko === "Risiko Sedang" && !riskFilter.sedang) continue;
        if (h.tingkatRisiko === "Risiko Tinggi" && !riskFilter.tinggi) continue;

        const existing = polygonPredictions.get(pNama);
        if (!existing || h.fri > existing.fri) {
          polygonPredictions.set(pNama, { nama: pNama, fri: h.fri, risiko: h.tingkatRisiko });
        }
      }

      syncPolygonStates(map, activePolygonNama, [...polygonPredictions.values()], visiblePolygons);
    };

    if (map.isStyleLoaded()) {
      update();
    } else {
      map.once("idle", update);
    }
  }, [wilayah, fri, history, riskFilter, polygonMap, visiblePolygons]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const currentKeys = new Set(history.map((h) => h.wilayah));

    for (const [key, entry] of markersRef.current) {
      if (!currentKeys.has(key)) {
        entry.marker.remove();
        markersRef.current.delete(key);
      }
    }

    for (const [key, popup] of popupsRef.current) {
      if (!currentKeys.has(key)) {
        popup.remove();
        popupsRef.current.delete(key);
      }
    }

    history.forEach((h) => {
      const isActive = h.wilayah === wilayah;
      const color = RISK_COLORS[h.tingkatRisiko] ?? "#64748b";

      const existingPopup = popupsRef.current.get(h.wilayah);
      if (existingPopup) {
        existingPopup.setHTML(buildRegionPopupHTML(h));
      } else {
        const popup = new maplibregl.Popup({
          offset: 20,
          maxWidth: "260px",
          closeButton: true,
          closeOnClick: false,
          className: "region-popup",
        })
          .setLngLat([h.longitude, h.latitude])
          .setHTML(buildRegionPopupHTML(h));

        popupsRef.current.set(h.wilayah, popup);
        if (isActive) popup.addTo(map);
      }

      const existing = markersRef.current.get(h.wilayah);
      if (existing) {
        mountMarker(existing, color, isActive);
        return;
      }

      const el = document.createElement("div");
      const root = createRoot(el);
      createdRootsRef.current.add(root);

      const marker = new maplibregl.Marker({ element: el }).setLngLat([h.longitude, h.latitude]).addTo(map);
      el.addEventListener("click", () => openPopup(h.wilayah));

      const entry = { marker, el, root };
      markersRef.current.set(h.wilayah, entry);
      mountMarker(entry, color, isActive);
    });
  }, [history, wilayah, layerVis.markers, mountMarker, openPopup]);

  useEffect(() => {
    if (!mapRef.current || latitude === undefined || longitude === undefined) return;
    if (!wilayah) return;

    mapRef.current.flyTo({ center: [longitude, latitude], zoom: 12, duration: 1000 });
    const timer = window.setTimeout(() => openPopup(wilayah), 300);

    return () => {
      window.clearTimeout(timer);
    };
  }, [latitude, longitude, wilayah, openPopup]);

  const switchLayer = useCallback((layerId: string) => {
    if (!mapRef.current) return;

    setActiveLayer(layerId);
    const map = mapRef.current;
    const tiles = BASE_LAYERS[layerId]?.tiles ?? BASE_LAYERS.streets.tiles;

    map.removeLayer("basemap");
    map.removeSource("basemap");
    map.addSource("basemap", { type: "raster", tiles, tileSize: 256 });
    const first = map.getStyle().layers?.[0]?.id;
    map.addLayer({ id: "basemap", type: "raster", source: "basemap" }, first);
  }, [setActiveLayer]);

  const zoomToAll = useCallback(() => {
    if (!mapRef.current || history.length === 0) return;

    const map = mapRef.current;
    const bounds = new maplibregl.LngLatBounds();
    history.forEach((h) => bounds.extend([h.longitude, h.latitude]));

    const features = map.querySourceFeatures(SOURCE_ID);
    features.forEach((f) => {
      const fNama = f.properties?.nama as string | undefined;
      if (fNama && visiblePolygons.has(fNama)) {
        bounds.extend(featureBounds(f as unknown as Feature));
      }
    });

    map.fitBounds(bounds, { padding: { top: 80, bottom: 80, left: 80, right: 420 }, duration: 1500, maxZoom: 11 });
    map.once("moveend", () => openAllPopups());
  }, [history, visiblePolygons, openAllPopups]);

  const handleSearchSelect = useCallback((...args: [string, number, number]) => {
    onSearch(args[0]);
  }, [onSearch]);

  const zoomIn = useCallback(() => mapRef.current?.zoomIn(), []);
  const zoomOut = useCallback(() => mapRef.current?.zoomOut(), []);
  const resetView = useCallback(() => {
    mapRef.current?.flyTo({ center: MAP_DEFAULT_CENTER, zoom: MAP_DEFAULT_ZOOM, duration: 1000 });
  }, []);
  const fullscreen = useCallback(() => {
    containerRef.current?.requestFullscreen?.();
  }, []);

  const activeEntry = wilayah ? history.find((h) => h.wilayah === wilayah) : undefined;

  return (
    <div ref={containerRef} className="relative flex-1 h-full min-w-0 rounded-[var(--radius-map)] overflow-hidden border border-[var(--border)] shadow-[var(--shadow-card)]" role="application" aria-label="Peta interaktif">
      <style>{`
        @keyframes marker-pulse{0%,100%{box-shadow:0 0 0 2px currentColor,0 0 8px currentColor}50%{box-shadow:0 0 0 4px currentColor,0 0 16px currentColor}}
        .active-pulse{animation:marker-pulse 2s ease-in-out infinite}
        .region-popup .maplibregl-popup-content{border-radius:var(--radius-popup);padding:14px 16px;box-shadow:var(--shadow-popup);background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);animation:popupIn .2s ease}
        .region-popup .maplibregl-popup-close-button{font-size:18px;padding:2px 8px;color:var(--text-muted);line-height:1}
        .region-popup .maplibregl-popup-close-button:hover{color:var(--text-primary);background:var(--bg-card-hover);border-radius:8px}
        .region-popup .maplibregl-popup-tip{border-top-color:var(--bg-card)}
        @keyframes popupIn{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:scale(1)}}
        .polygon-tooltip .maplibregl-popup-content{border-radius:12px;padding:8px 12px;box-shadow:var(--shadow-card);background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);pointer-events:none}
        .polygon-tooltip .maplibregl-popup-tip{border-top-color:var(--bg-card)}
      `}</style>

      <SearchBar key={wilayah ?? "no-selection"} value={wilayah ?? ""} onSelect={handleSearchSelect} />
      <PolygonFilter value={riskFilter} onChange={setRiskFilter} />
      <SpatialStatistics history={history} />

      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1 rounded-[var(--radius-card)] bg-[var(--bg-card)]/90 backdrop-blur-sm shadow-[var(--shadow-card)] border border-[var(--border)] p-1.5" role="toolbar" aria-label="Kontrol peta">
        <ToolBtn icon={Plus} label="Perbesar" onClick={zoomIn} />
        <ToolBtn icon={Minus} label="Perkecil" onClick={zoomOut} />
        <ToolBtn icon={Crosshair} label="Lokasi saya" onClick={locate} loading={geoLoading} />
        <ToolBtn icon={Globe} label="Tampilkan Semua" onClick={zoomToAll} />
        <ToolBtn icon={Maximize2} label="Layar penuh" onClick={fullscreen} />
        <ToolBtn icon={RotateCcw} label="Reset tampilan" onClick={resetView} />
        <LayerManager value={layerVis} onChange={setLayerVis} />
        {history.length > 1 && <ToolBtn icon={Trash2} label="Bersihkan Riwayat" onClick={onClearHistory} />}
      </div>

      <div className="absolute top-3 right-16 z-10 flex gap-1 rounded-[var(--radius-btn)] bg-[var(--bg-card)]/90 backdrop-blur-sm shadow-[var(--shadow-card)] border border-[var(--border)] p-1">
        {Object.entries(BASE_LAYERS).map(([id, { name }]) => (
          <button
            key={id}
            onClick={() => switchLayer(id)}
            className={`px-2.5 py-1 text-[10px] rounded-[14px] font-medium transition-all ${activeLayer === id ? "bg-[var(--brand-primary)] text-white shadow-[0_0_8px_var(--brand-glow)]" : "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]"}`}
            aria-pressed={activeLayer === id}
          >
            {name}
          </button>
        ))}
      </div>

      <FloodRiskLegend history={history} />
      <MapStatusBar wilayah={wilayah} entry={activeEntry} />
    </div>
  );
});

function ToolBtn({ icon: Icon, label, onClick, loading }: { icon: ElementType; label: string; onClick: () => void; loading?: boolean }) {
  return (
    <button
      title={label}
      aria-label={label}
      onClick={onClick}
      disabled={loading}
      className="flex items-center justify-center h-8 w-8 rounded-xl text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-all disabled:opacity-50"
    >
      <Icon className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
    </button>
  );
}

function MarkerPin({ color, isActive, visible }: { color: string; isActive: boolean; visible: boolean }) {
  const size = isActive ? 18 : 12;
  const containerSize = isActive ? 30 : 22;

  return (
    <div
      className={isActive ? "active-pulse" : ""}
      style={{
        width: containerSize,
        height: containerSize,
        display: visible ? "flex" : "none",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
        transition: "all 300ms ease",
        zIndex: isActive ? 10 : 1,
        color,
        filter: isActive ? `drop-shadow(0 0 10px ${color}80)` : `drop-shadow(0 0 6px ${color}40)`,
      }}
      aria-hidden="true"
    >
      <MapPin
        className="shrink-0"
        fill={color}
        stroke="white"
        strokeWidth={2.25}
        style={{ width: size, height: size }}
      />
    </div>
  );
}

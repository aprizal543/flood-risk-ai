import type maplibregl from "maplibre-gl";
import { loadGeoJSON, geoSourceSpec, SOURCE_ID, FILL_LAYER_ID, BORDER_LAYER_ID } from "./GeoSource";

/**
 * Add polygon source + layers. Supports hidden/predicted/active feature-states.
 * Hidden polygons render with 0 opacity (invisible).
 */
export async function addPolygonLayer(map: maplibregl.Map) {
  const data = await loadGeoJSON();
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID, geoSourceSpec(data));

  // Fill layer
  map.addLayer({
    id: FILL_LAYER_ID,
    type: "fill",
    source: SOURCE_ID,
    paint: {
      "fill-color": [
        "case",
        ["boolean", ["feature-state", "hidden"], false], "transparent",
        ["boolean", ["feature-state", "active"], false], ["coalesce", ["feature-state", "color"], "#94a3b8"],
        ["boolean", ["feature-state", "predicted"], false], ["coalesce", ["feature-state", "color"], "#94a3b8"],
        "#e2e8f0",
      ],
      "fill-opacity": [
        "case",
        ["boolean", ["feature-state", "hidden"], false], 0,
        ["boolean", ["feature-state", "active"], false], 0.50,
        ["boolean", ["feature-state", "hover"], false], 0.25,
        ["boolean", ["feature-state", "predicted"], false], 0.30,
        0,
      ],
      "fill-opacity-transition": { duration: 300 },
    },
  });

  // Border layer
  map.addLayer({
    id: BORDER_LAYER_ID,
    type: "line",
    source: SOURCE_ID,
    paint: {
      "line-color": [
        "case",
        ["boolean", ["feature-state", "hidden"], false], "transparent",
        ["boolean", ["feature-state", "active"], false], ["coalesce", ["feature-state", "color"], "#64748b"],
        ["boolean", ["feature-state", "predicted"], false], ["coalesce", ["feature-state", "color"], "#64748b"],
        ["boolean", ["feature-state", "hover"], false], "#94a3b8",
        "#cbd5e1",
      ],
      "line-width": [
        "case",
        ["boolean", ["feature-state", "hidden"], false], 0,
        ["boolean", ["feature-state", "active"], false], 4,
        ["boolean", ["feature-state", "hover"], false], 2.5,
        ["boolean", ["feature-state", "predicted"], false], 2,
        0,
      ],
      "line-opacity": [
        "case",
        ["boolean", ["feature-state", "hidden"], false], 0,
        1,
      ],
      "line-opacity-transition": { duration: 300 },
    },
  });

  // Active glow
  map.addLayer({
    id: "riau-active-glow",
    type: "line",
    source: SOURCE_ID,
    paint: {
      "line-color": "#ffffff",
      "line-width": ["case", ["boolean", ["feature-state", "active"], false], 7, 0],
      "line-opacity": ["case", ["boolean", ["feature-state", "active"], false], 0.6, 0],
      "line-blur": 3,
      "line-opacity-transition": { duration: 300 },
    },
  }, FILL_LAYER_ID);
}

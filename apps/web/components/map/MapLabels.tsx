import type maplibregl from "maplibre-gl";
import { SOURCE_ID } from "./GeoSource";

export const LABELS_LAYER_ID = "riau-labels";

/** Add a symbol layer for region labels with zoom-dependent visibility */
export function addLabelsLayer(map: maplibregl.Map) {
  if (map.getLayer(LABELS_LAYER_ID)) return;

  map.addLayer({
    id: LABELS_LAYER_ID,
    type: "symbol",
    source: SOURCE_ID,
    layout: {
      "text-field": [
        "concat",
        ["case",
          ["==", ["get", "tipe"], "Kota"], "Kota ",
          "Kab. ",
        ],
        ["get", "nama"],
      ],
      // Show simplified name
      "text-size": ["interpolate", ["linear"], ["zoom"], 7, 9, 10, 11, 12, 13],
      "text-anchor": "center",
      "text-allow-overlap": false,
      "text-ignore-placement": false,
      "text-optional": true,
    },
    paint: {
      "text-color": "#334155",
      "text-halo-color": "#ffffff",
      "text-halo-width": 1.5,
      "text-opacity": ["interpolate", ["linear"], ["zoom"], 7, 0, 8.5, 1],
    },
    minzoom: 7.5,
  });
}

// Override layout to show canonical names (strip prefix from nama)
// Actually let's use a simpler expression:
// The nama field already has "Kabupaten X" or "Kota X", we want just "X"
export function updateLabelsLayout(map: maplibregl.Map) {
  if (!map.getLayer(LABELS_LAYER_ID)) return;
  map.setLayoutProperty(LABELS_LAYER_ID, "text-field", [
    "case",
    ["==", ["get", "tipe"], "Kota"],
    ["concat", ["get", "tipe"], " ", ["slice", ["get", "nama"], 5]],
    // For Kabupaten, strip "Kabupaten " prefix (10 chars)
    ["slice", ["get", "nama"], 10],
  ]);
}

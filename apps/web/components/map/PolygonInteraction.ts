import maplibregl from "maplibre-gl";
import { SOURCE_ID, FILL_LAYER_ID } from "./GeoSource";
import { REALTIME_LABELS } from "@/lib/realtime-presentation";

/** FRI → hex color */
export function friColor(fri: number): string {
  if (fri <= 33) return "#22c55e";
  if (fri <= 66) return "#f59e0b";
  return "#ef4444";
}

/** Compute bounding box of a GeoJSON feature's geometry */
export function featureBounds(feature: GeoJSON.Feature): maplibregl.LngLatBounds {
  const bounds = new maplibregl.LngLatBounds();
  const extract = (coords: unknown) => {
    if (typeof (coords as number[])[0] === "number") {
      bounds.extend(coords as [number, number]);
    } else {
      for (const c of coords as unknown[]) extract(c);
    }
  };
  extract((feature.geometry as GeoJSON.Polygon).coordinates);
  return bounds;
}

/**
 * Attach hover-only interaction to the polygon layer (no click).
 * Tooltip shows region name + cached FRI if available.
 * Returns a cleanup function.
 */
export function attachPolygonHover(map: maplibregl.Map) {
  let hoveredId: number | null = null;
  const tooltip = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
    className: "polygon-tooltip",
    offset: 10,
  });

  const onMouseMove = (e: maplibregl.MapLayerMouseEvent) => {
    if (!e.features?.length) return;
    map.getCanvas().style.cursor = "pointer";
    const feat = e.features[0];
    const id = feat.id as number;

    if (hoveredId !== null && hoveredId !== id) {
      map.setFeatureState({ source: SOURCE_ID, id: hoveredId }, { hover: false });
    }
    hoveredId = id;
    map.setFeatureState({ source: SOURCE_ID, id }, { hover: true });

    const nama = (feat.properties?.nama as string) ?? "";
    const state = map.getFeatureState({ source: SOURCE_ID, id });
    const fri = state.fri as number | undefined;
    const risiko = state.risiko as string | undefined;

    let html = `<div style="font-size:11px;line-height:1.5"><strong>${nama.replace("Kabupaten ", "").replace("Kota ", "")}</strong>`;
    if (fri != null) {
      const color = friColor(fri);
      html += `<br/><span style="color:${color};font-weight:600">${REALTIME_LABELS.fri} ${fri.toFixed(1)}</span>`;
      if (risiko) html += `<br/><span style="color:#64748b">${risiko}</span>`;
    }
    html += "</div>";
    tooltip.setLngLat(e.lngLat).setHTML(html).addTo(map);
  };

  const onMouseLeave = () => {
    map.getCanvas().style.cursor = "";
    if (hoveredId !== null) {
      map.setFeatureState({ source: SOURCE_ID, id: hoveredId }, { hover: false });
      hoveredId = null;
    }
    tooltip.remove();
  };

  map.on("mousemove", FILL_LAYER_ID, onMouseMove);
  map.on("mouseleave", FILL_LAYER_ID, onMouseLeave);

  return () => {
    map.off("mousemove", FILL_LAYER_ID, onMouseMove);
    map.off("mouseleave", FILL_LAYER_ID, onMouseLeave);
    tooltip.remove();
  };
}

interface PolygonState {
  nama: string;
  fri: number;
  risiko: string;
}

/**
 * Sync polygon feature-states. Only polygons with predictions are visible/colored.
 * activeNama gets `active: true`, others get `predicted: true`.
 */
export function syncPolygonStates(
  map: maplibregl.Map,
  activeNama: string | null,
  predictions: PolygonState[],
  visiblePolygons: Set<string>,
) {
  if (!map.getSource(SOURCE_ID)) return;
  map.removeFeatureState({ source: SOURCE_ID });

  const features = map.querySourceFeatures(SOURCE_ID);
  const predMap = new Map(predictions.map((p) => [p.nama, p]));

  for (const f of features) {
    const fNama = f.properties?.nama as string | undefined;
    if (!fNama || f.id == null) continue;

    const visible = visiblePolygons.has(fNama);
    const pred = predMap.get(fNama);
    const isActive = fNama === activeNama;

    if (!visible) {
      map.setFeatureState({ source: SOURCE_ID, id: f.id as number }, { hidden: true });
    } else if (isActive && pred) {
      map.setFeatureState({ source: SOURCE_ID, id: f.id as number }, {
        active: true, color: friColor(pred.fri), fri: pred.fri, risiko: pred.risiko,
      });
    } else if (pred) {
      map.setFeatureState({ source: SOURCE_ID, id: f.id as number }, {
        predicted: true, color: friColor(pred.fri), fri: pred.fri, risiko: pred.risiko,
      });
    } else {
      map.setFeatureState({ source: SOURCE_ID, id: f.id as number }, { hidden: true });
    }
  }
}

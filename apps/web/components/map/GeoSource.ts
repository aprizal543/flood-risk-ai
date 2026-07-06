import type { GeoJSONSourceSpecification } from "maplibre-gl";

const GEOJSON_URL = "/geo/riau/riau_adm2.geojson";

let cache: GeoJSON.FeatureCollection | null = null;

export async function loadGeoJSON(): Promise<GeoJSON.FeatureCollection> {
  if (cache) return cache;
  const res = await fetch(GEOJSON_URL);
  cache = (await res.json()) as GeoJSON.FeatureCollection;
  return cache;
}

export const SOURCE_ID = "riau-adm2";

export function geoSourceSpec(data: GeoJSON.FeatureCollection): GeoJSONSourceSpecification {
  return { type: "geojson", data, generateId: true };
}

export const FILL_LAYER_ID = "riau-fill";
export const BORDER_LAYER_ID = "riau-border";
export const FILL_HOVER_LAYER_ID = "riau-fill-hover";

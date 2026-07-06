import { loadGeoJSON } from "./GeoSource";

export interface PIPResult {
  nama: string;       // full GeoJSON nama e.g. "Kabupaten Kampar"
  canonical: string;  // stripped e.g. "Kampar"
  featureId: number;
}

let cachedFeatures: GeoJSON.Feature[] | null = null;

async function getFeatures(): Promise<GeoJSON.Feature[]> {
  if (cachedFeatures) return cachedFeatures;
  const data = await loadGeoJSON();
  cachedFeatures = data.features;
  return cachedFeatures;
}

/** Ray-casting point-in-polygon for a single ring */
function pointInRing(lng: number, lat: number, ring: number[][]): boolean {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1];
    const xj = ring[j][0], yj = ring[j][1];
    if ((yi > lat) !== (yj > lat) && lng < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

/** Check if point is inside a Polygon or MultiPolygon geometry */
function pointInGeometry(lng: number, lat: number, geometry: GeoJSON.Geometry): boolean {
  if (geometry.type === "Polygon") {
    const coords = (geometry as GeoJSON.Polygon).coordinates;
    // Must be inside outer ring and outside holes
    if (!pointInRing(lng, lat, coords[0])) return false;
    for (let i = 1; i < coords.length; i++) {
      if (pointInRing(lng, lat, coords[i])) return false;
    }
    return true;
  }
  if (geometry.type === "MultiPolygon") {
    const polys = (geometry as GeoJSON.MultiPolygon).coordinates;
    for (const poly of polys) {
      if (!pointInRing(lng, lat, poly[0])) continue;
      let inHole = false;
      for (let i = 1; i < poly.length; i++) {
        if (pointInRing(lng, lat, poly[i])) { inHole = true; break; }
      }
      if (!inHole) return true;
    }
    return false;
  }
  return false;
}

/**
 * Determine which Riau ADM2 polygon contains the given lat/lng.
 * Returns null if point is outside all polygons.
 */
export async function findPolygon(lat: number, lng: number): Promise<PIPResult | null> {
  const features = await getFeatures();
  for (let i = 0; i < features.length; i++) {
    const f = features[i];
    if (pointInGeometry(lng, lat, f.geometry!)) {
      const nama = (f.properties?.nama as string) ?? "";
      const canonical = nama.replace(/^Kota\s+/i, "").replace(/^Kabupaten\s+/i, "");
      return { nama, canonical, featureId: i };
    }
  }
  return null;
}

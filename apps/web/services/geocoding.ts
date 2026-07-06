import axios from "axios";

const GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search";

export interface GeoResult {
  name: string;
  displayName: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string;
}

interface RawResult {
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string;
  country_code?: string;
}

/** Strip Indonesian administrative prefixes to get the place name only */
function stripAdminPrefix(name: string): string {
  return name.replace(/^Kota\s+/i, "").replace(/^Kabupaten\s+/i, "").trim();
}

/**
 * Search Open-Meteo Geocoding with smart Indonesia/Riau prioritization.
 *
 * Rules:
 * 1. Prefer country == Indonesia
 * 2. Among Indonesian results, prioritize admin1 == Riau
 * 3. If a Riau result exists, auto-select it (return only that)
 * 4. If no Riau but Indonesian results exist, return Indonesian ones
 * 5. Never auto-select another country when Indonesian results exist
 */
export async function searchLocations(query: string): Promise<GeoResult[]> {
  if (query.length < 2) return [];
  const { data } = await axios.get(GEOCODING_URL, {
    params: { name: query, count: 10, language: "id" },
  });
  const raw: RawResult[] = data.results ?? [];
  if (raw.length === 0) return [];

  const indonesian = raw.filter((r) => r.country === "Indonesia" || r.country_code === "ID");
  const riau = indonesian.filter((r) => r.admin1 === "Riau" || r.admin1 === "Riau Islands");

  // If Riau result exists, return only Riau results (auto-select)
  let selected: RawResult[];
  if (riau.length > 0) {
    selected = riau.slice(0, 5);
  } else if (indonesian.length > 0) {
    selected = indonesian.slice(0, 5);
  } else {
    selected = raw.slice(0, 5);
  }

  return selected.map((r) => ({
    name: stripAdminPrefix(r.name),
    displayName: [stripAdminPrefix(r.name), r.admin1, r.country].filter(Boolean).join(", "),
    latitude: r.latitude,
    longitude: r.longitude,
    country: r.country,
    admin1: r.admin1,
  }));
}

/** Reverse geocode by finding nearest region from local index */
export async function reverseGeocode(lat: number, lng: number): Promise<string> {
  const { loadSearchIndex } = await import("@/components/map/SearchIndex");
  const index = await loadSearchIndex();
  let best = "Pekanbaru";
  let bestDist = Infinity;
  for (const entry of index) {
    const dx = entry.centroid[0] - lng;
    const dy = entry.centroid[1] - lat;
    const dist = dx * dx + dy * dy;
    if (dist < bestDist) { bestDist = dist; best = entry.canonical; }
  }
  return best;
}

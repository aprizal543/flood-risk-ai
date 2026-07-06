export interface SearchEntry {
  nama: string;
  canonical: string;
  tipe: string;
  kode: string;
  centroid: [number, number];
  aliases: string[];
}

let cache: SearchEntry[] | null = null;

export async function loadSearchIndex(): Promise<SearchEntry[]> {
  if (cache) return cache;
  const res = await fetch("/geo/riau/search_index.json");
  cache = (await res.json()) as SearchEntry[];
  return cache;
}

/** Fuzzy search: matches nama, canonical, or any alias (case-insensitive substring) */
export function fuzzySearch(entries: SearchEntry[], query: string, max = 5): SearchEntry[] {
  if (!query || query.length < 2) return [];
  const q = query.toLowerCase();
  return entries
    .filter((e) =>
      e.nama.toLowerCase().includes(q) ||
      e.canonical.toLowerCase().includes(q) ||
      e.aliases.some((a) => a.includes(q))
    )
    .slice(0, max);
}

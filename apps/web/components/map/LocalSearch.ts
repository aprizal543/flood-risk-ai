"use client";

import { useCallback, useRef, useState } from "react";
import { loadSearchIndex, fuzzySearch, type SearchEntry } from "./SearchIndex";

/**
 * Hook for debounced local search. Call `search(query)` on input change.
 * Results update after the debounce delay.
 */
export function useLocalSearch(delay = 300) {
  const [results, setResults] = useState<SearchEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const indexRef = useRef<SearchEntry[] | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const search = useCallback((query: string) => {
    clearTimeout(timerRef.current);
    if (!query || query.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    timerRef.current = setTimeout(async () => {
      if (!indexRef.current) indexRef.current = await loadSearchIndex();
      setResults(fuzzySearch(indexRef.current, query, 5));
      setLoading(false);
    }, delay);
  }, [delay]);

  return { results, loading, search };
}

"use client";

import { useCallback } from "react";
import { useLocalStorage } from "@/hooks/use-local-storage";

const STORAGE_KEY = "floodrisk_search_history";
const MAX_HISTORY = 20;

export interface HistoryEntry {
  wilayah: string;
  latitude: number;
  longitude: number;
  fri: number;
  tingkatRisiko: string;
  timestamp: string;
  rr?: number;
  rain7?: number;
  rh_avg?: number;
  tavg?: number;
  tmax?: number;
  tmin?: number;
}

export function useSearchHistory() {
  const [history, setHistory] = useLocalStorage<HistoryEntry[]>(STORAGE_KEY, []);

  const upsert = useCallback((entry: HistoryEntry) => {
    setHistory((prev) => {
      const filtered = prev.filter((h) => h.wilayah !== entry.wilayah);
      return [entry, ...filtered].slice(0, MAX_HISTORY);
    });
  }, [setHistory]);

  const remove = useCallback((wilayah: string) => {
    setHistory((prev) => prev.filter((h) => h.wilayah !== wilayah));
  }, [setHistory]);

  const clear = useCallback((keepWilayah?: string) => {
    setHistory((prev) => keepWilayah ? prev.filter((h) => h.wilayah === keepWilayah) : []);
  }, [setHistory]);

  return { history, upsert, remove, clear };
}

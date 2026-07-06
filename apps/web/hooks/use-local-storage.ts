"use client";

import { useCallback, useSyncExternalStore } from "react";

function getServerSnapshot<T>(defaultValue: T): () => string {
  const json = JSON.stringify(defaultValue);
  return () => json;
}

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const subscribe = useCallback(
    (onStoreChange: () => void) => {
      const handler = (e: StorageEvent) => {
        if (e.key === key) onStoreChange();
      };
      window.addEventListener("storage", handler);
      return () => window.removeEventListener("storage", handler);
    },
    [key]
  );

  const getSnapshot = useCallback(() => {
    const stored = localStorage.getItem(key);
    return stored ?? JSON.stringify(defaultValue);
  }, [key, defaultValue]);

  const raw = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot(defaultValue));

  let value: T;
  try {
    value = JSON.parse(raw) as T;
  } catch {
    value = defaultValue;
  }

  const set = useCallback(
    (newValue: T | ((prev: T) => T)) => {
      const current = (() => {
        const stored = localStorage.getItem(key);
        if (stored === null) return defaultValue;
        try { return JSON.parse(stored) as T; } catch { return defaultValue; }
      })();
      const resolved = typeof newValue === "function"
        ? (newValue as (prev: T) => T)(current)
        : newValue;
      localStorage.setItem(key, JSON.stringify(resolved));
      // Trigger re-render by dispatching storage event on same window
      window.dispatchEvent(new StorageEvent("storage", { key }));
    },
    [key, defaultValue]
  );

  return [value, set] as const;
}

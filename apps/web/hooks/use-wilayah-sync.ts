"use client";

import { useCallback, useState } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { STORAGE_KEYS } from "@/lib/constants";

const DEFAULT_WILAYAH = "Pekanbaru";

export function useWilayahSync() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Priority: URL param > localStorage > default
  const getInitialWilayah = useCallback((): string => {
    const fromUrl = searchParams.get("wilayah");
    if (fromUrl) return fromUrl;
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEYS.lastWilayah);
      if (stored) return JSON.parse(stored) as string;
    }
    return DEFAULT_WILAYAH;
  }, [searchParams]);

  const [wilayah, setWilayahState] = useState<string | null>(() => getInitialWilayah());

  const setWilayah = useCallback(
    (wilayah: string) => {
      setWilayahState(wilayah);
      // Update URL
      const params = new URLSearchParams(searchParams.toString());
      params.set("wilayah", wilayah);
      router.push(`${pathname}?${params.toString()}`, { scroll: false });
      // Persist
      localStorage.setItem(STORAGE_KEYS.lastWilayah, JSON.stringify(wilayah));
    },
    [searchParams, router, pathname]
  );

  const clearWilayah = useCallback(() => {
    setWilayahState(null);
    localStorage.removeItem(STORAGE_KEYS.lastWilayah);
    router.push(pathname, { scroll: false });
  }, [router, pathname]);

  return { wilayah, setWilayah, clearWilayah };
}

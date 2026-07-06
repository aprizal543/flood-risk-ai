"use client";

import { useState, useCallback } from "react";
import { reverseGeocode } from "@/services/geocoding";

interface GeolocationState {
  loading: boolean;
  error: string | null;
}

export function useGeolocation(onLocated: (wilayah: string) => void) {
  const [state, setState] = useState<GeolocationState>({ loading: false, error: null });

  const locate = useCallback(() => {
    if (!navigator.geolocation) {
      setState({ loading: false, error: "Geolokasi tidak didukung browser Anda." });
      return;
    }

    setState({ loading: true, error: null });

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const name = await reverseGeocode(pos.coords.latitude, pos.coords.longitude);
          onLocated(name);
          setState({ loading: false, error: null });
        } catch {
          setState({ loading: false, error: "Gagal mendapatkan nama wilayah." });
        }
      },
      (err) => {
        const messages: Record<number, string> = {
          1: "Izin lokasi ditolak. Aktifkan izin lokasi di pengaturan browser.",
          2: "Lokasi tidak tersedia saat ini.",
          3: "Waktu permintaan lokasi habis. Coba lagi.",
        };
        setState({ loading: false, error: messages[err.code] ?? "Gagal mendapatkan lokasi." });
      },
      { enableHighAccuracy: false, timeout: 10000 }
    );
  }, [onLocated]);

  return { locate, ...state };
}

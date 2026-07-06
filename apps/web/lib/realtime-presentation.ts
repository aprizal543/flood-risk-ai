import type { PrediksiRealtimeResponse } from "@/types/api";
import type { HistoryEntry } from "@/hooks/use-search-history";

type RealtimeSource = PrediksiRealtimeResponse | HistoryEntry;

export const REALTIME_LABELS = {
  fri: "Flood Risk Index",
  risk: "Risiko",
  rainfall: "Curah Hujan Hari Ini",
  rain7: "Akumulasi Curah Hujan 7 Hari ke Belakang",
  humidity: "Kelembapan",
  tavg: "Suhu Rata-rata",
  prediction: "Prediksi",
} as const;

function isRealtimeResponse(source: RealtimeSource): source is PrediksiRealtimeResponse {
  return "RR" in source && "Rain7" in source && "RH_avg" in source && "Tavg" in source;
}

export function getRealtimeDisplayValues(source: RealtimeSource) {
  if (isRealtimeResponse(source)) {
    return {
      rainfall: source.RR,
      rain7: source.Rain7,
      humidity: source.RH_avg,
      tavg: source.Tavg,
    };
  }

  return {
    rainfall: source.rr ?? null,
    rain7: source.rain7 ?? null,
    humidity: source.rh_avg ?? null,
    tavg: source.tavg ?? null,
  };
}

export function formatOneDecimal(value: number | null): string {
  return value === null ? "—" : value.toFixed(1);
}

export function formatNoDecimal(value: number | null): string {
  return value === null ? "—" : value.toFixed(0);
}

export function formatMm(value: number | null): string {
  return value === null ? "—" : `${formatNoDecimal(value)} mm`;
}

export function formatPercent(value: number | null): string {
  return value === null ? "—" : `${formatNoDecimal(value)} %`;
}

export function formatCelsius(value: number | null): string {
  return value === null ? "—" : `${formatOneDecimal(value)} °C`;
}

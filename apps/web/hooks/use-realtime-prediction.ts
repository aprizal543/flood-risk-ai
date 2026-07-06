"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchRealtimePrediction } from "@/services/prediction";

export function useRealtimePrediction(wilayah: string, model: string = "rf") {
  return useQuery({
    queryKey: ["prediksi-realtime", wilayah, model],
    queryFn: () => fetchRealtimePrediction(wilayah, model),
    enabled: wilayah.length > 0,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

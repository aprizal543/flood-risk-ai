import axios from "axios";
import type { PrediksiRealtimeResponse } from "@/types/api";
import { getAuthorizationHeaders } from "@/services/authenticated-fetch";
import { getApiBaseUrl } from "@/lib/api-url";

const api = axios.create({
  baseURL: getApiBaseUrl(),
});

export async function fetchRealtimePrediction(
  wilayah: string,
  model: string = "rf",
  topN: number = 5
): Promise<PrediksiRealtimeResponse> {
  const headers = await getAuthorizationHeaders();
  const { data } = await api.get<PrediksiRealtimeResponse>(
    "/api/prediksi/realtime",
    { params: { wilayah, model, top_n: topN }, headers }
  );
  return data;
}

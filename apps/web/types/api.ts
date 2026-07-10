export interface Cuaca {
  tanggal: string;
  rr: number;
  rh_avg: number;
  tmax: number;
  tmin: number;
  latitude: number;
  longitude: number;
}

export interface Rekomendasi {
  komoditas: string;
  komoditas_id: string;
  skor: number;
  tingkat_keyakinan: number;
  tingkat_risiko: string;
  alasan: string[];
  ringkasan: string;
}

export interface Mitigasi {
  prioritas: number;
  kategori: string;
  tindakan: string;
}

export interface KnowledgeCommodityItem {
  komoditas: string;
  komoditas_id: string;
  vulnerability: string;
  max_inundation: string;
  maximum_inundation_duration: string;
  main_impacts: string[];
  damage_symptoms: string[];
  impacts: string[];
  symptoms: string[];
  reason: string;
  source?: string;
}

export interface KnowledgeRecommendation {
  recommended: KnowledgeCommodityItem[];
  alternative: KnowledgeCommodityItem[];
  not_recommended: KnowledgeCommodityItem[];
}

export interface PrediksiRealtimeResponse {
  status: string;
  wilayah: string;
  sumber_data: string;
  forecast_date: string;
  updated_at: string;
  waktu_prediksi: string;
  model: string;
  versi_model: string;
  RR: number;
  Rain7: number;
  RH_avg: number;
  Tavg: number;
  cuaca: Cuaca;
  hari_historis: number;
  fri: number;
  tingkat_risiko: string;
  rekomendasi: Rekomendasi[];
  mitigasi: Mitigasi[];
  knowledge_recommendation?: KnowledgeRecommendation;
}

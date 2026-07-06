import type { PrediksiRealtimeResponse } from "@/types/api";
import { authenticatedFetch } from "@/services/authenticated-fetch";
import { REALTIME_LABELS, formatCelsius, formatMm, formatPercent, getRealtimeDisplayValues } from "@/lib/realtime-presentation";
import { getApiBaseUrl } from "@/lib/api-url";

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

const API_BASE_URL = getApiBaseUrl();
const PROVIDER = (process.env.NEXT_PUBLIC_LLM_PROVIDER ?? "groq");

const SYSTEM_PROMPT = `Kamu adalah FloodRisk AI Decision Support — asisten yang HANYA menjelaskan hasil prediksi risiko banjir untuk hortikultura.

PERAN:
- Jelaskan Flood Risk Index, cuaca, rekomendasi komoditas, dan strategi mitigasi.
- Interpretasikan data prediksi yang diberikan.
- Berikan penjelasan dalam Bahasa Indonesia yang mudah dipahami petani.

FORMAT JAWABAN (WAJIB DIIKUTI):
- Mulai dengan judul singkat (gunakan ## heading).
- Berikan penjelasan singkat 1–2 kalimat.
- Gunakan bullet points untuk alasan atau detail.
- Akhiri dengan ringkasan 1 kalimat.
- Maksimal 350 kata.
- JANGAN tulis paragraf panjang lebih dari 4 baris.
- Gunakan markdown: ## untuk judul, **bold** untuk penekanan, - untuk bullet.

LARANGAN:
- JANGAN memprediksi cuaca atau Flood Risk Index sendiri.
- JANGAN merekomendasikan komoditas yang tidak ada dalam data.
- JANGAN memfabrikasi angka atau nilai.
- JANGAN menjawab pertanyaan di luar topik pertanian/banjir/FloodRisk AI.
- JANGAN membuat keputusan budidaya — keputusan tetap milik pengguna.

Jika informasi tidak tersedia, jawab: "Saya tidak memiliki informasi yang cukup berdasarkan data prediksi saat ini."
Jika pertanyaan di luar topik, jawab: "Saya hanya dapat membantu menjelaskan hasil analisis FloodRisk AI, risiko genangan lahan pertanian, rekomendasi komoditas, dan strategi mitigasi."
Selalu ingatkan: "Keputusan budidaya tetap berada pada pengguna dengan mempertimbangkan kondisi lapangan."`;

const KNOWLEDGE = `## Pengetahuan Flood Risk Index
Flood Risk Index 0-33 = Rendah (tanam normal), 34-66 = Sedang (tanam dengan pencegahan), 67-100 = Tinggi (tunda/lindungi).
Faktor Flood Risk Index v2: Curah Hujan Hari Ini, Akumulasi Curah Hujan 7 Hari ke Belakang, Kelembapan, dan Suhu Rata-rata.

## Komoditas
Skor 80-100 = sangat sesuai. Kangkung toleran genangan. Cabai/tomat sensitif genangan. Bayam siklus pendek toleran kelembapan.

## Mitigasi
Prioritas 1 = segera (drainase, perlindungan). Prioritas 2 = preventif (tanggul, mulsa). Prioritas 3 = jangka menengah (rotasi, infrastruktur).`;

function buildContext(data: PrediksiRealtimeResponse): string {
  const displayValues = getRealtimeDisplayValues(data);
  const recs = data.rekomendasi.slice(0, 5).map((r) => `${r.komoditas} (skor ${r.skor.toFixed(0)}, ${r.tingkat_risiko}): ${r.ringkasan}`).join("\n");
  const mits = data.mitigasi.slice(0, 3).map((m) => `P${m.prioritas} [${m.kategori}]: ${m.tindakan}`).join("\n");
  return `## Data Prediksi Saat Ini
Lokasi: ${data.wilayah}
Tanggal Prakiraan: ${data.forecast_date ?? data.cuaca.tanggal}
${REALTIME_LABELS.rainfall}: ${formatMm(displayValues.rainfall)}
${REALTIME_LABELS.rain7}: ${formatMm(displayValues.rain7)}
${REALTIME_LABELS.humidity}: ${formatPercent(displayValues.humidity)}
${REALTIME_LABELS.tavg}: ${formatCelsius(displayValues.tavg)}
${REALTIME_LABELS.fri}: ${data.fri.toFixed(1)}
${REALTIME_LABELS.risk}: ${data.tingkat_risiko}
Model: ${data.model}

## Rekomendasi Komoditas
${recs}

## Mitigasi
${mits}`;
}

function buildMessages(data: PrediksiRealtimeResponse, history: ChatMessage[], userMessage: string): ChatMessage[] {
  const contextMsg = `${KNOWLEDGE}\n\n${buildContext(data)}`;
  const messages: ChatMessage[] = [
    { role: "system", content: SYSTEM_PROMPT },
    { role: "system", content: contextMsg },
    ...history.slice(-12),
    { role: "user", content: userMessage },
  ];
  return messages;
}

export async function chat(
  data: PrediksiRealtimeResponse,
  history: ChatMessage[],
  userMessage: string,
): Promise<string> {
  const messages = buildMessages(data, history, userMessage);

  const res = await authenticatedFetch(`${API_BASE_URL}/api/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      provider: PROVIDER,
      messages,
    }),
  });

  if (res.status === 401) {
    return "API key untuk penyedia AI belum dikonfigurasi di backend.";
  }
  if (res.status === 429) {
    return "Batas permintaan ke penyedia AI tercapai. Silakan coba lagi nanti.";
  }
  if (!res.ok) {
    const json = await res.json().catch(() => ({}));
    return (json as { detail?: string }).detail ?? "Maaf, terjadi kesalahan saat menghubungi penyedia AI.";
  }

  const json = await res.json() as { content: string };
  return json.content;
}

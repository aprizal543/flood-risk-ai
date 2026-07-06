"use client";

import { useState, useRef, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Trash2, Brain, Copy, RotateCcw, ChevronDown, ChevronUp } from "lucide-react";
import { chat, type ChatMessage } from "@/services/llm";
import { useConversationStore } from "@/hooks/use-conversation-store";
import type { PrediksiRealtimeResponse } from "@/types/api";
import { REALTIME_LABELS, formatCelsius, formatMm, formatPercent, getRealtimeDisplayValues } from "@/lib/realtime-presentation";

interface Props {
  data: PrediksiRealtimeResponse | undefined;
}

const SUGGESTIONS = [
  "Apa arti Flood Risk Index saya?",
  "Mengapa komoditas ini direkomendasikan?",
  "Apa risiko terbesar hari ini?",
  "Apakah saya sebaiknya menunda penanaman?",
  "Bagaimana mitigasi terbaik?",
];

export function AISupportPanel({ data }: Props) {
  const { messages, addMessage, clearCurrent, removeLastAssistant } = useConversationStore(
    data?.wilayah,
    data?.forecast_date ?? data?.cuaca.tanggal,
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [evidenceOpen, setEvidenceOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const displayValues = data ? getRealtimeDisplayValues(data) : null;

  const scrollToBottom = useCallback(() => {
    setTimeout(() => scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }), 50);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || !data || loading) return;
    const userMsg: ChatMessage = { role: "user", content: text.trim() };
    addMessage(userMsg);
    setInput("");
    setLoading(true);
    scrollToBottom();
    try {
      const response = await chat(data, messages, text.trim());
      addMessage({ role: "assistant", content: response });
    } catch {
      addMessage({ role: "assistant", content: "Maaf, terjadi kesalahan. Pastikan API key sudah dikonfigurasi." });
    }
    setLoading(false);
    scrollToBottom();
  }, [data, messages, loading, scrollToBottom, addMessage]);

  const handleRegenerate = useCallback(async () => {
    if (!data || loading || messages.length < 2) return;
    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUserMsg) return;
    removeLastAssistant();
    setLoading(true);
    scrollToBottom();
    try {
      const history = messages.slice(0, -1); // without last assistant
      const response = await chat(data, history, lastUserMsg.content);
      addMessage({ role: "assistant", content: response });
    } catch {
      addMessage({ role: "assistant", content: "Maaf, terjadi kesalahan saat regenerasi." });
    }
    setLoading(false);
    scrollToBottom();
  }, [data, messages, loading, scrollToBottom, addMessage, removeLastAssistant]);

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); sendMessage(input); };
  const handleKeyDown = (e: React.KeyboardEvent) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); } };

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center gap-4 px-8">
        <div className="h-14 w-14 rounded-full bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center">
          <Brain className="h-6 w-6 text-[var(--brand-primary)]" />
        </div>
        <p className="text-xs text-[var(--text-muted)]">Cari wilayah terlebih dahulu untuk mengaktifkan AI Decision Support.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 pt-4 pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-[var(--brand-primary)]/10 flex items-center justify-center">
              <Brain className="h-4 w-4 text-[var(--brand-primary)]" />
            </div>
            <div>
              <h2 className="text-[12px] font-semibold text-[var(--text-primary)]">AI Decision Support</h2>
              <p className="text-[9px] text-[var(--text-muted)]">{data.wilayah} • {data.forecast_date ?? data.cuaca.tanggal}</p>
            </div>
          </div>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--bg-card)] border border-[var(--border)] text-[9px] text-[var(--text-muted)]">
            AI Assistant
          </span>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-2 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center text-center pt-8 gap-4">
            <div className="h-12 w-12 rounded-2xl bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center">
              <Brain className="h-5 w-5 text-[var(--brand-primary)] opacity-60" />
            </div>
            <div>
              <p className="text-[11px] font-medium text-[var(--text-primary)]">AI Decision Support</p>
              <p className="text-[9px] text-[var(--text-muted)] mt-1 max-w-[260px]">
                Tanyakan kondisi cuaca, risiko banjir, atau rekomendasi budidaya berdasarkan prediksi saat ini.
              </p>
            </div>
            <div className="flex flex-wrap gap-1.5 justify-center mt-2">
              {SUGGESTIONS.map((q) => (
                <button key={q} onClick={() => sendMessage(q)}
                  className="px-3 py-1.5 text-[10px] rounded-full border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:border-[var(--border-hover)] hover:bg-[var(--bg-card)] transition-all">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className="group relative max-w-[88%]">
                <div className={`px-3.5 py-2.5 rounded-[16px] text-[11px] leading-relaxed ${
                  msg.role === "user"
                    ? "bg-[var(--brand-primary)] text-white rounded-br-[4px]"
                    : "bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-primary)] rounded-bl-[4px]"
                }`}>
                  {msg.role === "user" ? (
                    <span>{msg.content}</span>
                  ) : (
                    <MarkdownContent content={msg.content} />
                  )}
                </div>
                {/* Actions on hover */}
                <div className="absolute -top-6 right-0 hidden group-hover:flex gap-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-0.5 shadow-sm">
                  <button onClick={() => navigator.clipboard.writeText(msg.content)} title="Copy" className="h-5 w-5 flex items-center justify-center rounded text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors">
                    <Copy className="h-3 w-3" />
                  </button>
                  {msg.role === "assistant" && i === messages.length - 1 && (
                    <button onClick={handleRegenerate} title="Regenerate" className="h-5 w-5 flex items-center justify-center rounded text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors">
                      <RotateCcw className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
            <div className="px-4 py-3 rounded-[16px] rounded-bl-[4px] bg-[var(--bg-card)] border border-[var(--border)]">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:0ms]" />
                  <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:150ms]" />
                  <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:300ms]" />
                </div>
                <span className="text-[9px] text-[var(--text-muted)]">Menganalisis data cuaca...</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Evidence Panel - after messages exist */}
        {messages.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-2">
            <button onClick={() => setEvidenceOpen((o) => !o)} className="flex items-center gap-1.5 text-[9px] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors mb-1">
              {evidenceOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
              Dasar Analisis
            </button>
            {evidenceOpen && (
              <div className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] p-3 text-[9px] space-y-1.5">
                <ERow label={REALTIME_LABELS.fri} value={`${data.fri.toFixed(1)} (${data.tingkat_risiko})`} />
                <ERow label={REALTIME_LABELS.rainfall} value={formatMm(displayValues?.rainfall ?? null)} />
                <ERow label={REALTIME_LABELS.rain7} value={formatMm(displayValues?.rain7 ?? null)} />
                <ERow label={REALTIME_LABELS.humidity} value={formatPercent(displayValues?.humidity ?? null)} />
                <ERow label={REALTIME_LABELS.tavg} value={formatCelsius(displayValues?.tavg ?? null)} />
                <ERow label="Prakiraan" value={data.forecast_date ?? data.cuaca.tanggal} />
                <ERow label="Top Komoditas" value={data.rekomendasi[0]?.komoditas ?? "—"} />
                <ERow label="Sumber" value="Open-Meteo" />
                <div className="flex flex-wrap gap-1 pt-1 border-t border-[var(--border)]">
                  {["Flood Risk Index Guide", "Komoditas", "Mitigasi", "FAQ"].map((r) => (
                    <span key={r} className="px-2 py-0.5 rounded-full bg-[var(--brand-primary)]/10 text-[var(--brand-primary)] text-[8px] font-medium">{r}</span>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="px-4 py-1.5">
        <p className="text-[8px] text-[var(--text-muted)] text-center">AI memberikan penjelasan berdasarkan data prediksi. Keputusan budidaya tetap berada pada pengguna.</p>
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="px-4 pb-4 pt-1">
        <div className="flex items-end gap-2 bg-[var(--bg-card)] border border-[var(--border)] rounded-[20px] px-4 py-2 focus-within:border-[var(--brand-primary)]/50 focus-within:shadow-[0_0_0_3px_var(--brand-glow)] transition-all">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tanyakan sesuatu mengenai kondisi cuaca atau rekomendasi budidaya..."
            rows={1}
            className="flex-1 text-[11px] bg-transparent text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none resize-none max-h-24"
          />
          <div className="flex gap-1.5 shrink-0">
            {messages.length > 0 && (
              <button type="button" onClick={clearCurrent} title="Hapus percakapan ini" className="h-7 w-7 flex items-center justify-center rounded-full text-[var(--text-muted)] hover:text-red-400 hover:bg-red-500/10 transition-colors">
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
            <button type="submit" disabled={!input.trim() || loading} className="h-7 w-7 flex items-center justify-center rounded-full bg-[var(--brand-primary)] text-white disabled:opacity-30 transition-opacity">
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   MARKDOWN RENDERER
   ═══════════════════════════════════════════════════════════ */

function MarkdownContent({ content }: { content: string }) {
  const rendered = useMemo(() => parseMarkdown(content), [content]);
  return <div className="ai-markdown">{rendered}</div>;
}

/**
 * Lightweight markdown parser for AI responses.
 * Handles: headings, bold, italic, bullet lists, numbered lists, paragraphs.
 * No external dependency needed.
 */
function parseMarkdown(text: string): React.ReactNode[] {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let listItems: React.ReactNode[] = [];
  let listType: "ul" | "ol" | null = null;
  let key = 0;

  const flushList = () => {
    if (listItems.length > 0 && listType) {
      if (listType === "ul") {
        elements.push(<ul key={key++} className="ai-list">{listItems}</ul>);
      } else {
        elements.push(<ol key={key++} className="ai-list ai-list-numbered">{listItems}</ol>);
      }
      listItems = [];
      listType = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Empty line
    if (!trimmed) {
      flushList();
      continue;
    }

    // Headings
    const h3Match = trimmed.match(/^###\s+(.+)/);
    if (h3Match) { flushList(); elements.push(<h4 key={key++} className="ai-heading">{inlineFormat(h3Match[1])}</h4>); continue; }
    const h2Match = trimmed.match(/^##\s+(.+)/);
    if (h2Match) { flushList(); elements.push(<h3 key={key++} className="ai-heading">{inlineFormat(h2Match[1])}</h3>); continue; }
    const h1Match = trimmed.match(/^#\s+(.+)/);
    if (h1Match) { flushList(); elements.push(<h3 key={key++} className="ai-heading ai-heading-primary">{inlineFormat(h1Match[1])}</h3>); continue; }

    // Bullet list
    const bulletMatch = trimmed.match(/^[-*•]\s+(.+)/);
    if (bulletMatch) {
      if (listType !== "ul") { flushList(); listType = "ul"; }
      listItems.push(<li key={key++}>{inlineFormat(bulletMatch[1])}</li>);
      continue;
    }

    // Numbered list
    const numMatch = trimmed.match(/^\d+[.)]\s+(.+)/);
    if (numMatch) {
      if (listType !== "ol") { flushList(); listType = "ol"; }
      listItems.push(<li key={key++}>{inlineFormat(numMatch[1])}</li>);
      continue;
    }

    // Paragraph
    flushList();
    elements.push(<p key={key++} className="ai-paragraph">{inlineFormat(trimmed)}</p>);
  }

  flushList();
  return elements;
}

/**
 * Format inline markdown: **bold**, *italic*, `code`
 */
function inlineFormat(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  // Match **bold**, *italic*, `code`
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let partKey = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[2]) {
      parts.push(<strong key={partKey++}>{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(<em key={partKey++}>{match[3]}</em>);
    } else if (match[4]) {
      parts.push(<code key={partKey++} className="ai-code">{match[4]}</code>);
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? <>{parts}</> : text;
}

/* ═══════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════ */

function ERow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="font-medium text-[var(--text-primary)]">{value}</span>
    </div>
  );
}

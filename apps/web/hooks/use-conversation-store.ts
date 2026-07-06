"use client";

import { useState, useCallback, useMemo } from "react";
import type { ChatMessage } from "@/services/llm";

const STORAGE_KEY = "floodrisk_ai_conversations";

interface ConversationStore {
  [key: string]: ChatMessage[];
}

/**
 * Build the conversation key from wilayah + forecast_date.
 * Example: "Pekanbaru_2026-07-01"
 */
function buildKey(wilayah: string, forecastDate: string): string {
  return `${wilayah}_${forecastDate}`;
}

function loadStore(): ConversationStore {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveStore(store: ConversationStore): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    // localStorage full or unavailable — silently ignore
  }
}

function loadMessages(key: string | null): ChatMessage[] {
  if (!key) return [];
  const store = loadStore();
  return store[key] ?? [];
}

function persistMessages(key: string | null, messages: ChatMessage[]): void {
  if (!key) return;
  const store = loadStore();
  store[key] = messages;
  saveStore(store);
}

/**
 * Hook for region-based conversation persistence.
 *
 * - Each conversation is keyed by `{wilayah}_{forecast_date}`
 * - Switching regions automatically loads/creates the correct conversation
 * - "Clear" only clears the current conversation
 * - Conversations persist across workspace navigation via localStorage
 *
 * The consumer component should pass `conversationKey` as a React `key` prop
 * on itself or a wrapper to ensure state resets on region change.
 * Alternatively, this hook detects key changes via the `keyVersion` state.
 */
export function useConversationStore(wilayah: string | undefined, forecastDate: string | undefined) {
  const key = useMemo(
    () => (wilayah && forecastDate ? buildKey(wilayah, forecastDate) : null),
    [wilayah, forecastDate],
  );

  // Use a version counter to force re-read from localStorage when key changes.
  // The initial state loads from localStorage. When key changes externally,
  // the consumer re-creates with a new key (via React key prop pattern).
  const [messages, setMessages] = useState<ChatMessage[]>(() => loadMessages(key));

  // Track current key to detect changes without refs
  const [activeKey, setActiveKey] = useState<string | null>(key);

  // If key changed, reload from storage synchronously
  if (key !== activeKey) {
    setActiveKey(key);
    setMessages(loadMessages(key));
  }

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => {
      const next = [...prev, msg];
      persistMessages(key, next);
      return next;
    });
  }, [key]);

  const clearCurrent = useCallback(() => {
    setMessages([]);
    persistMessages(key, []);
  }, [key]);

  const clearAll = useCallback(() => {
    setMessages([]);
    saveStore({});
  }, []);

  const removeLastAssistant = useCallback(() => {
    setMessages((prev) => {
      const copy = [...prev];
      for (let i = copy.length - 1; i >= 0; i--) {
        if (copy[i].role === "assistant") {
          copy.splice(i, 1);
          break;
        }
      }
      persistMessages(key, copy);
      return copy;
    });
  }, [key]);

  return {
    messages,
    addMessage,
    clearCurrent,
    clearAll,
    removeLastAssistant,
    conversationKey: key,
  };
}

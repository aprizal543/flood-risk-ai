"use client";

import { useEffect, useCallback, useSyncExternalStore } from "react";

const RESET_DATE_KEY = "floodrisk_last_reset_date";
const TOAST_KEY = "floodrisk_reset_toast_pending";

function getTodayWIB(): string {
  return new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Jakarta" });
}

function getToastSnapshot(): string {
  return localStorage.getItem(TOAST_KEY) ?? "false";
}

function getToastServerSnapshot(): string {
  return "false";
}

function subscribeToast(cb: () => void) {
  window.addEventListener("storage", cb);
  return () => window.removeEventListener("storage", cb);
}

/**
 * Hook: detects day change and triggers reset.
 * Uses useSyncExternalStore to read toast state from localStorage (lint-safe).
 */
export function useDailyReset(onReset: () => void) {
  const toastRaw = useSyncExternalStore(subscribeToast, getToastSnapshot, getToastServerSnapshot);
  const showToast = toastRaw === "true";

  // Check function: runs from event handlers only (not synchronously in effect body)
  const check = useCallback(() => {
    const today = getTodayWIB();
    const lastReset = localStorage.getItem(RESET_DATE_KEY);
    if (lastReset === today) return;
    localStorage.setItem(RESET_DATE_KEY, today);
    if (lastReset !== null) {
      onReset();
      localStorage.setItem(TOAST_KEY, "true");
      window.dispatchEvent(new StorageEvent("storage", { key: TOAST_KEY }));
    }
  }, [onReset]);

  // Subscribe to events; initial check via deferred callback
  useEffect(() => {
    const timer = setTimeout(check, 0);
    const onVisibility = () => { if (document.visibilityState === "visible") check(); };
    const onFocus = () => check();
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("focus", onFocus);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("focus", onFocus);
    };
  }, [check]);

  const dismissToast = useCallback(() => {
    localStorage.setItem(TOAST_KEY, "false");
    window.dispatchEvent(new StorageEvent("storage", { key: TOAST_KEY }));
  }, []);

  return { showToast, dismissToast };
}

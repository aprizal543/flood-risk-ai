"use client";

import { useEffect, useRef } from "react";
import { X } from "lucide-react";

interface ToastProps {
  message: string;
  description?: string;
  duration?: number;
  visible: boolean;
  onClose: () => void;
}

export function Toast({ message, description, duration = 5000, visible, onClose }: ToastProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    clearTimeout(timerRef.current);
    if (visible) {
      timerRef.current = setTimeout(onClose, duration);
    }
    return () => clearTimeout(timerRef.current);
  }, [visible, duration, onClose]);

  if (!visible) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm animate-in slide-in-from-top-2 fade-in">
      <div className="bg-white rounded-lg shadow-lg border border-[var(--border)] p-4 flex gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-[var(--text-primary)]">{message}</p>
          {description && <p className="text-xs text-[var(--text-muted)] mt-1">{description}</p>}
        </div>
        <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

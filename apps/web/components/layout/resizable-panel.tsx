"use client";

import { useCallback, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { useLocalStorage } from "@/hooks/use-local-storage";
import {
  PANEL_DEFAULT_WIDTH,
  PANEL_MIN_WIDTH,
  PANEL_MAX_WIDTH,
  STORAGE_KEYS,
} from "@/lib/constants";

interface ResizablePanelProps {
  children: React.ReactNode;
}

export function ResizablePanel({ children }: ResizablePanelProps) {
  const [width, setWidth] = useLocalStorage(STORAGE_KEYS.panelWidth, PANEL_DEFAULT_WIDTH);
  const isDragging = useRef(false);
  const panelRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback(() => {
    isDragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const handleDoubleClick = useCallback(() => {
    setWidth(PANEL_DEFAULT_WIDTH);
  }, [setWidth]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;
      const sidebar = document.querySelector("[aria-label='Navigasi utama']");
      const sidebarWidth = sidebar?.getBoundingClientRect().width ?? 80;
      const newWidth = e.clientX - sidebarWidth;
      if (newWidth >= PANEL_MIN_WIDTH && newWidth <= PANEL_MAX_WIDTH) {
        setWidth(newWidth);
      } else if (newWidth < PANEL_MIN_WIDTH - 50) {
        setWidth(0);
      }
    };

    const handleMouseUp = () => {
      if (isDragging.current) {
        isDragging.current = false;
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [setWidth]);

  const collapsed = width === 0;

  return (
    <>
      <motion.div
        ref={panelRef}
        animate={{ width: collapsed ? 0 : width }}
        transition={{ duration: 0.2, ease: [0.4, 0, 0.6, 1] }}
        className="relative h-full overflow-hidden shrink-0 rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--bg-panel)] shadow-[var(--shadow-card)]"
        aria-label="Panel informasi"
      >
        {!collapsed && (
          <div className="h-full overflow-y-auto p-4">{children}</div>
        )}
      </motion.div>

      {/* Divider */}
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label="Geser untuk mengubah ukuran panel"
        tabIndex={0}
        className="relative w-1 h-full shrink-0 cursor-col-resize group z-15"
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") setWidth((w) => Math.max(PANEL_MIN_WIDTH, (w || PANEL_DEFAULT_WIDTH) - 10));
          if (e.key === "ArrowRight") setWidth((w) => Math.min(PANEL_MAX_WIDTH, (w || PANEL_DEFAULT_WIDTH) + 10));
        }}
      >
        <div className="absolute inset-y-0 -left-1 w-3" />
        <div className="absolute inset-y-0 left-0 w-1 bg-[var(--border)] group-hover:bg-[var(--brand-primary)] transition-colors duration-150" />
      </div>
    </>
  );
}

"use client";

import { useState, useCallback } from "react";

export type WorkspaceMenu = "dashboard" | "ai-support" | "reports" | "settings" | "about";

export function useWorkspaceStore() {
  const [activeMenu, setActiveMenu] = useState<WorkspaceMenu>("dashboard");
  const switchTo = useCallback((menu: WorkspaceMenu) => setActiveMenu(menu), []);
  return { activeMenu, switchTo };
}

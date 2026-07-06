"use client";

import { useState } from "react";
import { Home, Brain, FileText, Settings, Info, LogOut, Droplets } from "lucide-react";
import { cn } from "@/lib/utils";
import type { WorkspaceMenu } from "@/hooks/use-workspace-store";
import { useAuth } from "@/hooks/use-auth";

const NAV_ITEMS: { icon: typeof Home; label: string; id: WorkspaceMenu }[] = [
  { icon: Home, label: "Dashboard", id: "dashboard" },
  { icon: Brain, label: "AI Assistant", id: "ai-support" },
  { icon: FileText, label: "Laporan", id: "reports" },
  { icon: Settings, label: "Pengaturan", id: "settings" },
  { icon: Info, label: "Tentang", id: "about" },
];

interface SidebarProps {
  activeMenu: WorkspaceMenu;
  onNavigate: (menu: WorkspaceMenu) => void;
  onLogout: () => void;
}

function getInitials(name: string | null | undefined): string {
  if (!name || name.trim().length === 0) return "?";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

export function Sidebar({ activeMenu, onNavigate, onLogout }: SidebarProps) {
  const [showLogout, setShowLogout] = useState(false);
  const { user } = useAuth();

  const fullName = user?.full_name ?? "User";
  const initials = getInitials(user?.full_name);

  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-30 flex flex-col items-center py-4 w-[72px]" aria-label="Navigasi">
        <div className="flex flex-col items-center gap-2 h-full bg-[var(--bg-sidebar)] border border-[var(--border)] rounded-[var(--radius-sidebar)] mx-2 my-2 py-4 px-1.5 shadow-[var(--shadow-float)]">
          {/* Logo */}
          <div className="flex items-center justify-center h-9 w-9 rounded-xl bg-[var(--brand-primary)]/10 mb-3">
            <Droplets className="h-5 w-5 text-[var(--brand-primary)]" />
          </div>

          {/* Navigation */}
          <nav className="flex flex-col gap-1 flex-1">
            {NAV_ITEMS.map(({ icon: Icon, label, id }) => {
              const active = activeMenu === id;
              return (
                <button
                  key={id}
                  onClick={() => onNavigate(id)}
                  title={label}
                  aria-label={label}
                  className={cn(
                    "relative flex items-center justify-center h-10 w-10 rounded-xl transition-all duration-200",
                    active
                      ? "bg-[var(--brand-primary)]/15 text-[var(--brand-primary)] shadow-[0_0_12px_var(--brand-glow)]"
                      : "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card)]"
                  )}
                >
                  <Icon className="h-[18px] w-[18px]" />
                </button>
              );
            })}
          </nav>

          {/* User */}
          <div className="relative group">
            <div className="flex items-center justify-center h-9 w-9 rounded-full bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-muted)] group-hover:text-[var(--text-primary)] transition-colors cursor-default">
              <span className="text-[10px] font-semibold">{initials}</span>
            </div>
            <div className="absolute left-full ml-3 bottom-0 px-2.5 py-1.5 text-[11px] font-medium whitespace-nowrap rounded-lg bg-[var(--bg-card)] border border-[var(--border)] shadow-[var(--shadow-popup)] text-[var(--text-primary)] opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
              {fullName}
            </div>
          </div>

          {/* Logout */}
          <button onClick={() => setShowLogout(true)} title="Keluar" className="flex items-center justify-center h-9 w-9 rounded-xl text-[var(--text-muted)] hover:text-red-400 hover:bg-red-500/10 transition-colors">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </aside>

      {/* Logout Dialog */}
      {showLogout && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius-card)] shadow-[var(--shadow-popup)] p-6 w-80">
            <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">Keluar dari FloodRisk AI?</h3>
            <p className="text-xs text-[var(--text-muted)] mb-5">Riwayat prediksi dan percakapan AI akan dihapus.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowLogout(false)} className="px-4 py-2 text-xs rounded-[var(--radius-btn)] border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">Batalkan</button>
              <button onClick={() => { setShowLogout(false); onLogout(); }} className="px-4 py-2 text-xs rounded-[var(--radius-btn)] bg-red-500 text-white hover:bg-red-600 transition-colors font-medium">Keluar</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

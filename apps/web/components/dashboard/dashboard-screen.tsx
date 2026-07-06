"use client";

import { Suspense, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import { ResizablePanel } from "@/components/layout/resizable-panel";
import { MapContainer } from "@/components/map/map-container";
import { DashboardPanel } from "@/components/dashboard/dashboard-panel";
import { AISupportPanel } from "@/components/dashboard/ai-support-panel";
import { ReportsPanel } from "@/components/dashboard/reports-panel";
import { SettingsPanel, AboutPanel } from "@/components/dashboard/workspace-panels";
import { Toast } from "@/components/shared/Toast";
import { useRealtimePrediction } from "@/hooks/use-realtime-prediction";
import { useWilayahSync } from "@/hooks/use-wilayah-sync";
import { useSearchHistory } from "@/hooks/use-search-history";
import { useDailyReset } from "@/hooks/use-daily-reset";
import { useWorkspaceStore } from "@/hooks/use-workspace-store";
import { useAuth } from "@/hooks/use-auth";
import { getRealtimeDisplayValues } from "@/lib/realtime-presentation";

function DashboardContent() {
  const { wilayah, setWilayah, clearWilayah } = useWilayahSync();
  const { history, upsert, remove, clear } = useSearchHistory();
  const { activeMenu, switchTo } = useWorkspaceStore();
  const { signOut } = useAuth();

  const handleDailyReset = useCallback(() => { clear(); }, [clear]);
  const { showToast: showResetToast, dismissToast } = useDailyReset(handleDailyReset);

  const { data, isLoading, error, refetch } = useRealtimePrediction(wilayah ?? "");

  useEffect(() => {
    if (data?.cuaca.latitude && data?.cuaca.longitude) {
      const displayValues = getRealtimeDisplayValues(data);
      upsert({
        wilayah: data.wilayah,
        latitude: data.cuaca.latitude,
        longitude: data.cuaca.longitude,
        fri: data.fri,
        tingkatRisiko: data.tingkat_risiko,
        timestamp: data.waktu_prediksi,
        rr: displayValues.rainfall ?? undefined,
        rain7: displayValues.rain7 ?? undefined,
        rh_avg: displayValues.humidity ?? undefined,
        tavg: displayValues.tavg ?? undefined,
      });
    }
  }, [data, upsert]);

  const handleMarkerClick = useCallback((w: string) => {
    setWilayah(w);
    switchTo("dashboard");
  }, [setWilayah, switchTo]);

  const handleClearHistory = useCallback(() => clear(wilayah ?? undefined), [clear, wilayah]);
  const handleClearAI = useCallback(() => {
    localStorage.removeItem("floodrisk_ai_conversation");
  }, []);

const handleLogout = useCallback(async () => {
  try {
    clear();

    if (typeof window !== "undefined") {
      localStorage.removeItem("floodrisk_ai_conversation");
    }

    await signOut();
  } catch (error) {
    console.error("Logout failed:", error);
  }
}, [clear, signOut]);

  const handleRemoveCity = useCallback((w: string) => {
    remove(w);
    if (w === wilayah) {
      clearWilayah();
    }
  }, [remove, wilayah, clearWilayah]);

  return (
    <div className="flex h-screen w-screen overflow-hidden p-2 gap-2">
      <Sidebar activeMenu={activeMenu} onNavigate={switchTo} onLogout={handleLogout} />
      <div className="flex flex-1 h-full gap-2 ml-[72px]">
        <ResizablePanel>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeMenu}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 8 }}
              transition={{ duration: 0.15 }}
              className="h-full"
            >
              {activeMenu === "dashboard" && (
                <DashboardPanel data={data} isLoading={isLoading} error={error} onRetry={() => refetch()} />
              )}
              {activeMenu === "ai-support" && <AISupportPanel data={data} />}
              {activeMenu === "reports" && <ReportsPanel data={data} />}
              {activeMenu === "settings" && <SettingsPanel onClearHistory={() => clear()} onClearAI={handleClearAI} />}
              {activeMenu === "about" && <AboutPanel />}
            </motion.div>
          </AnimatePresence>
        </ResizablePanel>
        <MapContainer
          wilayah={wilayah}
          fri={data?.fri}
          latitude={data?.cuaca.latitude}
          longitude={data?.cuaca.longitude}
          history={history}
          onSearch={setWilayah}
          onMarkerClick={handleMarkerClick}
          onClearHistory={handleClearHistory}
          onRemoveCity={handleRemoveCity}
        />
      </div>
      <Toast
        visible={showResetToast}
        message="🌅 Monitoring Baru Dimulai"
        description="Riwayat prediksi hari sebelumnya telah dibersihkan. Silakan cari wilayah untuk melihat kondisi cuaca dan Flood Risk Index terbaru."
        duration={5000}
        onClose={dismissToast}
      />
    </div>
  );
}

export function DashboardScreen() {
  return (
    <Suspense>
      <DashboardContent />
    </Suspense>
  );
}

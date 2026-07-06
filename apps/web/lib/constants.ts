export const SIDEBAR_WIDTH = 80;
export const SIDEBAR_COLLAPSED_WIDTH = 48;
export const PANEL_DEFAULT_WIDTH = 380;
export const PANEL_MIN_WIDTH = 320;
export const PANEL_MAX_WIDTH = 720;

export const STORAGE_KEYS = {
  sidebarCollapsed: "floodrisk_sidebar_collapsed",
  panelWidth: "floodrisk_panel_width",
  theme: "floodrisk_theme",
  mapLayer: "floodrisk_map_layer",
  lastWilayah: "floodrisk_last_wilayah",
} as const;

export const MAP_DEFAULT_CENTER: [number, number] = [101.447, 0.507];
export const MAP_DEFAULT_ZOOM = 11;

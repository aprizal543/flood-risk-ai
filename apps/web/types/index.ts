export type RiskLevel = "Rendah" | "Sedang" | "Tinggi";
export type Theme = "light" | "dark" | "system";
export type Model = "rf" | "lstm";

export interface NavItem {
  icon: string;
  label: string;
  href: string;
}

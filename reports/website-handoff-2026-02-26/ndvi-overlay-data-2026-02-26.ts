export type ActionType = "irrigation_needed" | "pest_disease_pressure" | "irrigation_leak";

export type Point = { xPct: number; yPct: number };

export type OverlayPoint = {
  id: string;
  action: ActionType;
  label: string;
  xPct: number;
  yPct: number;
  confidence?: number;
  note?: string;
  rowPath?: Point[];
};

export const ACTION_COLORS = {
  irrigation_needed: {
    base: "#F59E0B",
    bg: "rgba(245,158,11,0.18)",
    border: "#F59E0B",
    text: "#B45309"
  },
  pest_disease_pressure: {
    base: "#DC2626",
    bg: "rgba(220,38,38,0.18)",
    border: "#DC2626",
    text: "#991B1B"
  },
  irrigation_leak: {
    base: "#2563EB",
    bg: "rgba(37,99,235,0.18)",
    border: "#2563EB",
    text: "#1E40AF"
  }
} as const;

export const demoOverlays: OverlayPoint[] = [
  { id: "ir-01", action: "irrigation_needed", label: "Irrigation Needed", xPct: 18, yPct: 32, confidence: 0.86, note: "Low vigor + thermal stress", rowPath: [{ xPct: 14, yPct: 28 }, { xPct: 22, yPct: 38 }, { xPct: 24, yPct: 41 }, { xPct: 16, yPct: 31 }] },
  { id: "ir-02", action: "irrigation_needed", label: "Irrigation Needed", xPct: 26, yPct: 46, confidence: 0.83, rowPath: [{ xPct: 22, yPct: 42 }, { xPct: 30, yPct: 52 }, { xPct: 32, yPct: 55 }, { xPct: 24, yPct: 45 }] },
  { id: "ir-03", action: "irrigation_needed", label: "Irrigation Needed", xPct: 34, yPct: 59, confidence: 0.81, rowPath: [{ xPct: 30, yPct: 55 }, { xPct: 38, yPct: 65 }, { xPct: 40, yPct: 68 }, { xPct: 32, yPct: 58 }] },
  { id: "ir-04", action: "irrigation_needed", label: "Irrigation Needed", xPct: 42, yPct: 72, confidence: 0.78, rowPath: [{ xPct: 38, yPct: 68 }, { xPct: 46, yPct: 78 }, { xPct: 48, yPct: 81 }, { xPct: 40, yPct: 71 }] },

  { id: "pd-01", action: "pest_disease_pressure", label: "Pest/Disease Pressure", xPct: 56, yPct: 28, confidence: 0.88, note: "Localized canopy anomaly", rowPath: [{ xPct: 52, yPct: 24 }, { xPct: 60, yPct: 34 }, { xPct: 62, yPct: 37 }, { xPct: 54, yPct: 27 }] },
  { id: "pd-02", action: "pest_disease_pressure", label: "Pest/Disease Pressure", xPct: 63, yPct: 41, confidence: 0.85, rowPath: [{ xPct: 59, yPct: 37 }, { xPct: 67, yPct: 47 }, { xPct: 69, yPct: 50 }, { xPct: 61, yPct: 40 }] },
  { id: "pd-03", action: "pest_disease_pressure", label: "Pest/Disease Pressure", xPct: 70, yPct: 54, confidence: 0.84, rowPath: [{ xPct: 66, yPct: 50 }, { xPct: 74, yPct: 60 }, { xPct: 76, yPct: 63 }, { xPct: 68, yPct: 53 }] },
  { id: "pd-04", action: "pest_disease_pressure", label: "Pest/Disease Pressure", xPct: 77, yPct: 66, confidence: 0.80, rowPath: [{ xPct: 73, yPct: 62 }, { xPct: 81, yPct: 72 }, { xPct: 83, yPct: 75 }, { xPct: 75, yPct: 65 }] },

  { id: "lk-01", action: "irrigation_leak", label: "Irrigation Leak", xPct: 48, yPct: 63, confidence: 0.91, note: "Thermal hotspot + moisture pattern", rowPath: [{ xPct: 45, yPct: 60 }, { xPct: 51, yPct: 66 }, { xPct: 53, yPct: 69 }, { xPct: 47, yPct: 63 }] },
  { id: "lk-02", action: "irrigation_leak", label: "Irrigation Leak", xPct: 53, yPct: 70, confidence: 0.89, rowPath: [{ xPct: 50, yPct: 67 }, { xPct: 56, yPct: 73 }, { xPct: 58, yPct: 76 }, { xPct: 52, yPct: 70 }] },
  { id: "lk-03", action: "irrigation_leak", label: "Irrigation Leak", xPct: 58, yPct: 76, confidence: 0.87, rowPath: [{ xPct: 55, yPct: 73 }, { xPct: 61, yPct: 79 }, { xPct: 63, yPct: 82 }, { xPct: 57, yPct: 76 }] },
  { id: "lk-04", action: "irrigation_leak", label: "Irrigation Leak", xPct: 63, yPct: 82, confidence: 0.85, rowPath: [{ xPct: 60, yPct: 79 }, { xPct: 66, yPct: 85 }, { xPct: 68, yPct: 88 }, { xPct: 62, yPct: 82 }] }
];

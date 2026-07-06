"use client";

import { createRoot } from "react-dom/client";
import { PrintableReport } from "./PrintableReport";
import type { PrediksiRealtimeResponse } from "@/types/api";

interface PrintOptions {
  data: PrediksiRealtimeResponse;
}

/**
 * Opens a new window, renders the PrintableReport component,
 * injects print styles, waits for fonts to load, then triggers print.
 *
 * Flow:
 * 1. Open blank window
 * 2. Write HTML skeleton with Inter font link + linked print.css
 * 3. Mount React component into the window
 * 4. Wait for document.fonts.ready + stylesheet loaded
 * 5. Trigger window.print()
 */
export function openPrintWindow({ data }: PrintOptions): void {
  const printWin = window.open("", "_blank", "width=900,height=1100");
  if (!printWin) {
    alert("Popup diblokir oleh browser. Izinkan popup untuk mencetak laporan.");
    return;
  }

  // Write the HTML skeleton — stylesheet is loaded from /print-report.css (public dir)
  printWin.document.write(`<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FloodRisk AI — Forecast Report | ${data.wilayah}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/print-report.css" />
</head>
<body>
  <div id="print-root"></div>
</body>
</html>`);
  printWin.document.close();

  // Mount React component
  const root = printWin.document.getElementById("print-root");
  if (!root) {
    printWin.close();
    return;
  }

  const reactRoot = createRoot(root);
  reactRoot.render(
    <PrintableReport data={data} />
  );

  // Wait for fonts + stylesheet to load, then print
  const triggerPrint = () => {
    printWin.setTimeout(() => {
      printWin.focus();
      printWin.print();
    }, 300);
  };

  // Wait for both fonts and stylesheet to be ready
  const waitAndPrint = () => {
    if (printWin.document.fonts && printWin.document.fonts.ready) {
      printWin.document.fonts.ready
        .then(() => triggerPrint())
        .catch(() => triggerPrint());
    } else {
      printWin.setTimeout(triggerPrint, 1000);
    }
  };

  // Wait for the stylesheet to load
  const styleLink = printWin.document.querySelector('link[href="/print-report.css"]');
  if (styleLink) {
    styleLink.addEventListener("load", waitAndPrint);
    styleLink.addEventListener("error", waitAndPrint); // Still print even if CSS fails
  } else {
    waitAndPrint();
  }
}

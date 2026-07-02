"""anomaly.py – Derivasi fitur anomali curah hujan."""

import numpy as np


# Percentile breakpoints dari dataset Pekanbaru (bmkg_clean.csv)
# TODO: Ganti dengan klimatologi realtime saat data historis lebih panjang tersedia
_RR_PERCENTILES = np.array([0, 0.8, 5.0, 20.0, 50.0, 100.0, 167.0])
_PCT_VALUES = np.array([0, 21.0, 50.0, 70.0, 85.0, 95.0, 100.0])


def compute_rainfall_anomaly(rr: float) -> float:
    """Hitung anomali curah hujan sebagai persentil aproksimasi (0-100).

    Menggunakan interpolasi linier berdasarkan distribusi empiris dataset Pekanbaru.

    TODO: Implementasikan klimatologi realtime untuk akurasi lebih tinggi.
    """
    if np.isnan(rr):
        return float("nan")
    return float(np.interp(rr, _RR_PERCENTILES, _PCT_VALUES))

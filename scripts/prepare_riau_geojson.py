"""Prepare Riau ADM2 GeoJSON from geoBoundaries Indonesia dataset."""

import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

INPUT = "data/geo/raw/geoBoundaries-IDN-ADM2_simplified.geojson"
OUTPUT_DIR = "apps/web/public/geo/riau"
OUTPUT_GEOJSON = os.path.join(OUTPUT_DIR, "riau_adm2.geojson")
OUTPUT_META = os.path.join(OUTPUT_DIR, "metadata.json")

# Expected Riau features: shapeName -> (nama, tipe)
RIAU_FEATURES = {
    "Kota Pekanbaru": ("Kota Pekanbaru", "Kota"),
    "Kota Dumai": ("Kota Dumai", "Kota"),
    "Kampar": ("Kabupaten Kampar", "Kabupaten"),
    "Bengkalis": ("Kabupaten Bengkalis", "Kabupaten"),
    "Siak": ("Kabupaten Siak", "Kabupaten"),
    "Pelalawan": ("Kabupaten Pelalawan", "Kabupaten"),
    "Rokan Hulu": ("Kabupaten Rokan Hulu", "Kabupaten"),
    "Rokan Hilir": ("Kabupaten Rokan Hilir", "Kabupaten"),
    "Kuantan Singingi": ("Kabupaten Kuantan Singingi", "Kabupaten"),
    "Indragiri Hulu": ("Kabupaten Indragiri Hulu", "Kabupaten"),
    "Indragiri Hilir": ("Kabupaten Indragiri Hilir", "Kabupaten"),
    "Kepulauan Meranti": ("Kabupaten Kepulauan Meranti", "Kabupaten"),
}


def main():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    features = []
    for feat in data["features"]:
        name = feat["properties"]["shapeName"]
        if name in RIAU_FEATURES:
            nama, tipe = RIAU_FEATURES[name]
            feat["properties"] = {
                "kode": feat["properties"]["shapeISO"] or feat["properties"]["shapeID"],
                "nama": nama,
                "provinsi": "Riau",
                "tipe": tipe,
            }
            features.append(feat)

    geojson = {"type": "FeatureCollection", "features": features}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    kab_count = sum(1 for ft in features if ft["properties"]["tipe"] == "Kabupaten")
    kota_count = sum(1 for ft in features if ft["properties"]["tipe"] == "Kota")

    metadata = {
        "province": "Riau",
        "feature_count": len(features),
        "coordinate_system": "WGS84",
        "source": "geoBoundaries ADM2 Simplified",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUTPUT_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Validation
    size_kb = os.path.getsize(OUTPUT_GEOJSON) / 1024
    geom_valid = all(
        f["geometry"]["type"] in ("Polygon", "MultiPolygon") for f in features
    )

    print(f"✔ Province detected: Riau")
    print(f"✔ Feature count: {len(features)}")
    print(f"✔ Kabupaten count: {kab_count}")
    print(f"✔ Kota count: {kota_count}")
    print(f"✔ Geometry valid: {geom_valid}")
    print(f"✔ Output size: {size_kb:.1f} KB")

    if len(features) != 12:
        print(f"⚠ Expected 12 features, got {len(features)}")
        missing = set(RIAU_FEATURES.keys()) - {
            f["properties"]["nama"].replace("Kabupaten ", "").replace("Kota ", "")
            if f["properties"]["tipe"] == "Kabupaten"
            else f["properties"]["nama"]
            for f in features
        }
        if missing:
            print(f"  Missing: {missing}")


if __name__ == "__main__":
    main()

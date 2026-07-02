import json

with open("apps/web/public/geo/riau/riau_adm2.geojson", encoding="utf-8") as f:
    data = json.load(f)

def centroid(geom):
    coords = []
    def extract(c, d):
        if d == 0:
            coords.append(c)
        else:
            for i in c:
                extract(i, d - 1)
    if geom["type"] == "Polygon":
        extract(geom["coordinates"], 2)
    else:
        extract(geom["coordinates"], 3)
    lngs = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [round(sum(lngs) / len(lngs), 6), round(sum(lats) / len(lats), 6)]

index = []
for feat in data["features"]:
    p = feat["properties"]
    nama = p["nama"]
    canonical = nama.replace("Kota ", "").replace("Kabupaten ", "")
    c = centroid(feat["geometry"])
    index.append({"nama": nama, "canonical": canonical, "tipe": p["tipe"], "kode": p["kode"], "centroid": c})

index.sort(key=lambda x: x["nama"])
with open("apps/web/public/geo/riau/search_index.json", "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"Done: {len(index)} entries")
for e in index:
    print(f"  {e['nama']} @ {e['centroid']}")

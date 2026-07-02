import requests
import csv

cities = [
    "Pekanbaru", "Medan", "Padang", "Palembang", "Jambi", "Bandung", "Jakarta", "Bogor", "Semarang", "Yogyakarta"
]

API_URL = "http://localhost:8000/api/prediksi/realtime"

fieldnames = ["city", "tanggal", "rr", "rain3", "rain7", "rain14", "rh_avg", "temp_range", "rainfall_anomaly", "month", "day_of_year", "fri", "risk", "recommendations"]

results = []

for city in cities:
    try:
        params = {"wilayah": city, "model": "rf"}
        response = requests.get(API_URL, params=params, timeout=15)
        data = response.json()
        if data["status"] == "berhasil":
            r = data["cuaca"]
            recs = data.get("rekomendasi", [])
            rec_str = "; ".join([rec.get("komoditas", "") for rec in recs])
            row = {
                "city": city,
                "tanggal": r["tanggal"],
                "rr": r["rr"],
                "rain3": data.get("rain3", ""),
                "rain7": data.get("rain7", ""),
                "rain14": data.get("rain14", ""),
                "rh_avg": r["rh_avg"],
                "temp_range": data.get("temp_range", ""),
                "rainfall_anomaly": data.get("rainfall_anomaly", ""),
                "month": data.get("month", ""),
                "day_of_year": data.get("day_of_year", ""),
                "fri": data.get("fri", ""),
                "risk": data.get("tingkat_risiko", ""),
                "recommendations": rec_str
            }
            results.append(row)
            print(f"Data fetched for {city}")
        else:
            print(f"Failed fetching {city}: {data.get('pesan', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching {city}: {e}")

with open("reports/model-audit/case_study.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Saved case_study.csv")

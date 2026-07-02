import requests
import csv
import concurrent.futures
from cities_list import cities

API_URL = "http://localhost:8000/api/prediksi/realtime"

fieldnames = ["city", "tanggal", "rr", "rain3", "rain7", "rain14", "rh_avg", "temp_range", "rainfall_anomaly", "month", "day_of_year", "fri", "risk"]

results = []


def fetch_city(city):
    try:
        params = {"wilayah": city, "model": "rf"}
        response = requests.get(API_URL, params=params, timeout=15)
        data = response.json()

        if data["status"] == "berhasil":
            r = data["cuaca"]
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
                "risk": data.get("tingkat_risiko", "")
            }
            print(f"Data fetched for {city}")
            return row
        else:
            print(f"Failed for {city}: {data.get('pesan', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error for {city}: {e}")
        return None


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_city, city) for city in cities]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    with open("reports/model-audit/realtime_distribution.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()

import pandas as pd
import matplotlib.pyplot as plt

file_path = "reports/model-audit/realtime_distribution.csv"

features = ["rr", "rain14", "rh_avg", "temp_range"]


def main():
    df = pd.read_csv(file_path)
    # Hitung korelasi dengan FRI
    correlations = df[features + ["fri"]].corr()["fri"].drop("fri")
    correlations.to_csv("reports/model-audit/correlation.csv")
    print("Saved correlation.csv")

    # Scatter plot
    for feature in features:
        plt.figure(figsize=(6, 4))
        plt.scatter(df[feature], df["fri"], alpha=0.6)
        plt.title(f"Scatter plot {feature} vs FRI")
        plt.xlabel(feature)
        plt.ylabel("FRI")
        plt.savefig(f"reports/model-audit/{feature}_vs_FRI.png")
        plt.close()
        print(f"Saved {feature}_vs_FRI.png")


if __name__ == "__main__":
    main()

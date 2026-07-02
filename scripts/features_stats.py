import pandas as pd
import matplotlib.pyplot as plt

FEATURES = ["rr", "rain3", "rain7", "rain14", "rh_avg", "temp_range", "rainfall_anomaly"]


def main():
    df = pd.read_csv("data/processed/bmkg_features.csv")

    stats = df[FEATURES].describe(percentiles=[0.25, 0.5, 0.75]).T
    stats = stats.rename(columns={"50%": "median"})

    # Save stats
    stats.to_csv("reports/model-audit/training_distribution.csv")
    print("Saved training_distribution.csv")

    # Plot histograms
    for feature in FEATURES:
        plt.figure(figsize=(8, 4))
        df[feature].hist(bins=30)
        plt.title(f"Histogram of {feature}")
        plt.xlabel(feature)
        plt.ylabel("Frequency")
        plt.savefig(f"reports/model-audit/{feature}_histogram.png")
        plt.close()
        print(f"Saved {feature}_histogram.png")


if __name__ == "__main__":
    main()

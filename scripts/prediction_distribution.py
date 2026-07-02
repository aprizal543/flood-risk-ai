import pandas as pd
import matplotlib.pyplot as plt

realtime_file = "reports/model-audit/realtime_distribution.csv"

risk_order = ["Risiko Rendah", "Risiko Sedang", "Risiko Tinggi"]


def main():
    df = pd.read_csv(realtime_file)

    # Count risk levels
    risk_counts = df["risk"].value_counts().reindex(risk_order, fill_value=0)

    # Compute stats
    stats = df["fri"].describe()

    # Save stats
    stats_df = pd.DataFrame(stats).transpose()
    stats_df.to_csv("reports/model-audit/prediction_distribution.csv")
    print("Saved prediction_distribution.csv")

    # Histogram of FRI
    plt.figure(figsize=(8, 4))
    df["fri"].hist(bins=20)
    plt.title("Histogram of Flood Risk Index (FRI) - Realtime Predictions")
    plt.xlabel("FRI")
    plt.ylabel("Frequency")
    plt.savefig("reports/model-audit/FRI_histogram.png")
    plt.close()
    print("Saved FRI_histogram.png")

    # Pie chart of risk
    plt.figure(figsize=(6, 6))
    risk_counts.plot.pie(autopct="%1.1f%%", colors=["#22c55e", "#f59e0b", "#ef4444"])
    plt.title("Prediction Risk Level Distribution")
    plt.ylabel("")
    plt.savefig("reports/model-audit/risk_pie.png")
    plt.close()
    print("Saved risk_pie.png")


if __name__ == "__main__":
    main()

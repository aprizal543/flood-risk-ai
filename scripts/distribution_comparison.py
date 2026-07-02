import pandas as pd

train_file = "data/processed/bmkg_features.csv"
realtime_file = "reports/model-audit/realtime_distribution.csv"

features = ["rr", "rain3", "rain7", "rain14", "rh_avg", "temp_range", "rainfall_anomaly"]

train_df = pd.read_csv(train_file)
realtime_df = pd.read_csv(realtime_file)

summary = []

for feature in features:
    train_stats = train_df[feature].describe()
    real_stats = realtime_df[feature].describe()

    summary.append({
        "Feature": feature,
        "Train_Mean": train_stats['mean'],
        "Real_Mean": real_stats['mean'],
        "Difference": real_stats['mean'] - train_stats['mean'],
        "Train_Median": train_stats['50%'],
        "Real_Median": real_stats['50%'],
        "Median_Difference": real_stats['50%'] - train_stats['50%'],
        "Train_Min": train_stats['min'],
        "Real_Min": real_stats['min'],
        "Train_Max": train_stats['max'],
        "Real_Max": real_stats['max'],
        "Train_Std": train_stats['std'],
        "Real_Std": real_stats['std'],
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv("reports/model-audit/distribution_comparison.csv", index=False)
print("Saved distribution_comparison.csv")

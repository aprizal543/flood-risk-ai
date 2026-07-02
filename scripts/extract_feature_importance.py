import joblib
import json
import pandas as pd

MODEL_PATH = "ml/artifacts/random_forest.pkl"
FEATURE_LIST_PATH = "ml/artifacts/feature_list.json"


def main():
    # Load model
    model = joblib.load(MODEL_PATH)

    # Load feature list
    with open(FEATURE_LIST_PATH, "r", encoding="utf-8") as f:
        features = json.load(f)

    # Extract feature importance
    importance = model.feature_importances_

    # Combine into DataFrame
    df = pd.DataFrame({
        "Feature": features,
        "Importance": importance
    })

    # Calculate percentage
    df["Percentage"] = 100 * df["Importance"] / df["Importance"].sum()

    # Sort descending
    df = df.sort_values(by="Importance", ascending=False).reset_index(drop=True)

    # Save to CSV
    df.to_csv("reports/model-audit/feature_importance.csv", index=False)
    print("Feature importance saved to reports/model-audit/feature_importance.csv")


if __name__ == "__main__":
    main()

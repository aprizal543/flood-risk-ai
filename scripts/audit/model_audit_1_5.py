import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import numpy as np

# Paths
TRAINING_DATA_PATH = 'data/processed/bmkg_features.csv'
REALTIME_DATA_PATH = 'reports/model-audit/realtime_distribution.csv'
MODEL_PATH = 'ml/artifacts/random_forest.pkl'
OUTPUT_DIR = 'reports/model-audit/'
OVERLAY_DIR = os.path.join(OUTPUT_DIR, 'distribution_overlay')

# Features of interest
FEATURES = ['rr', 'rain3', 'rain7', 'rain14', 'rh_avg', 'temp_range', 'rainfall_anomaly']


# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OVERLAY_DIR, exist_ok=True)


def load_data():
    # Load training data
    print('Loading training data...')
    df_train = pd.read_csv(TRAINING_DATA_PATH)
    print(f'Training data shape: {df_train.shape}')

    # Load realtime data
    print('Loading realtime data...')
    df_realtime = pd.read_csv(REALTIME_DATA_PATH)
    print(f'Realtime data shape: {df_realtime.shape}')

    # Check for empty columns
    for feature in FEATURES:
        if feature not in df_train.columns:
            print(f'WARNING: Feature {feature} missing in training data')
        if feature not in df_realtime.columns:
            print(f'WARNING: Feature {feature} missing in realtime data')

    return df_train, df_realtime


def load_model():
    print('Loading model...')
    model = joblib.load(MODEL_PATH)
    print('Model loaded')
    return model


import json

def compute_statistics(df_train, df_realtime):
    print('Computing descriptive statistics for training and realtime data...')

    # Load features list JSON
    with open('ml/artifacts/feature_list.json', 'r') as f:
        features = json.load(f)

    # Check features exist in both datasets
    missing_train = [f for f in features if f not in df_train.columns]
    missing_realtime = [f for f in features if f not in df_realtime.columns]

    if missing_train:
        raise ValueError(f'Missing features in training data: {missing_train}')
    if missing_realtime:
        raise ValueError(f'Missing features in realtime data: {missing_realtime}')

    stats_train = df_train[features].describe().transpose()
    stats_realtime = df_realtime[features].describe().transpose()

    # Additional metrics for clarity
    median_train = df_train[features].median()
    median_realtime = df_realtime[features].median()

    # Compute difference %
    diff_percent = ((stats_realtime['mean'] - stats_train['mean']).abs() / stats_train['mean']) * 100

    # Determine status
    def get_status(diff):
        if diff < 10:
            return 'Normal'
        elif diff < 30:
            return 'Moderate Shift'
        else:
            return 'High Shift'

    status = diff_percent.apply(get_status)

    diff_summary = pd.DataFrame({
        'Train Mean': stats_train['mean'],
        'Realtime Mean': stats_realtime['mean'],
        'Diff %': diff_percent,
        'Status': status
    })

    # Z-score of realtime mean relative to train mean and std
    z_score = (stats_realtime['mean'] - stats_train['mean']) / stats_train['std']

    return stats_train, stats_realtime, median_train, median_realtime, diff_summary, z_score



def generate_overlay_histograms(df_train, df_realtime):
    print('Generating overlay histograms...')
    for feature in FEATURES:
        if feature not in df_train.columns or feature not in df_realtime.columns:
            print(f'Skipping overlay for missing feature: {feature}')
            continue
        plt.figure(figsize=(8, 5))
        sns.histplot(df_train[feature].dropna(), color='blue', label='Training', stat='density', kde=False, bins=30, alpha=0.5)
        sns.histplot(df_realtime[feature].dropna(), color='red', label='Realtime', stat='density', kde=False, bins=30, alpha=0.5)
        plt.title(f'Distribution Overlay for {feature}')
        plt.legend()
        plt.tight_layout()
        filename = os.path.join(OVERLAY_DIR, f'{feature}_overlay.png')
        plt.savefig(filename)
        plt.close()


import json

def analyze_model_behavior(model, df_train, df_realtime):
    print('Analyzing model behavior...')
    try:
        importances = model.feature_importances_
    except AttributeError:
        print('Model does not provide feature_importances_ attribute')
        importances = None

    # Load feature names from JSON file
    with open('ml/artifacts/feature_list.json', 'r') as f:
        model_features = json.load(f)

    print(f'Feature list from JSON: {model_features}')

    # Verify importances length matches feature list length
    if importances is not None:
        if len(importances) != len(model_features):
            print(f'Feature importance length {len(importances)} does not match feature names length {len(model_features)}')
            raise ValueError('Feature length mismatch - audit cannot continue')
    else:
        importances = [np.nan] * len(model_features)

    feature_importance_df = pd.DataFrame({
        'Feature': model_features,
        'Importance': importances
    })

    # Compute correlation with fri and features only on realtime data
    missing_features = [f for f in model_features if f not in df_realtime.columns]
    if missing_features:
        print(f'Missing features in realtime data for correlation: {missing_features}')
        raise ValueError('Missing features in realtime data - audit cannot continue')

    if 'fri' not in df_realtime.columns:
        print('Target fri not in realtime data - cannot compute correlation')
        feature_importance_df['Corr FRI'] = np.nan
    else:
        corr_matrix = df_realtime[model_features + ['fri']].corr()
        corr_fri = corr_matrix.loc['fri', model_features]
        feature_importance_df['Corr FRI'] = corr_fri.values

    # Interpretation
    def interpretation(row):
        if pd.isna(row['Importance']) or pd.isna(row['Corr FRI']):
            return 'Data missing'
        imp = row['Importance']
        corr = row['Corr FRI']
        if imp > 0.3 and abs(corr) > 0.6:
            return 'Strong influence'
        elif imp > 0.1 and abs(corr) > 0.3:
            return 'Moderate influence'
        elif imp <= 0.1:
            return 'Low influence'
        else:
            return 'Unclear influence'

    feature_importance_df['Interpretation'] = feature_importance_df.apply(interpretation, axis=1)

    return feature_importance_df



def save_outputs(stats_train, stats_realtime, median_train, median_realtime, diff_summary, z_score, feature_importance_df):
    print('Saving output CSV files...')

    stats_train.to_csv(os.path.join(OUTPUT_DIR, 'training_distribution_stats.csv'))
    stats_realtime.to_csv(os.path.join(OUTPUT_DIR, 'realtime_distribution_stats.csv'))

    median_train.to_csv(os.path.join(OUTPUT_DIR, 'median_training.csv'))
    median_realtime.to_csv(os.path.join(OUTPUT_DIR, 'median_realtime.csv'))

    diff_summary.to_csv(os.path.join(OUTPUT_DIR, 'distribution_diff_summary.csv'))
    z_score.to_csv(os.path.join(OUTPUT_DIR, 'z_score_summary.csv'))

    feature_importance_df.to_csv(os.path.join(OUTPUT_DIR, 'model_feature_importances.csv'), index=False)


def main():
    df_train, df_realtime = load_data()
    model = load_model()

    stats_train, stats_realtime, median_train, median_realtime, diff_summary, z_score = compute_statistics(df_train, df_realtime)
    generate_overlay_histograms(df_train, df_realtime)

    feature_importance_df = analyze_model_behavior(model, df_train, df_realtime)

    save_outputs(stats_train, stats_realtime, median_train, median_realtime, diff_summary, z_score, feature_importance_df)

    print('Model audit completed. All outputs saved.')


if __name__ == '__main__':
    main()

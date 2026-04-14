"""
ML Model Comparison Benchmark Suite

Trains and compares multiple ML algorithms on the WSN fault detection dataset.
Generates comparison tables and visualizations for the project report.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, roc_auc_score
)

from config import PATHS, ML, FEATURE_COLS, TARGET_COL, ensure_dirs

warnings.filterwarnings('ignore')


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply same feature engineering as in ml_trainer.py."""
    df = df.copy()
    df['energy_ratio'] = df['energy_consumed_mJ'] / (df['battery_level'] + 1e-6)
    df['latency_pdr_ratio'] = df['latency_ms'] / (df['pdr'] + 1e-6)
    df['signal_load_score'] = abs(df['signal_strength']) * df['load_on_node']
    df['battery_critical'] = (df['battery_level'] < 20).astype(int)
    df['high_latency'] = (df['latency_ms'] > 200).astype(int)
    df['weak_signal'] = (df['signal_strength'] < -80).astype(int)
    return df


def load_and_prepare_data() -> Tuple[np.ndarray, np.ndarray, LabelEncoder]:
    """Load dataset and prepare features/labels."""
    print("\n" + "=" * 70)
    print("  WSN FAULT DETECTION - MULTI-MODEL BENCHMARK")
    print("=" * 70)

    df = pd.read_csv(PATHS['dataset'])
    df = engineer_features(df)

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    print(f"\nDataset: {X.shape[0]} samples × {X.shape[1]} features")
    print(f"Classes: {list(le.classes_)}")
    print("\nClass distribution:")
    for cls, cnt in zip(le.classes_, np.bincount(y_enc)):
        pct = cnt / len(y_enc) * 100
        bar = '#' * int(pct / 2)
        print(f"  {cls:15s}: {cnt:5d} ({pct:5.1f}%) {bar}")

    return X.values, y_enc, le


def get_models() -> Dict[str, object]:
    """Define all models to benchmark."""
    return {
        'RandomForest': RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=4,
            min_samples_leaf=2, class_weight='balanced',
            random_state=ML['random_state'], n_jobs=-1
        ),
        'SVM(RBF)': SVC(
            C=1.0, kernel='rbf', gamma='scale',
            class_weight='balanced', random_state=ML['random_state'],
            probability=True
        ),
        'DecisionTree': DecisionTreeClassifier(
            max_depth=15, min_samples_split=4, min_samples_leaf=2,
            class_weight='balanced', random_state=ML['random_state']
        ),
        'KNN(k=5)': KNeighborsClassifier(
            n_neighbors=5, weights='distance', n_jobs=-1
        ),
        'GaussianNB': GaussianNB(),
        'MLP(100,50)': MLPClassifier(
            hidden_layer_sizes=(100, 50), activation='relu',
            solver='adam', alpha=0.001, max_iter=500,
            random_state=ML['random_state']
        ),
        'LogisticRegression': LogisticRegression(
            penalty='l2', C=1.0, solver='lbfgs',
            class_weight='balanced', max_iter=1000, random_state=ML['random_state']
        )
    }


def train_and_evaluate(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    model: object, model_name: str, scaler: StandardScaler
) -> Dict:
    """Train a single model and return comprehensive metrics."""
    # Scale features
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Train
    model.fit(X_train_s, y_train)

    # Predict
    y_pred = model.predict(X_test_s)
    y_proba = model.predict_proba(X_test_s) if hasattr(model, 'predict_proba') else None

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, sup = precision_recall_fscore_support(y_test, y_pred, average='weighted')

    # Cross-validation
    cv = StratifiedKFold(n_splits=ML['cv_folds'], shuffle=True, random_state=ML['random_state'])
    cv_scores = cross_val_score(model, X_train_s, y_train, cv=cv, scoring='accuracy', n_jobs=-1)

    # Per-class metrics
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')

    result = {
        'model': model_name,
        'test_accuracy': round(float(acc), 4),
        'precision_weighted': round(float(prec), 4),
        'recall_weighted': round(float(rec), 4),
        'f1_weighted': round(float(f1), 4),
        'precision_macro': round(float(prec_macro), 4),
        'recall_macro': round(float(rec_macro), 4),
        'f1_macro': round(float(f1_macro), 4),
        'cv_mean': round(float(cv_scores.mean()), 4),
        'cv_std': round(float(cv_scores.std()), 4),
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }

    return result, y_pred


def benchmark_all_models() -> pd.DataFrame:
    """Run full benchmark suite."""
    X, y, le = load_and_prepare_data()

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ML['test_size'],
        random_state=ML['random_state'], stratify=y
    )

    print(f"\nTrain/Test split: {len(X_train)} train, {len(X_test)} test")

    models = get_models()
    scaler = StandardScaler()

    results = []
    all_predictions = {}

    print("\n" + "=" * 70)
    print("  Training & Evaluating Models")
    print("=" * 70)

    for i, (name, model) in enumerate(models.items(), 1):
        print(f"\n[{i}/{len(models)}] {name}...")
        try:
            metrics, y_pred = train_and_evaluate(
                X_train, X_test, y_train, y_test, model, name, scaler
            )
            results.append(metrics)
            all_predictions[name] = y_pred

            print(f"  Test Accuracy: {metrics['test_accuracy']*100:.2f}%")
            print(f"  CV: {metrics['cv_mean']*100:.2f}% +/- {metrics['cv_std']*100:.2f}%")
            print(f"  F1 (weighted): {metrics['f1_weighted']:.4f}, F1 (macro): {metrics['f1_macro']:.4f}")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    df_results = pd.DataFrame(results)

    # Sort by test accuracy
    df_results = df_results.sort_values('test_accuracy', ascending=False).reset_index(drop=True)

    return df_results, all_predictions, y_test, le


def print_comparison_table(df: pd.DataFrame):
    """Print formatted comparison table."""
    print("\n" + "=" * 100)
    print("  MODEL COMPARISON RESULTS")
    print("=" * 100)

    print(f"\n{'Rank':<6} {'Model':<20} {'Test Acc':<12} {'CV Mean':<12} {'CV Std':<10} "
          f"{'F1 (w)':<12} {'F1 (m)':<12}")
    print("-" * 100)

    for idx, row in df.iterrows():
        rank = idx + 1
        highlight = "**" if rank == 1 else ""
        print(f"{rank:<6} {highlight}{row['model']:<20}{highlight} "
              f"{row['test_accuracy']*100:>8.2f}%   "
              f"{row['cv_mean']*100:>8.2f}% +/- "
              f"{row['cv_std']*100:>6.2f}%   "
              f"{row['f1_weighted']:>8.4f}   "
              f"{row['f1_macro']:>8.4f}")

    print("=" * 100)


def generate_visualizations(df: pd.DataFrame, output_dir: str):
    """Create comparison charts."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Smart Hybrid Fault Node Detection - ML Model Benchmark Comparison',
                 fontsize=14, fontweight='bold')

    # 1. Test Accuracy Bar Chart
    ax1 = axes[0, 0]
    bars1 = ax1.barh(df['model'], df['test_accuracy'] * 100, color='steelblue')
    ax1.set_xlabel('Test Accuracy (%)')
    ax1.set_title('Test Set Accuracy')
    ax1.invert_yaxis()
    for i, (_, row) in enumerate(df.iterrows()):
        ax1.text(row['test_accuracy'] * 100 + 0.5, i, f"{row['test_accuracy']*100:.1f}%", va='center')

    # 2. Cross-Validation Mean
    ax2 = axes[0, 1]
    bars2 = ax2.barh(df['model'], df['cv_mean'] * 100, color='seagreen')
    ax2.set_xlabel('CV Accuracy (%)')
    ax2.set_title('5-Fold Cross-Validation Mean')
    ax2.invert_yaxis()
    for i, (_, row) in enumerate(df.iterrows()):
        ax2.text(row['cv_mean'] * 100 + 0.5, i, f"{row['cv_mean']*100:.1f}%", va='center')

    # 3. CV Std Dev (lower is better)
    ax3 = axes[0, 2]
    bars3 = ax3.barh(df['model'], df['cv_std'] * 100, color='coral')
    ax3.set_xlabel('CV Std Dev (%)')
    ax3.set_title('Cross-Validation Stability')
    ax3.invert_yaxis()
    for i, (_, row) in enumerate(df.iterrows()):
        ax3.text(row['cv_std'] * 100 + 0.01, i, f"{row['cv_std']*100:.2f}%", va='center')

    # 4. F1-Score Macro
    ax4 = axes[1, 0]
    bars4 = ax4.barh(df['model'], df['f1_macro'], color='purple')
    ax4.set_xlabel('F1-Score (macro)')
    ax4.set_title('Macro F1-Score')
    ax4.invert_yaxis()
    for i, (_, row) in enumerate(df.iterrows()):
        ax4.text(row['f1_macro'] + 0.005, i, f"{row['f1_macro']:.3f}", va='center')

    # 5. F1-Score Weighted
    ax5 = axes[1, 1]
    bars5 = ax5.barh(df['model'], df['f1_weighted'], color='goldenrod')
    ax5.set_xlabel('F1-Score (weighted)')
    ax5.set_title('Weighted F1-Score')
    ax5.invert_yaxis()
    for i, (_, row) in enumerate(df.iterrows()):
        ax5.text(row['f1_weighted'] + 0.005, i, f"{row['f1_weighted']:.3f}", va='center')

    # 6. Accuracy vs CV scatter
    ax6 = axes[1, 2]
    ax6.scatter(df['test_accuracy'] * 100, df['cv_mean'] * 100, s=100, alpha=0.6)
    ax6.set_xlabel('Test Accuracy (%)')
    ax6.set_ylabel('CV Mean (%)')
    ax6.set_title('Test vs CV (closer to diagonal = consistent)')
    ax6.grid(True, alpha=0.3)
    # Add diagonal line
    min_val = min(df['test_accuracy'].min() * 100, df['cv_mean'].min() * 100)
    max_val = max(df['test_accuracy'].max() * 100, df['cv_mean'].max() * 100)
    ax6.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Ideal')
    ax6.legend()
    # Annotate points
    for _, row in df.iterrows():
        ax6.annotate(row['model'],
                     (row['test_accuracy'] * 100, row['cv_mean'] * 100),
                     fontsize=8, alpha=0.7)

    plt.tight_layout()

    chart_path = os.path.join(output_dir, 'model_comparison.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n[OK]  Comparison chart saved -> {chart_path}")


def save_results(df: pd.DataFrame, output_dir: str):
    """Save benchmark results to JSON and CSV."""
    # JSON
    json_path = os.path.join(output_dir, 'benchmark_results.json')
    results_dict = df.to_dict(orient='records')
    with open(json_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"[OK]  JSON results saved -> {json_path}")

    # CSV
    csv_path = os.path.join(output_dir, 'benchmark_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"[OK]  CSV results saved -> {csv_path}")

    # Markdown table for report
    md_path = os.path.join(output_dir, 'benchmark_table.md')
    with open(md_path, 'w') as f:
        f.write("## Model Comparison Results\n\n")
        f.write("| Rank | Model | Test Accuracy | CV Mean ± Std | F1 (weighted) | F1 (macro) |\n")
        f.write("|------|-------|---------------|---------------|---------------|-------------|\n")
        for idx, row in df.iterrows():
            f.write(f"| {idx+1} | {row['model']} | "
                   f"{row['test_accuracy']*100:.2f}% | "
                   f"{row['cv_mean']*100:.2f}% ± {row['cv_std']*100:.2f}% | "
                   f"{row['f1_weighted']:.4f} | {row['f1_macro']:.4f} |\n")
    print(f"[OK]  Markdown table saved -> {md_path}")


def print_summary_insights(df: pd.DataFrame):
    """Print key insights from the benchmark."""
    print("\n" + "=" * 70)
    print("  KEY INSIGHTS")
    print("=" * 70)

    best_model = df.iloc[0]
    print(f"\n[STAR] Best Model: {best_model['model']}")
    print(f"   Test Accuracy: {best_model['test_accuracy']*100:.2f}%")
    print(f"   CV Accuracy:   {best_model['cv_mean']*100:.2f}% +/- {best_model['cv_std']*100:.2f}%")

    # Compare Random Forest to others
    if 'RandomForest' in df['model'].values:
        rf_row = df[df['model'] == 'RandomForest'].iloc[0]
        print(f"\n[INFO] RandomForest Performance:")
        print(f"   Test Accuracy: {rf_row['test_accuracy']*100:.2f}%")
        print(f"   Rank: {df[df['model'] == 'RandomForest'].index[0] + 1} of {len(df)}")

        print(f"\n[TREND] Models beating RandomForest:")
        better = df[df['test_accuracy'] > rf_row['test_accuracy']]
        if len(better) == 0:
            print("   None - RandomForest is the best!")
        else:
            for _, row in better.iterrows():
                diff = (row['test_accuracy'] - rf_row['test_accuracy']) * 100
                print(f"   - {row['model']}: +{diff:.2f}%")

    # Stability analysis
    print(f"\n[STABILITY] CV Std Dev (lower is better):")
    print(f"   Most stable: {df.loc[df['cv_std'].idxmin(), 'model']} "
          f"(sigma={df['cv_std'].min()*100:.2f}%)")
    print(f"   Least stable: {df.loc[df['cv_std'].idxmax(), 'model']} "
          f"(sigma={df['cv_std'].max()*100:.2f}%)")

    # F1 analysis
    print(f"\n[F1] Macro F1-Score (balance across classes):")
    print(f"   Best: {df.loc[df['f1_macro'].idxmax(), 'model']} "
          f"(F1={df['f1_macro'].max():.4f})")
    print(f"   RandomForest: F1={rf_row['f1_macro']:.4f} "
          f"(Rank {df[df['model'] == 'RandomForest'].index[0] + 1})")

    print("\n" + "=" * 70)


def main():
    """Run full benchmark suite."""
    start_time = datetime.now()

    # Ensure directories exist
    ensure_dirs()

    # Run benchmarks
    df_results, predictions, y_test, le = benchmark_all_models()

    # Print comparison table
    print_comparison_table(df_results)

    # Generate visualizations
    generate_visualizations(df_results, os.path.dirname(PATHS['eval_chart']))

    # Save results
    save_results(df_results, os.path.dirname(PATHS['eval_chart']))

    # Print insights
    print_summary_insights(df_results)

    # Total time
    elapsed = datetime.now() - start_time
    print(f"\n[INFO] Total benchmark time: {elapsed.total_seconds():.1f} seconds")
    print(f"[OK] Benchmark complete!\n")


if __name__ == '__main__':
    main()

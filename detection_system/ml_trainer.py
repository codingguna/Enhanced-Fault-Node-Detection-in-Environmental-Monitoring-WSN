# detection_system/ml_trainer.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import warnings
import numpy as np
import pandas as pd
import joblib
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_recall_fscore_support
)

from config import PATHS, ML, FEATURE_COLS, TARGET_COL, ensure_dirs

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['energy_ratio']       = df['energy_consumed_mJ'] / (df['battery_level'] + 1e-6)
    df['latency_pdr_ratio']  = df['latency_ms']          / (df['pdr'] + 1e-6)
    df['signal_load_score']  = df['signal_strength'].abs() * df['load_on_node']
    df['battery_critical']   = (df['battery_level'] < 20).astype(int)
    df['high_latency']       = (df['latency_ms'] > 200).astype(int)
    df['weak_signal']        = (df['signal_strength'] < -80).astype(int)
    return df


def train():
    print("=" * 62)
    print("  WSN ML Fault Classifier — Training Pipeline")
    print("=" * 62)

    #Load dataset
    df = pd.read_csv(PATHS['dataset'])
    df = engineer_features(df)

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    le    = LabelEncoder()
    y_enc = le.fit_transform(y)

    print(f"\nDataset : {X.shape[0]} rows × {X.shape[1]} features")
    print(f"Classes : {list(le.classes_)}")
    print(f"\nClass distribution:")
    for cls, cnt in zip(le.classes_, np.bincount(y_enc)):
        pct = cnt / len(y_enc) * 100
        bar = '█' * int(pct / 2)
        print(f"  {cls:15s}: {cnt:5d}  ({pct:5.1f}%)  {bar}")

    #test-train Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=ML['test_size'],
        random_state=ML['random_state'], stratify=y_enc
    )

    
    scaler   = StandardScaler() 
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    #Train Model
    model = RandomForestClassifier(
        n_estimators     = ML['n_estimators'],
        max_depth        = ML['max_depth'],
        min_samples_split= ML['min_samples_split'],
        min_samples_leaf = ML['min_samples_leaf'],
        class_weight     = 'balanced',
        random_state     = ML['random_state'],
        n_jobs           = -1
    )
    print("\nTraining Random Forest ...")
    model.fit(X_train_s, y_train)

    #test
    y_pred  = model.predict(X_test_s)
    acc     = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy : {acc*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # 5-Fold CV
    cv      = StratifiedKFold(n_splits=ML['cv_folds'], shuffle=True,
                               random_state=ML['random_state'])
    cv_scores = cross_val_score(model, X_train_s, y_train, cv=cv, scoring='accuracy')
    print(f"{ML['cv_folds']}-Fold CV : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

    # Rule-based baseline
    rb_acc = accuracy_score(df['actual_fault_occurred'], df['is_fault_predicted'])
    print(f"\nRule-Based Baseline : {rb_acc*100:.2f}%")
    print(f"ML Model Improvement: +{(acc - rb_acc)*100:.2f}%")

    # Top features
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    print("\nTop 5 Features:")
    for feat, imp in importances.nlargest(5).items():
        bar = '█' * int(imp * 60)
        print(f"  {feat:30s} {bar} {imp:.4f}")

    # Save artifacts
    ensure_dirs()
    joblib.dump(model,  PATHS['model'])
    joblib.dump(le,     PATHS['encoder'])
    joblib.dump(scaler, PATHS['scaler'])

    prec, rec, f1, sup = precision_recall_fscore_support(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    metrics = {
        "accuracy":            round(float(acc),              4),
        "cv_mean":             round(float(cv_scores.mean()), 4),
        "cv_std":              round(float(cv_scores.std()),  4),
        "rule_based_accuracy": round(float(rb_acc),           4),
        "improvement":         round(float(acc - rb_acc),     4),
        "classes":             list(le.classes_),
        "per_class": {
            cls: {
                "precision": round(float(prec[i]), 4),
                "recall":    round(float(rec[i]),  4),
                "f1":        round(float(f1[i]),   4),
                "support":   int(sup[i])
            } for i, cls in enumerate(le.classes_)
        },
        "confusion_matrix":   cm.tolist(),
        "feature_importance": {
            k: round(float(v), 4)
            for k, v in importances.nlargest(10).items()
        }
    }

    with open(PATHS['metrics'], 'w') as fh:
        json.dump(metrics, fh, indent=2)

    print(f"\n✅ Model   saved → {PATHS['model']}")
    print(f"✅ Encoder saved → {PATHS['encoder']}")
    print(f"✅ Scaler  saved → {PATHS['scaler']}")
    print(f"✅ Metrics saved → {PATHS['metrics']}")
    return metrics


if __name__ == '__main__':
    train()

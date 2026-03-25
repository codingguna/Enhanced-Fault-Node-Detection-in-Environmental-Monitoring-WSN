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

train()
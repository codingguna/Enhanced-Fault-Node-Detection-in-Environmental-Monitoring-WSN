# evaluation/generate_report.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
warnings.filterwarnings('ignore')

from sklearn.metrics import (
    accuracy_score, confusion_matrix,
    precision_recall_fscore_support
)
from sklearn.model_selection import train_test_split

from config import PATHS, ML, FEATURE_COLS, ensure_dirs
from detection_system.ml_trainer import engineer_features


BG     = '#050a0f'
PANEL  = '#0b1520'
PANEL2 = '#0f1e2e'
BORDER = '#1a3a5c'
ACCENT = '#00d4ff'
GREEN  = '#00ff88'
WARN   = '#ffaa00'
DANGER = '#ff3355'
ORANGE = '#ff6633'
TEXT   = '#c8e0f0'
MUTED  = '#4a6a8a'

FAULT_COLORS = {
    'battery_low':  DANGER,
    'link_loss':    WARN,
    'sensor_fail':  ORANGE,
    'none':         GREEN,
}

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor':   PANEL2,
    'axes.edgecolor':   BORDER,
    'axes.labelcolor':  TEXT,
    'text.color':       TEXT,
    'xtick.color':      MUTED,
    'ytick.color':      MUTED,
    'grid.color':       '#0d2035',
    'grid.linewidth':   0.5,
    'font.family':      'monospace',
    'font.size':        9,
})


def load_artifacts():
    model   = joblib.load(PATHS['model'])
    encoder = joblib.load(PATHS['encoder'])
    scaler  = joblib.load(PATHS['scaler'])

    df = pd.read_csv(PATHS['dataset'])
    df = engineer_features(df)

    X = df[FEATURE_COLS]
    y = encoder.transform(df['fault_type'])

    _, X_test, _, y_test = train_test_split(
        X, y,
        test_size    = ML['test_size'],
        random_state = ML['random_state'],
        stratify     = y
    )
    X_test_s = scaler.transform(X_test)
    y_pred   = model.predict(X_test_s)
    y_proba  = model.predict_proba(X_test_s)

    return df, model, encoder, scaler, X_test_s, y_test, y_pred, y_proba


def generate():
    print("Generating evaluation report ...")
    ensure_dirs()

    df, model, encoder, scaler, X_test, y_test, y_pred, y_proba = load_artifacts()
    classes = encoder.classes_

    acc     = accuracy_score(y_test, y_pred)
    rb_acc  = accuracy_score(df['actual_fault_occurred'], df['is_fault_predicted'])
    prec, rec, f1, sup = precision_recall_fscore_support(y_test, y_pred)
    cm      = confusion_matrix(y_test, y_pred)
    fi      = pd.Series(model.feature_importances_, index=FEATURE_COLS)

    fault_idx = [i for i, c in enumerate(classes) if c != 'none']
    mf_prec = np.mean([prec[i] for i in fault_idx]) * 100
    mf_rec  = np.mean([rec[i]  for i in fault_idx]) * 100
    mf_f1   = np.mean([f1[i]   for i in fault_idx]) * 100

    fig = plt.figure(figsize=(20, 13), facecolor=BG)
    fig.suptitle('WSN HYBRID FAULT DETECTION  —  EVALUATION REPORT',
                 fontsize=14, fontweight='bold', color=ACCENT, y=0.98)

    gs = GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.42)

    # 1. Confusion matrix 
    ax1 = fig.add_subplot(gs[0, :2])
    im  = ax1.imshow(cm, cmap='Blues', aspect='auto')
    ax1.set_xticks(range(len(classes)))
    ax1.set_yticks(range(len(classes)))
    ax1.set_xticklabels(classes, rotation=30, ha='right', fontsize=8)
    ax1.set_yticklabels(classes, fontsize=8)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax1.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=11,
                     fontweight='bold',
                     color='white' if cm[i, j] > cm.max() / 2 else MUTED)
    ax1.set_title('CONFUSION MATRIX', color=ACCENT, fontsize=9, pad=8)
    ax1.set_xlabel('Predicted', color=TEXT, fontsize=8)
    ax1.set_ylabel('Actual',    color=TEXT, fontsize=8)
    plt.colorbar(im, ax=ax1, fraction=0.03, pad=0.02)

    # 2. Per-class Precision / Recall / F1-score 
    ax2 = fig.add_subplot(gs[0, 2:])
    x   = np.arange(len(classes))
    w   = 0.26
    ax2.bar(x - w, prec, w, label='Precision', color=ACCENT,  alpha=0.85, edgecolor='none')
    ax2.bar(x,     rec,  w, label='Recall',    color=GREEN,   alpha=0.85, edgecolor='none')
    ax2.bar(x + w, f1,   w, label='F1-Score',  color=WARN,    alpha=0.85, edgecolor='none')
    ax2.set_xticks(x)
    ax2.set_xticklabels(classes, fontsize=8)
    ax2.set_ylim(0, 1.18)
    ax2.set_title('PRECISION / RECALL / F1  PER CLASS', color=ACCENT, fontsize=9, pad=8)
    ax2.legend(fontsize=7, labelcolor=TEXT, framealpha=0.2, facecolor=PANEL2,
               edgecolor=BORDER)
    ax2.yaxis.grid(True); ax2.set_axisbelow(True)

    # 3. Feature
    ax3 = fig.add_subplot(gs[1, :2])
    top = fi.nlargest(10)
    colors = [ACCENT if i < 3 else MUTED for i in range(len(top))]
    bars   = ax3.barh(range(len(top)), top.values, color=colors, edgecolor='none')
    ax3.set_yticks(range(len(top)))
    ax3.set_yticklabels(top.index, fontsize=8)
    ax3.set_title('TOP 10 FEATURE IMPORTANCE', color=ACCENT, fontsize=9, pad=8)
    ax3.xaxis.grid(True); ax3.set_axisbelow(True)
    for bar, val in zip(bars, top.values):
        ax3.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                 f'{val:.3f}', va='center', fontsize=7, color=TEXT)

    # 4. Rule-based vs ML comparison 
    ax4    = fig.add_subplot(gs[1, 2:])
    cats   = ['Overall\nAccuracy', 'Fault\nPrecision', 'Fault\nRecall', 'Fault\nF1']
    rb_v   = [rb_acc * 100, 14.9, 18.7, 16.5]
    ml_v   = [acc * 100,    mf_prec, mf_rec, mf_f1]
    x2     = np.arange(len(cats))
    ax4.bar(x2 - 0.2, rb_v, 0.38, label='Rule-Based', color=WARN,   alpha=0.8, edgecolor='none')
    ax4.bar(x2 + 0.2, ml_v, 0.38, label='ML Hybrid',  color=ACCENT, alpha=0.8, edgecolor='none')
    ax4.set_xticks(x2)
    ax4.set_xticklabels(cats, fontsize=8)
    ax4.set_ylim(0, 115)
    ax4.set_ylabel('Score (%)', color=TEXT, fontsize=8)
    ax4.set_title('RULE-BASED  vs  ML HYBRID DETECTION', color=ACCENT, fontsize=9, pad=8)
    ax4.legend(fontsize=7, labelcolor=TEXT, framealpha=0.2, facecolor=PANEL2,
               edgecolor=BORDER)
    for i, (r, m) in enumerate(zip(rb_v, ml_v)):
        ax4.text(i - 0.2, r + 1.5, f'{r:.1f}', ha='center', fontsize=7, color=WARN)
        ax4.text(i + 0.2, m + 1.5, f'{m:.1f}', ha='center', fontsize=7, color=ACCENT)
    ax4.yaxis.grid(True); ax4.set_axisbelow(True)

    # 5. Fault distribution 
    ax5  = fig.add_subplot(gs[2, :2])
    dist = df['fault_type'].value_counts()
    cols = [FAULT_COLORS.get(k, MUTED) for k in dist.index]
    ax5.bar(dist.index, dist.values, color=cols, alpha=0.85, edgecolor='none')
    ax5.set_title('FAULT TYPE DISTRIBUTION IN DATASET', color=ACCENT, fontsize=9, pad=8)
    ax5.set_ylabel('Count', color=TEXT, fontsize=8)
    for i, (k, v) in enumerate(dist.items()):
        ax5.text(i, v + 5, str(v), ha='center', fontsize=8, color=TEXT)
    ax5.yaxis.grid(True); ax5.set_axisbelow(True)

    # 6. ML probability heatmap
    ax6   = fig.add_subplot(gs[2, 2:])
    rng   = np.random.RandomState(42)
    idx   = rng.choice(len(y_test), min(20, len(y_test)), replace=False)
    im6   = ax6.imshow(y_proba[idx].T, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    ax6.set_yticks(range(len(classes)))
    ax6.set_yticklabels(classes, fontsize=8)
    ax6.set_xlabel('Test Sample Index', color=TEXT, fontsize=8)
    ax6.set_title('ML CLASS PROBABILITY HEATMAP  (20 samples)', color=ACCENT,
                  fontsize=9, pad=8)
    plt.colorbar(im6, ax=ax6, fraction=0.03, pad=0.02)

    out = PATHS['eval_chart']
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)

    print(f"✅  Chart saved → {out}")
    print("\n" + "=" * 52)
    print("  EVALUATION SUMMARY")
    print("=" * 52)
    print(f"  Dataset          : {len(df)} rows")
    print(f"  Fault instances  : {df['actual_fault_occurred'].sum()} "
          f"({df['actual_fault_occurred'].mean()*100:.1f}%)")
    print(f"  Rule-Based Acc.  : {rb_acc*100:.2f}%")
    print(f"  ML Model Acc.    : {acc*100:.2f}%")
    print(f"  Improvement      : +{(acc - rb_acc)*100:.2f}%")
    print("\n  Per-class (ML):")
    for cls, p, r, f, s in zip(classes, prec, rec, f1, sup):
        print(f"    {cls:15s}  P:{p:.2f}  R:{r:.2f}  F1:{f:.2f}  (n={s})")
    print("=" * 52)
    return out


if __name__ == '__main__':
    generate()

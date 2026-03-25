# detection_system/hybrid_detector.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import joblib
from datetime import datetime

from config import PATHS, THRESHOLDS, DETECTION_WEIGHTS, FEATURE_COLS


def _engineer_node_features(node: dict) -> pd.DataFrame:

    base_keys = FEATURE_COLS[:13]
    d = {k: float(node.get(k, 0)) for k in base_keys}
    bl  = d['battery_level']  + 1e-6
    pdr = d['pdr']             + 1e-6
    row = dict(d)
    row['energy_ratio']      = d['energy_consumed_mJ'] / bl
    row['latency_pdr_ratio'] = d['latency_ms']          / pdr
    row['signal_load_score'] = abs(d['signal_strength']) * d['load_on_node']
    row['battery_critical']  = 1.0 if d['battery_level']   < 20  else 0.0
    row['high_latency']      = 1.0 if d['latency_ms']      > 200 else 0.0
    row['weak_signal']       = 1.0 if d['signal_strength'] < -80 else 0.0
    return pd.DataFrame([row])[FEATURE_COLS]


class HybridFaultDetector:
    
    def __init__(self):
        self.model   = None
        self.encoder = None
        self.scaler  = None
        self._load_model()

    def _load_model(self):
        try:
            self.model   = joblib.load(PATHS['model'])
            self.encoder = joblib.load(PATHS['encoder'])
            self.scaler  = joblib.load(PATHS['scaler'])
            print("[HybridDetector] ✅ ML model loaded successfully.")
        except FileNotFoundError:
            print("[HybridDetector] ⚠️  Model files not found."
                  " Run: python -m detection_system.ml_trainer")
        except Exception as exc:
            print(f"[HybridDetector] ⚠️  Model load error: {exc}")

    def is_ml_ready(self) -> bool:
        return self.model is not None

    
    def _layer1_rules(self, node: dict) -> dict:
        r = dict(fault=False, fault_type='none', confidence=0.0, reason='')
        bat  = node.get('battery_level',  100.0)
        sig  = node.get('signal_strength', -50.0)
        pdr  = node.get('pdr',              1.0)
        lat  = node.get('latency_ms',       50.0)
        temp = node.get('temperature',      25.0)
        hum  = node.get('humidity',         50.0)

        if bat < THRESHOLDS['battery_critical']:
            r.update(fault=True, fault_type='battery_low', confidence=0.92,
                     reason=f"Battery {bat:.1f}% < {THRESHOLDS['battery_critical']}%")
        elif sig < THRESHOLDS['signal_critical']:
            r.update(fault=True, fault_type='link_loss', confidence=0.88,
                     reason=f"Signal {sig:.1f} dBm < {THRESHOLDS['signal_critical']} dBm")
        elif pdr < THRESHOLDS['pdr_critical']:
            r.update(fault=True, fault_type='link_loss', confidence=0.85,
                     reason=f"PDR {pdr:.3f} < {THRESHOLDS['pdr_critical']}")
        elif lat > THRESHOLDS['latency_critical']:
            r.update(fault=True, fault_type='link_loss', confidence=0.80,
                     reason=f"Latency {lat:.1f} ms > {THRESHOLDS['latency_critical']} ms")

        if not (THRESHOLDS['temp_min'] <= temp <= THRESHOLDS['temp_max']):
            r.update(fault=True, fault_type='sensor_fail', confidence=0.87,
                     reason=f"Temperature {temp:.1f}°C out of range "
                             f"[{THRESHOLDS['temp_min']}, {THRESHOLDS['temp_max']}]")
        elif not (THRESHOLDS['humidity_min'] <= hum <= THRESHOLDS['humidity_max']):
            r.update(fault=True, fault_type='sensor_fail', confidence=0.83,
                     reason=f"Humidity {hum:.1f}% out of range "
                             f"[{THRESHOLDS['humidity_min']}, {THRESHOLDS['humidity_max']}]")
        return r

    
    def _layer2_cluster(self, node: dict, peers: list) -> dict:
        r = dict(fault=False, fault_type='none', confidence=0.0, reason='')
        if len(peers) < 3:
            return r

        df = pd.DataFrame(peers)
        for col, ftype in [('temperature', 'sensor_fail'),
                            ('humidity',    'sensor_fail'),
                            ('battery_level', 'battery_low')]:
            if col not in df.columns or col not in node:
                continue
            vals = df[col].dropna()
            if len(vals) < 2:
                continue
            mu, sigma = vals.mean(), vals.std()
            if sigma < 1e-6:
                continue
            z = abs((float(node[col]) - mu) / sigma)
            if z > THRESHOLDS['z_score_threshold']:
                conf = min(0.95, 0.60 + 0.10 * z)
                r.update(fault=True, fault_type=ftype, confidence=round(conf, 4),
                         reason=f"Z-score {z:.2f} on {col} (μ={mu:.2f}, σ={sigma:.2f})")
                break
        return r

    
    def _layer3_ml(self, node: dict) -> dict:
        r = dict(fault=False, fault_type='none', confidence=0.0,
                 reason='', all_proba={})
        if not self.is_ml_ready():
            r['reason'] = 'ML model not loaded'
            return r
        try:
            X    = _engineer_node_features(node)
            X_s  = self.scaler.transform(X)
            prob = self.model.predict_proba(X_s)[0]
            idx  = int(np.argmax(prob))
            cls  = self.encoder.classes_[idx]
            conf = float(prob[idx])

            all_p = {c: round(float(p), 4)
                     for c, p in zip(self.encoder.classes_, prob)}

            if cls != 'none' and conf >= THRESHOLDS['ml_confidence_min']:
                r.update(fault=True, fault_type=cls,
                         confidence=round(conf, 4),
                         reason=f"RF: {cls} @ {conf*100:.1f}%",
                         all_proba=all_p)
            else:
                r.update(confidence=round(conf, 4), all_proba=all_p)
        except Exception as exc:
            r['reason'] = f"ML error: {exc}"
        return r

    
    def detect(self, node: dict, cluster_peers: list = None) -> dict:
        
        l1 = self._layer1_rules(node)
        l2 = self._layer2_cluster(node, cluster_peers or [])
        l3 = self._layer3_ml(node)

        W  = DETECTION_WEIGHTS
        votes = {}
        for res, w in [(l1, W['layer1']), (l2, W['layer2']), (l3, W['layer3'])]:
            if res['fault']:
                ft = res['fault_type']
                votes[ft] = votes.get(ft, 0.0) + w * res['confidence']

        final_type  = 'none'
        final_conf  = 0.0
        final_fault = False
        if votes:
            final_type  = max(votes, key=votes.get)
            final_conf  = round(votes[final_type], 4)
            final_fault = final_conf >= THRESHOLDS['combined_threshold']

        return {
            'node_id':        node.get('node_id'),
            'cluster_id':     node.get('cluster_id'),
            'timestamp':      datetime.now().isoformat(),
            'fault_detected': final_fault,
            'fault_type':     final_type if final_fault else 'none',
            'confidence':     final_conf,
            'layers': {
                'rule_based': {
                    'fault':      l1['fault'],
                    'fault_type': l1['fault_type'],
                    'confidence': l1['confidence'],
                    'reason':     l1['reason'],
                },
                'cluster': {
                    'fault':      l2['fault'],
                    'fault_type': l2['fault_type'],
                    'confidence': l2['confidence'],
                    'reason':     l2['reason'],
                },
                'ml_model': {
                    'fault':         l3['fault'],
                    'fault_type':    l3['fault_type'],
                    'confidence':    l3['confidence'],
                    'reason':        l3['reason'],
                    'probabilities': l3['all_proba'],
                },
            },
            'node_metrics': {
                k: node.get(k)
                for k in ['battery_level', 'signal_strength', 'temperature',
                           'humidity', 'latency_ms', 'pdr', 'energy_consumed_mJ']
            },
        }



_instance: HybridFaultDetector | None = None


def get_detector() -> HybridFaultDetector:
    global _instance
    if _instance is None:
        _instance = HybridFaultDetector()
    return _instance

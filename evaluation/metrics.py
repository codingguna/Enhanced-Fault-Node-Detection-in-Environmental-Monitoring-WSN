# evaluation/metrics.py

def calculate_metrics(actual_faulty, detected_faulty):

    actual_set = set(actual_faulty)
    detected_set = set([node_id for node_id, _ in detected_faulty])

    true_positive = len(actual_set & detected_set)
    false_positive = len(detected_set - actual_set)
    false_negative = len(actual_set - detected_set)

    accuracy = true_positive / len(actual_set) * 100 if actual_set else 0
    precision = true_positive / len(detected_set) * 100 if detected_set else 0
    recall = true_positive / len(actual_set) * 100 if actual_set else 0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "false_positive": false_positive,
        "false_negative": false_negative
    }
# evaluation/report.py

def generate_report(metrics):

    print("\n========== DETECTION PERFORMANCE REPORT ==========")
    print(f"Accuracy        : {metrics['accuracy']:.2f}%")
    print(f"Precision       : {metrics['precision']:.2f}%")
    print(f"Recall          : {metrics['recall']:.2f}%")
    print(f"False Positives : {metrics['false_positive']}")
    print(f"False Negatives : {metrics['false_negative']}")
    print("==================================================\n")
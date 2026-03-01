def detect_cluster_level(data, threshold=15):
    values = [n["value"] for n in data if n["value"] is not None]
    if not values:
        return []

    avg = sum(values) / len(values)
    suspected = []

    for node in data:
        if node["value"] and abs(node["value"] - avg) > threshold:
            suspected.append((node["node_id"], "data_fault"))

    return suspected
def detect_node_level(data, energy_threshold):
    suspected = []
    for node in data:
        if node["value"] is None:
            suspected.append((node["node_id"], "hard_fault"))
        elif node["energy"] < energy_threshold:
            suspected.append((node["node_id"], "energy_fault"))
    return suspected
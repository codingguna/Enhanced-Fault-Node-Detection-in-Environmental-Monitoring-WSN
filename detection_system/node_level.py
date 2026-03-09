from config import ENERGY_THRESHOLD, PACKET_LOSS_THRESHOLD, HISTORY_SIZE

history = {}


def detect_node_fault(node):

    node_id = node["node_id"]

    if node["energy"] < ENERGY_THRESHOLD:
        return ("system", "Battery Failure")

    if node["packet_loss"] > PACKET_LOSS_THRESHOLD:
        return ("system", "Communication Failure")

    if node_id not in history:
        history[node_id] = []

    history[node_id].append(node)

    if len(history[node_id]) > HISTORY_SIZE:
        history[node_id].pop(0)

    return None
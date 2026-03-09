from config import NEIGHBOR_THRESHOLD, HISTORY_THRESHOLD, HISTORY_SIZE, SENSORS

history = {}


def confirm_faults(nodes, suspected):

    confirmed = []

    for i, node in enumerate(nodes):

        node_id = node["node_id"]

        if node_id not in history:
            history[node_id] = {s: [] for s in SENSORS}

        for sensor in SENSORS:

            value = node[sensor]

            history[node_id][sensor].append(value)

            if len(history[node_id][sensor]) > HISTORY_SIZE:
                history[node_id][sensor].pop(0)

        neighbors = []

        if i > 0:
            neighbors.append(nodes[i-1])

        if i < len(nodes)-1:
            neighbors.append(nodes[i+1])

        for sensor in SENSORS:

            val = node[sensor]

            # spatial
            if neighbors:

                avg = sum(n[sensor] for n in neighbors)/len(neighbors)

                if abs(val-avg) > NEIGHBOR_THRESHOLD:
                    confirmed.append((node_id, sensor, "Neighbor Deviation"))

            # temporal
            hist = history[node_id][sensor]

            if len(hist) >= 3:

                prev = sum(hist[:-1])/(len(hist)-1)

                if abs(val-prev) > HISTORY_THRESHOLD:
                    confirmed.append((node_id, sensor, "Sudden Change"))

    return confirmed
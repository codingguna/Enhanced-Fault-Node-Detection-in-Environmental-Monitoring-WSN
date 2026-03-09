from config import SENSORS, DRIFT_THRESHOLD, OUTLIER_THRESHOLD


def detect_cluster_fault(nodes):

    faults = []

    for sensor in SENSORS:

        values = [n[sensor] for n in nodes]

        avg = sum(values) / len(values)

        for node in nodes:

            val = node[sensor]
            node_id = node["node_id"]

            dev = abs(val - avg)

            if dev > DRIFT_THRESHOLD and dev <= OUTLIER_THRESHOLD:
                faults.append((node_id, sensor, "Sensor Drift"))

            if dev > OUTLIER_THRESHOLD:
                faults.append((node_id, sensor, "Outlier Sensor"))

    return faults
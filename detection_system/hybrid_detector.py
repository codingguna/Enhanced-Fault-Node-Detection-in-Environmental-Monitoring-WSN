from .node_level import detect_node_level
from .cluster_level import detect_cluster_level
from config import ENERGY_THRESHOLD

def hybrid_detect(data):
    node_faults = detect_node_level(data, ENERGY_THRESHOLD)
    cluster_faults = detect_cluster_level(data)

    combined = node_faults + cluster_faults
    return list({(nid, ftype) for nid, ftype in combined})
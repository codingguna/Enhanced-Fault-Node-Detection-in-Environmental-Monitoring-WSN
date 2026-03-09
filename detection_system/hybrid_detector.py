from detection_system.node_level import detect_node_fault
from detection_system.cluster_level import detect_cluster_fault
from detection_system.centralized import confirm_faults


def hybrid_detect(nodes):

    suspected = []

    for node in nodes:

        res = detect_node_fault(node)

        if res:
            sensor, fault = res
            suspected.append((node["node_id"], sensor, fault))

    suspected += detect_cluster_fault(nodes)

    confirmed = confirm_faults(nodes, suspected)

    return confirmed
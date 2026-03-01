import random

def inject_faults(nodes, percentage):
    count = int(len(nodes) * percentage)
    faulty_nodes = random.sample(nodes, count)

    for node in faulty_nodes:
        node.is_faulty = True
        node.fault_type = random.choice(["soft", "intermittent"])

    return [node.node_id for node in faulty_nodes]
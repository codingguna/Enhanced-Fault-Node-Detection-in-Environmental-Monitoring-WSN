from flask import Flask, request, jsonify
from detection_system.hybrid_detector import hybrid_detect
from database.db import init_db, insert_sensor, insert_fault

app = Flask(__name__)

init_db()

live_nodes = []


@app.route("/data", methods=["POST"])
def receive():

    global live_nodes

    nodes = request.get_json()

    if not nodes:
        return jsonify({"error": "No sensor data received"}), 400

    faults = hybrid_detect(nodes)

    for node in nodes:
        insert_sensor(node)
        node["status"] = "OK"
        node["fault"] = "None"

    for nid, sensor, fault in faults:

        for node in nodes:
            if node["node_id"] == nid:
                node["status"] = "FAULT"
                node["fault"] = f"{sensor}:{fault}"

        insert_fault(nid, sensor, fault)

    live_nodes = nodes

    return jsonify({"status": "ok"})

@app.route("/nodes")
def nodes():

    return jsonify(live_nodes)


if __name__ == "__main__":
    app.run(debug=True)
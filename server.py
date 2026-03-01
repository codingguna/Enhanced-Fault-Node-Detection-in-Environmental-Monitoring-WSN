from flask import Flask, request, jsonify
import csv
from detection_system.hybrid_detector import hybrid_detect
from detection_system.centralized import CentralizedConfirmation

app = Flask(__name__)
central = CentralizedConfirmation()
live_data = []

@app.route("/data", methods=["POST"])
def receive_data():
    global live_data

    data = request.json
    live_data = data

    suspected = hybrid_detect(data)
    confirmed = central.confirm(suspected)

    with open("data/detected_faults.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "fault_type"])
        for row in confirmed:
            writer.writerow(row)

    return jsonify({"status": "ok"})

@app.route("/nodes", methods=["GET"])
def get_nodes():
    return jsonify(live_data)

if __name__ == "__main__":
    app.run(debug=True)
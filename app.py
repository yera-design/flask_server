import base64
import io
import os
import time

import matplotlib

matplotlib.use("Agg")  # render without a display, required for a server process
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request

from algorithms import ALGORITHMS

app = Flask(__name__)

PLOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def _parse_int(value, default):
    if value is None or value == "":
        return default
    return int(str(value).replace(",", "").strip())

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Visualizer is running.",
        "usage": "/analyze?algo=<name>&n_max=<int>&step=<int>",
        "supported_algorithms": sorted(ALGORITHMS.keys()),
    })

@app.route("/analyze", methods=["GET"])
def analyze():
    algo = request.args.get("algo", "").strip().strip("'\"").lower().replace(" ", "_")
    if algo not in ALGORITHMS:
        return jsonify({
            "error": f"Unsupported algorithm '{algo}'",
            "supported_algorithms": sorted(ALGORITHMS.keys()),
        }), 400

    try:
        step = _parse_int(request.args.get("step"), 1)
        n_max = _parse_int(request.args.get("n_max"), 100)
    except ValueError:
        return jsonify({"error": "step and n_max must be integers"}), 400

    if step <= 0 or n_max < 0:
        return jsonify({"error": "step must be > 0 and n_max must be >= 0"}), 400

    complexity, formula = ALGORITHMS[algo]

    n_values = list(range(0, n_max + 1, step))
    if n_values[-1] != n_max:  # always include the requested upper bound
        n_values.append(n_max)
    op_counts = [formula(n) for n in n_values]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(n_values, op_counts, marker="o", markersize=3)
    ax.set_xlabel("n (number of elements)")
    ax.set_ylabel("operations")
    ax.set_title(f"{algo} — {complexity}")
    ax.grid(True, alpha=0.3)

    filepath = os.path.join(PLOTS_DIR, f"{algo}_{int(time.time())}.png")
    fig.savefig(filepath, dpi=100, bbox_inches="tight")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({
        "algo": algo,
        "complexity": complexity,
        "step": step,
        "n_max": n_max,
        "n_values": n_values,
        "operation_counts": op_counts,
        "image_path": filepath,
        "image_base64": image_base64,
    })


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)

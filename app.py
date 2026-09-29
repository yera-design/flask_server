import base64
import io
import math
import os
import time
from datetime import timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render without a display, required for a server process
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.exc import SQLAlchemyError

from algorithms import ALGORITHMS
from models import Analysis, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# SQLite file next to this script by default; set DATABASE_URL to point
# elsewhere (e.g. a Postgres URL) without touching the code.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{Path(BASE_DIR, 'analyses.db').as_posix()}"
)
db.init_app(app)
with app.app_context():
    db.create_all()  # no-op if the tables already exist

# JWT_SECRET_KEY signs and verifies tokens; set it via an env var in any real
# deployment. JWT_TOKEN_LOCATION defaults to ["headers"], so tokens are only
# ever read from the Authorization header, never from a query parameter.
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-only-secret-key-please-override-in-any-real-deployment"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# This exercise has one user, checked against env vars so nothing sensitive
# is hardcoded in source. Swap for a real user table/password hashing if this
# ever needs more than one account.
APP_USERNAME = os.environ.get("APP_USERNAME", "student")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "changeme123")

UNAUTHORIZED_MESSAGE = "I don't know you. Bye."


@jwt.unauthorized_loader  # no Authorization header at all
def _handle_missing_token(_reason):
    return jsonify({"error": UNAUTHORIZED_MESSAGE}), 401


@jwt.invalid_token_loader  # header present but malformed/bad signature
def _handle_invalid_token(_reason):
    return jsonify({"error": UNAUTHORIZED_MESSAGE}), 401


@jwt.expired_token_loader  # header present, well-formed, but expired
def _handle_expired_token(_jwt_header, _jwt_payload):
    return jsonify({"error": UNAUTHORIZED_MESSAGE}), 401

PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def _parse_int(value, default):
    if value is None or value == "":
        return default
    return int(str(value).replace(",", "").strip())


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _validate_analysis_payload(payload):
    """Return an error message if the payload is not a valid /analyze result, else None."""
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"

    required = ["algo", "complexity", "step", "n_max", "n_values", "operation_counts"]
    missing = [key for key in required if key not in payload]
    if missing:
        return f"Missing required field(s): {', '.join(missing)}"

    algo = payload["algo"]
    if not isinstance(algo, str) or algo not in ALGORITHMS:
        return f"Unsupported algorithm '{algo}'"
    if payload["complexity"] != ALGORITHMS[algo][0]:
        return f"complexity does not match '{algo}' (expected {ALGORITHMS[algo][0]})"

    if not _is_int(payload["step"]) or payload["step"] <= 0:
        return "step must be an integer > 0"
    if not _is_int(payload["n_max"]) or payload["n_max"] < 0:
        return "n_max must be an integer >= 0"

    n_values, op_counts = payload["n_values"], payload["operation_counts"]
    for name, values in (("n_values", n_values), ("operation_counts", op_counts)):
        if not isinstance(values, list) or not values:
            return f"{name} must be a non-empty list"
        if not all(_is_number(v) for v in values):
            return f"{name} must contain only finite numbers"
    if len(n_values) != len(op_counts):
        return "n_values and operation_counts must be the same length"

    for name in ("image_path", "image_base64"):
        if payload.get(name) is not None and not isinstance(payload[name], str):
            return f"{name} must be a string"

    return None


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Visualizer is running.",
        "usage": "/analyze?algo=<name>&n_max=<int>&step=<int>",
        "login": "POST /login with {\"username\", \"password\"} to get a JWT",
        "save": "POST /save_analysis (needs 'Authorization: Bearer <token>') with the JSON returned by /analyze",
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


@app.route("/login", methods=["POST"])
def login():
    credentials = request.get_json(silent=True) or {}
    username = credentials.get("username")
    password = credentials.get("password")

    if username != APP_USERNAME or password != APP_PASSWORD:
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=username)
    response = jsonify({"access_token": access_token})
    # Also expose it as a response header, in addition to the JSON body.
    response.headers["Authorization"] = f"Bearer {access_token}"
    return response, 200


@app.route("/save_analysis", methods=["POST"])
@jwt_required()  # requires "Authorization: Bearer <token>" on the request
def save_analysis():
    payload = request.get_json(silent=True)
    error = _validate_analysis_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    analysis = Analysis(
        algo=payload["algo"],
        complexity=payload["complexity"],
        step=payload["step"],
        n_max=payload["n_max"],
        n_values=payload["n_values"],
        operation_counts=payload["operation_counts"],
        image_path=payload.get("image_path"),
        image_base64=payload.get("image_base64"),
        created_by=get_jwt_identity(),
    )

    try:
        db.session.add(analysis)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to save analysis")
        return jsonify({"error": "Could not save the analysis to the database"}), 500

    return jsonify({
        "message": "Analysis saved",
        "analysis": analysis.to_dict(),
    }), 201


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)

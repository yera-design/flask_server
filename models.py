from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow():
    return datetime.now(timezone.utc)


class Analysis(db.Model):
    """One saved result of GET /analyze (one row per call to POST /save_analysis)."""

    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    algo = db.Column(db.String(64), nullable=False, index=True)
    complexity = db.Column(db.String(32), nullable=False)
    step = db.Column(db.Integer, nullable=False)
    n_max = db.Column(db.Integer, nullable=False)
    # Lists are stored with SQLAlchemy's JSON type, so we never hand-write SQL
    # or serialize them ourselves.
    n_values = db.Column(db.JSON, nullable=False)
    operation_counts = db.Column(db.JSON, nullable=False)
    image_path = db.Column(db.String(512), nullable=True)
    image_base64 = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(120), nullable=True)  # JWT identity of the caller
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    def to_dict(self, include_image=False):
        data = {
            "id": self.id,
            "algo": self.algo,
            "complexity": self.complexity,
            "step": self.step,
            "n_max": self.n_max,
            "n_values": self.n_values,
            "operation_counts": self.operation_counts,
            "image_path": self.image_path,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_image:
            data["image_base64"] = self.image_base64
        return data

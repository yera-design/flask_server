import os
import tempfile
import unittest

# Point the app at a throwaway database BEFORE importing it, so tests never
# touch the real analyses.db.
_TMP_DIR = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_TMP_DIR.name, 'test.db').replace(os.sep, '/')}"

from app import app  # noqa: E402
from models import Analysis, db  # noqa: E402


def tearDownModule():
    with app.app_context():
        db.engine.dispose()
    _TMP_DIR.cleanup()


class TestSaveAnalysis(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def _analyze_payload(self, algo="bubble_sort", n_max=20, step=10):
        """A real /analyze response, exactly what run_all_analyses.py would POST."""
        response = self.client.get("/analyze", query_string={"algo": algo, "n_max": n_max, "step": step})
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def _count(self):
        with app.app_context():
            return db.session.query(Analysis).count()

    def test_saves_analyze_output_to_database(self):
        payload = self._analyze_payload()
        response = self.client.post("/save_analysis", json=payload)

        self.assertEqual(response.status_code, 201)
        saved = response.get_json()["analysis"]
        self.assertEqual(saved["algo"], "bubble_sort")
        self.assertEqual(saved["complexity"], "O(n^2)")

        with app.app_context():
            row = db.session.get(Analysis, saved["id"])
            self.assertIsNotNone(row)
            self.assertEqual(row.n_values, payload["n_values"])
            self.assertEqual(row.operation_counts, payload["operation_counts"])
            self.assertEqual(row.step, 10)
            self.assertEqual(row.n_max, 20)
            self.assertEqual(row.image_path, payload["image_path"])
            self.assertEqual(row.image_base64, payload["image_base64"])
            self.assertIsNotNone(row.created_at)

    def test_each_post_creates_a_new_row(self):
        payload = self._analyze_payload()
        self.client.post("/save_analysis", json=payload)
        self.client.post("/save_analysis", json=payload)
        self.assertEqual(self._count(), 2)

    def test_image_fields_are_optional(self):
        payload = self._analyze_payload()
        payload.pop("image_path")
        payload.pop("image_base64")
        response = self.client.post("/save_analysis", json=payload)
        self.assertEqual(response.status_code, 201)

    def test_response_does_not_echo_the_image(self):
        response = self.client.post("/save_analysis", json=self._analyze_payload())
        self.assertNotIn("image_base64", response.get_json()["analysis"])

    def test_rejects_non_json_body(self):
        response = self.client.post("/save_analysis", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_rejects_json_that_is_not_an_object(self):
        response = self.client.post("/save_analysis", json=[1, 2, 3])
        self.assertEqual(response.status_code, 400)

    def test_rejects_missing_fields(self):
        payload = self._analyze_payload()
        del payload["n_values"]
        response = self.client.post("/save_analysis", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("n_values", response.get_json()["error"])
        self.assertEqual(self._count(), 0)

    def test_rejects_unknown_algorithm(self):
        payload = self._analyze_payload()
        payload["algo"] = "bogo_sort"
        response = self.client.post("/save_analysis", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_rejects_wrong_complexity_for_algorithm(self):
        payload = self._analyze_payload()
        payload["complexity"] = "O(1)"
        response = self.client.post("/save_analysis", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_rejects_bad_step_and_n_max(self):
        for field, bad in (("step", 0), ("step", "10"), ("step", True), ("n_max", -1), ("n_max", 1.5)):
            with self.subTest(field=field, value=bad):
                payload = self._analyze_payload()
                payload[field] = bad
                response = self.client.post("/save_analysis", json=payload)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_rejects_mismatched_or_malformed_lists(self):
        payload = self._analyze_payload()
        payload["operation_counts"] = payload["operation_counts"][:-1]
        self.assertEqual(self.client.post("/save_analysis", json=payload).status_code, 400)

        payload = self._analyze_payload()
        payload["n_values"] = ["a"] * len(payload["operation_counts"])
        self.assertEqual(self.client.post("/save_analysis", json=payload).status_code, 400)

        payload = self._analyze_payload()
        payload["n_values"] = payload["operation_counts"] = []
        self.assertEqual(self.client.post("/save_analysis", json=payload).status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get("/save_analysis").status_code, 405)


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest

# Point the app at a throwaway database BEFORE importing it, so tests never
# touch the real analyses.db.
_TMP_DIR = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_TMP_DIR.name, 'test.db').replace(os.sep, '/')}"

from app import APP_PASSWORD, APP_USERNAME, app  # noqa: E402
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
        """A real /analyze response, exactly what all_analyses.py would POST."""
        response = self.client.get("/analyze", query_string={"algo": algo, "n_max": n_max, "step": step})
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def _login(self, username=APP_USERNAME, password=APP_PASSWORD):
        return self.client.post("/login", json={"username": username, "password": password})

    def _auth_headers(self):
        token = self._login().get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _count(self):
        with app.app_context():
            return db.session.query(Analysis).count()

    # ---- /login ----

    def test_login_with_correct_credentials_returns_a_token(self):
        response = self._login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())
        # Also available as a response header, not just in the JSON body.
        self.assertIn("Bearer ", response.headers.get("Authorization", ""))

    def test_login_with_wrong_password_is_rejected(self):
        response = self._login(password="wrong")
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access_token", response.get_json())

    def test_login_with_unknown_username_is_rejected(self):
        response = self._login(username="someone-else")
        self.assertEqual(response.status_code, 401)

    def test_login_requires_a_json_body(self):
        response = self.client.post("/login", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 401)

    # ---- /save_analysis auth ----

    def test_save_without_a_token_is_rejected(self):
        response = self.client.post("/save_analysis", json=self._analyze_payload())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "I don't know you. Bye.")
        self.assertEqual(self._count(), 0)

    def test_save_with_a_malformed_token_is_rejected(self):
        headers = {"Authorization": "Bearer not-a-real-token"}
        response = self.client.post("/save_analysis", json=self._analyze_payload(), headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "I don't know you. Bye.")

    def test_save_with_missing_bearer_prefix_is_rejected(self):
        token = self._login().get_json()["access_token"]
        headers = {"Authorization": token}  # no "Bearer " prefix
        response = self.client.post("/save_analysis", json=self._analyze_payload(), headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_token_as_query_parameter_is_not_accepted(self):
        token = self._login().get_json()["access_token"]
        response = self.client.post(f"/save_analysis?token={token}", json=self._analyze_payload())
        self.assertEqual(response.status_code, 401)

    def test_save_records_which_user_saved_it(self):
        payload = self._analyze_payload()
        response = self.client.post("/save_analysis", json=payload, headers=self._auth_headers())
        self.assertEqual(response.get_json()["analysis"]["created_by"], APP_USERNAME)

    # ---- /save_analysis behavior (now with a valid token on every call) ----

    def test_saves_analyze_output_to_database(self):
        payload = self._analyze_payload()
        response = self.client.post("/save_analysis", json=payload, headers=self._auth_headers())

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
        headers = self._auth_headers()
        payload = self._analyze_payload()
        self.client.post("/save_analysis", json=payload, headers=headers)
        self.client.post("/save_analysis", json=payload, headers=headers)
        self.assertEqual(self._count(), 2)

    def test_image_fields_are_optional(self):
        payload = self._analyze_payload()
        payload.pop("image_path")
        payload.pop("image_base64")
        response = self.client.post("/save_analysis", json=payload, headers=self._auth_headers())
        self.assertEqual(response.status_code, 201)

    def test_response_does_not_echo_the_image(self):
        headers = self._auth_headers()
        response = self.client.post("/save_analysis", json=self._analyze_payload(), headers=headers)
        self.assertNotIn("image_base64", response.get_json()["analysis"])

    def test_rejects_non_json_body(self):
        headers = self._auth_headers()
        response = self.client.post("/save_analysis", data="not json", content_type="text/plain", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_rejects_json_that_is_not_an_object(self):
        response = self.client.post("/save_analysis", json=[1, 2, 3], headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_rejects_missing_fields(self):
        headers = self._auth_headers()
        payload = self._analyze_payload()
        del payload["n_values"]
        response = self.client.post("/save_analysis", json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("n_values", response.get_json()["error"])
        self.assertEqual(self._count(), 0)

    def test_rejects_unknown_algorithm(self):
        payload = self._analyze_payload()
        payload["algo"] = "bogo_sort"
        response = self.client.post("/save_analysis", json=payload, headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_rejects_wrong_complexity_for_algorithm(self):
        payload = self._analyze_payload()
        payload["complexity"] = "O(1)"
        response = self.client.post("/save_analysis", json=payload, headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_rejects_bad_step_and_n_max(self):
        headers = self._auth_headers()
        for field, bad in (("step", 0), ("step", "10"), ("step", True), ("n_max", -1), ("n_max", 1.5)):
            with self.subTest(field=field, value=bad):
                payload = self._analyze_payload()
                payload[field] = bad
                response = self.client.post("/save_analysis", json=payload, headers=headers)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_rejects_mismatched_or_malformed_lists(self):
        headers = self._auth_headers()

        payload = self._analyze_payload()
        payload["operation_counts"] = payload["operation_counts"][:-1]
        self.assertEqual(self.client.post("/save_analysis", json=payload, headers=headers).status_code, 400)

        payload = self._analyze_payload()
        payload["n_values"] = ["a"] * len(payload["operation_counts"])
        self.assertEqual(self.client.post("/save_analysis", json=payload, headers=headers).status_code, 400)

        payload = self._analyze_payload()
        payload["n_values"] = payload["operation_counts"] = []
        self.assertEqual(self.client.post("/save_analysis", json=payload, headers=headers).status_code, 400)
        self.assertEqual(self._count(), 0)

    def test_get_is_not_allowed(self):
        # Routing rejects this before @jwt_required() even runs, no token needed.
        self.assertEqual(self.client.get("/save_analysis").status_code, 405)


if __name__ == "__main__":
    unittest.main()

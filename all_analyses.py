import os

import requests

from algorithms import ALGORITHMS

BASE_URL = "http://localhost:8000"
N_MAX = 100

# Must match APP_USERNAME / APP_PASSWORD on the server (see app.py).
APP_USERNAME = os.environ.get("APP_USERNAME", "student")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "changeme123")


def _login():
    response = requests.post(
        f"{BASE_URL}/login", json={"username": APP_USERNAME, "password": APP_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["access_token"]


def run_all(n_max=N_MAX):
    try:
        token = _login()
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Is 'python app.py' running?")
        return
    except requests.exceptions.HTTPError as exc:
        print(f"Login failed -> {exc}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    for algo in sorted(ALGORITHMS):
        try:
            response = requests.get(f"{BASE_URL}/analyze", params={"algo": algo, "n_max": n_max})
            response.raise_for_status()

            data = response.json()
            # Persist to the database through the API instead of writing a JSON file.
            saved = requests.post(f"{BASE_URL}/save_analysis", json=data, headers=headers)
            saved.raise_for_status()
        except requests.exceptions.ConnectionError:
            print("Could not connect to the server. Is 'python app.py' running?")
            return
        except requests.exceptions.HTTPError as exc:
            print(f"{algo}: request failed -> {exc}")
            continue

        analysis_id = saved.json()["analysis"]["id"]
        print(f"{algo}: {data['complexity']} -> saved to database (id={analysis_id})")


if __name__ == "__main__":
    run_all()

import requests

from algorithms import ALGORITHMS

BASE_URL = "http://localhost:8000"
N_MAX = 100


def run_all(n_max=N_MAX):
    for algo in sorted(ALGORITHMS):
        try:
            response = requests.get(f"{BASE_URL}/analyze", params={"algo": algo, "n_max": n_max})
            response.raise_for_status()

            data = response.json()
            # Persist to the database through the API instead of writing a JSON file.
            saved = requests.post(f"{BASE_URL}/save_analysis", json=data)
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

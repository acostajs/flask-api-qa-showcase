import os
import requests


def test_employees_health() -> None:
    """Smoke test to verify that the /employees endpoint is reachable and healthy."""
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
    response = requests.get(f"{base_url}/employees", timeout=5)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_shifts_health() -> None:
    """Smoke test to verify that the /shifts endpoint is reachable and healthy."""
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
    response = requests.get(f"{base_url}/shifts", timeout=5)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

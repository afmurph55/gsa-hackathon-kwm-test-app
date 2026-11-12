"""Verify dashboard boundaries, failed-refresh preservation and saved data updates."""

import importlib.util
import json
import threading
from contextlib import contextmanager
from pathlib import Path

import httpx

SPEC = importlib.util.spec_from_file_location(
    "dashboard_server", Path(__file__).resolve().parents[1] / "dashboard/serve.py"
)
dashboard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dashboard)
QUERY = {
    "fuel": "distillate",
    "geography": "US",
    "frequency": "weekly",
    "lookback_periods": 12,
}


@contextmanager
def server(tmp_path, refresh):
    path = tmp_path / "snapshot.json"
    path.write_text(
        json.dumps({"cases": [{"query": QUERY, "response": {"text": "saved"}}]})
    )
    instance = dashboard.create_server(0, path, refresh)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{instance.server_address[1]}"
        ) as client:
            yield client, path
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=2)


def test_refresh_checks_origin_host_bounds_and_file_access(tmp_path):
    calls = []
    with server(tmp_path, lambda query: calls.append(query)) as (client, _path):
        assert (
            client.post(
                "/api/refresh", json=QUERY, headers={"Origin": "https://other.example"}
            ).status_code
            == 403
        )
        assert client.get("/", headers={"Host": "other.example"}).status_code == 403
        assert client.get("/.env").status_code == 404
        assert client.post("/api/refresh", content="plain").status_code == 415
        assert (
            client.post(
                "/api/refresh", json={**QUERY, "lookback_periods": 999}
            ).status_code
            == 400
        )
        assert (
            client.post("/api/refresh", json={**QUERY, "fuel": "ulsd"}).status_code
            == 400
        )
        assert (
            client.post(
                "/api/refresh", json={**QUERY, "api_key": "never-accepted"}
            ).status_code
            == 400
        )
        assert not calls


def test_failed_refresh_keeps_snapshot_and_suppresses_upstream_exception(tmp_path):
    def failure(_query):
        raise RuntimeError("SYNTHETIC-SENSITIVE-UPSTREAM-TEXT")

    with server(tmp_path, failure) as (client, path):
        before = path.read_bytes()
        response = client.post("/api/refresh", json=QUERY)
        assert response.status_code == 502
        assert "SYNTHETIC-SENSITIVE-UPSTREAM-TEXT" not in response.text
        assert path.read_bytes() == before


def test_successful_refresh_persists_only_result_and_serves_snapshot(tmp_path):
    case = {"query": QUERY, "response": {"text": "refreshed"}}
    with server(tmp_path, lambda _query: case) as (client, path):
        response = client.post("/api/refresh", json=QUERY)
        assert response.status_code == 200
        assert json.loads(path.read_text())["cases"] == [case]
        assert (
            path.with_suffix(".js").read_text().startswith("window.FUELSUPPLY_DATA = ")
        )
        snapshot = client.get("/api/snapshot")
        assert snapshot.status_code == 200
        assert snapshot.json()["cases"] == [case]

import json
import sqlite3

from fastapi.testclient import TestClient
import pytest

from app.main import create_app
from app.settings import Settings


@pytest.fixture
def runtime(tmp_path):
    return Settings(
        db_path=tmp_path / "current_sea_test.db",
        log_path=tmp_path / "invocations_test.jsonl",
    )


@pytest.fixture
def client(runtime):
    with TestClient(create_app(runtime)) as test_client:
        yield test_client


def test_health_reports_trial_stage(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "project": "CURRENT•SEA",
        "version": "0.0.1",
        "development_stage": "3 — TRIAL",
    }


def test_scan_returns_explainable_signals(client):
    response = client.post(
        "/v1/ambiguity/scan",
        json={"text": "We might send it soon."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "ambiguity-scan"
    assert body["ambiguous"] is True
    assert body["signal_count"] == 3
    assert {signal["code"] for signal in body["signals"]} == {
        "UNCERTAIN_COMMITMENT",
        "POSSIBLE_UNRESOLVED_REFERENCE",
        "VAGUE_TIME",
    }


def test_clear_wording_returns_no_signals(client):
    response = client.post(
        "/v1/ambiguity/scan",
        json={"text": "Morgan will send invoice 184 by 5:00 PM UTC on Friday."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ambiguous"] is False
    assert body["ambiguity_score"] == 0
    assert body["signals"] == []


def test_invocation_is_observable_without_storing_input(client, runtime):
    private_text = "Our private phrase might happen later."
    response = client.post("/v1/ambiguity/scan", json={"text": private_text})
    request_id = response.json()["request_id"]

    with sqlite3.connect(runtime.db_path) as connection:
        row = connection.execute(
            "SELECT * FROM invocations WHERE id = ?", (request_id,)
        ).fetchone()

    log_event = json.loads(runtime.log_path.read_text(encoding="utf-8").strip())
    assert row is not None
    assert log_event["request_id"] == request_id
    assert private_text not in runtime.log_path.read_text(encoding="utf-8")


def test_asset_registry_is_seeded(client, runtime):
    client.get("/health")

    with sqlite3.connect(runtime.db_path) as connection:
        row = connection.execute(
            """
            SELECT id, development_stage, development_name, value_state
            FROM assets
            WHERE id = 'ambiguity-scan'
            """
        ).fetchone()

    assert row == ("ambiguity-scan", 3, "TRIAL", "ACTIVE")


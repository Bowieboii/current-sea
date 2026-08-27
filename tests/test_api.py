import json
import sqlite3
import asyncio

from fastapi.testclient import TestClient
from mcp import Client
import pytest

from app.main import create_app
from app.settings import Settings


@pytest.fixture
def runtime(tmp_path):
    return Settings(
        database_url=f"sqlite:///{(tmp_path / 'current_sea_test.db').as_posix()}",
        log_path=tmp_path / "invocations_test.jsonl",
        daily_invocation_limit=100,
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
        "version": "0.0.3",
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
    assert body["source"] == "rest"
    assert body["daily_remaining"] == 99
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


def test_whitespace_only_input_is_rejected_cleanly(client):
    response = client.post("/v1/ambiguity/scan", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Text must contain at least one visible character."
    )


def test_invocation_is_observable_without_storing_input(client, runtime):
    private_text = "Our private phrase might happen later."
    response = client.post("/v1/ambiguity/scan", json={"text": private_text})
    request_id = response.json()["request_id"]

    db_path = runtime.database_url.removeprefix("sqlite:///")
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT source FROM invocations WHERE id = ?", (request_id,)
        ).fetchone()

    log_event = json.loads(runtime.log_path.read_text(encoding="utf-8").strip())
    assert row is not None
    assert row[0] == "rest"
    assert log_event["request_id"] == request_id
    assert private_text not in runtime.log_path.read_text(encoding="utf-8")


def test_asset_registry_is_seeded(client, runtime):
    client.get("/health")

    db_path = runtime.database_url.removeprefix("sqlite:///")
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, development_stage, development_name, value_state
            FROM assets
            WHERE id = 'ambiguity-scan'
            """
        ).fetchone()

    assert row == ("ambiguity-scan", 3, "TRIAL", "ACTIVE")


def test_status_reports_invocations_by_machine_surface(client):
    client.post("/v1/ambiguity/scan", json={"text": "Send it soon."})

    response = client.get("/v1/status")

    assert response.status_code == 200
    assert response.json()["summary"]["by_source"] == {"rest": 1}


def test_daily_trial_ceiling_returns_429(tmp_path):
    runtime = Settings(
        database_url=f"sqlite:///{(tmp_path / 'limited.db').as_posix()}",
        log_path=tmp_path / "limited.jsonl",
        daily_invocation_limit=1,
    )
    with TestClient(create_app(runtime)) as limited_client:
        first = limited_client.post(
            "/v1/ambiguity/scan", json={"text": "Send it soon."}
        )
        second = limited_client.post(
            "/v1/ambiguity/scan", json={"text": "Send it later."}
        )

    assert first.status_code == 200
    assert second.status_code == 429


def test_mcp_client_can_discover_and_invoke_asset(client):
    async def invoke():
        async with Client(client.app.state.mcp_server) as mcp_client:
            tools = await mcp_client.list_tools()
            result = await mcp_client.call_tool(
                "scan_ambiguity", {"text": "We might send it soon."}
            )
            return tools, result

    tools, result = asyncio.run(invoke())

    assert {tool.name for tool in tools.tools} == {"scan_ambiguity"}
    assert result.structured_content["source"] == "mcp"
    assert result.structured_content["ambiguous"] is True


def test_v001_database_is_migrated_without_losing_invocations(tmp_path):
    from app.database import build_engine, initialize_database

    db_path = tmp_path / "v001.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE assets (
                id TEXT PRIMARY KEY, name TEXT, version TEXT, description TEXT,
                development_stage INTEGER, development_name TEXT,
                value_state TEXT, generation INTEGER, parent_asset_id TEXT,
                created_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE invocations (
                id TEXT PRIMARY KEY, asset_id TEXT, occurred_at TEXT,
                input_char_count INTEGER, signal_count INTEGER,
                ambiguity_score INTEGER, duration_ms REAL, outcome TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO assets VALUES
            ('ambiguity-scan', 'Ambiguity Scan', '0.1.0', 'old', 3, 'TRIAL',
             'ACTIVE', 0, NULL, '2026-01-01T00:00:00+00:00')
            """
        )
        connection.execute(
            """
            INSERT INTO invocations VALUES
            ('old-call', 'ambiguity-scan', '2026-01-01T00:00:00+00:00',
             4, 1, 20, 0.1, 'completed')
            """
        )

    engine = build_engine(f"sqlite:///{db_path.as_posix()}")
    initialize_database(engine)
    engine.dispose()

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT id, source FROM invocations WHERE id = 'old-call'"
        ).fetchone()

    assert row == ("old-call", "rest")
def test_good_is_flagged_as_subjective_threshold(client):
    response = client.post(
        "/v1/ambiguity/scan",
        json={"text": "Make sure the final result is good."},
    )

    assert response.status_code == 200
    body = response.json()

    assert "SUBJECTIVE_THRESHOLD" in {
        signal["code"] for signal in body["signals"]
    }
    assert any(
        signal["phrase"].lower() == "good"
        for signal in body["signals"]
    )

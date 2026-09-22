import os

import pytest

from oura_dashboard.sample_data import build_sample_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "sample.db"
    build_sample_db(str(db_path), hours=12)
    monkeypatch.setenv("OURA_DB_PATH", str(db_path))

    from oura_dashboard.app import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_dashboard_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"SAMPLE-0001" in resp.data
    assert b"Heart rate" in resp.data


def test_api_readings_filters_by_kind(client):
    resp = client.get("/api/readings?kind=hr")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) > 0
    assert all(row["kind"] == "hr" for row in data)


def test_api_sleep_summary(client):
    resp = client.get("/api/sleep_summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert all(isinstance(v, int) for v in data.values())

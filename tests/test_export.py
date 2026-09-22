import csv
import json
import sqlite3

from oura_dashboard.export import export_csv, export_json
from oura_dashboard.db import connect, get_readings
from oura_dashboard.sample_data import build_sample_db


def test_export_csv_matches_db(tmp_path):
    db_path = tmp_path / "sample.db"
    build_sample_db(str(db_path), hours=6)

    conn = connect(str(db_path))
    rows = get_readings(conn)
    conn.close()
    assert len(rows) > 0

    out_path = tmp_path / "readings.csv"
    export_csv(rows, str(out_path))

    with open(out_path, newline="") as f:
        reader = csv.DictReader(f)
        exported = list(reader)

    assert len(exported) == len(rows)
    assert exported[0]["kind"] == rows[0]["kind"]
    assert float(exported[0]["value"]) == rows[0]["value"]


def test_export_json_matches_db(tmp_path):
    db_path = tmp_path / "sample.db"
    build_sample_db(str(db_path), hours=6)

    conn = connect(str(db_path))
    rows = get_readings(conn, kind="hr")
    conn.close()
    assert all(r["kind"] == "hr" for r in rows)

    out_path = tmp_path / "readings.json"
    export_json(rows, str(out_path))

    with open(out_path) as f:
        exported = json.load(f)

    assert exported == rows


def test_export_since_filter(tmp_path):
    db_path = tmp_path / "sample.db"
    build_sample_db(str(db_path), hours=6)

    conn = connect(str(db_path))
    all_rows = get_readings(conn, kind="hr")
    midpoint = all_rows[len(all_rows) // 2]["captured_unix"]
    filtered = get_readings(conn, kind="hr", since=midpoint)
    conn.close()

    assert all(r["captured_unix"] >= midpoint for r in filtered)
    assert len(filtered) < len(all_rows)

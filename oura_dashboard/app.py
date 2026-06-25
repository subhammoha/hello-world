"""Local web dashboard for browsing readings synced by open_oura.

Run:
    OURA_DB_PATH=/path/to/oura.db python -m oura_dashboard.app

Then open http://localhost:5000 (or http://<this machine's LAN IP>:5000 from your phone).
"""
import time

from flask import Flask, jsonify, render_template, request

from oura_dashboard.db import connect, get_device, get_kinds, get_latest_reading, get_readings, get_sync_state

app = Flask(__name__)

CHART_KINDS = ["hr", "spo2", "activity_met"]


@app.route("/")
def dashboard():
    conn = connect()
    try:
        device = get_device(conn)
        sync_state = get_sync_state(conn)
        latest_hr = get_latest_reading(conn, "hr")
        latest_spo2 = get_latest_reading(conn, "spo2")
        latest_battery = get_latest_reading(conn, "battery")
        kinds = get_kinds(conn)
    finally:
        conn.close()

    sleep_kinds = [k for k in kinds if k.startswith("sleep_stage_")]

    return render_template(
        "dashboard.html",
        device=device,
        sync_state=sync_state,
        latest_hr=latest_hr,
        latest_spo2=latest_spo2,
        latest_battery=latest_battery,
        chart_kinds=[k for k in CHART_KINDS if k in kinds],
        sleep_kinds=sleep_kinds,
    )


@app.route("/api/readings")
def api_readings():
    kind = request.args.get("kind")
    since = request.args.get("since", type=int)
    limit = request.args.get("limit", type=int)
    conn = connect()
    try:
        rows = get_readings(conn, kind=kind, since=since, limit=limit)
    finally:
        conn.close()
    return jsonify(rows)


@app.route("/api/sleep_summary")
def api_sleep_summary():
    conn = connect()
    try:
        kinds = [k for k in get_kinds(conn) if k.startswith("sleep_stage_")]
        summary = {}
        for kind in kinds:
            rows = get_readings(conn, kind=kind)
            summary[kind.replace("sleep_stage_", "")] = len(rows)
    finally:
        conn.close()
    return jsonify(summary)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

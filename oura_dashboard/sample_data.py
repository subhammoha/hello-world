"""Generate a synthetic oura.db matching open_oura's schema, for testing without a real ring."""
import argparse
import math
import sqlite3
import time

SCHEMA = """
CREATE TABLE device (
    serial TEXT PRIMARY KEY,
    hardware_id TEXT,
    firmware TEXT,
    api_version TEXT,
    mac TEXT,
    updated_unix INTEGER
);
CREATE TABLE sync_state (
    serial TEXT PRIMARY KEY,
    next_cursor TEXT,
    last_sync_unix INTEGER
);
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial TEXT,
    tag TEXT,
    name TEXT,
    ring_timestamp INTEGER,
    body BLOB,
    decoded_json TEXT,
    captured_unix INTEGER,
    UNIQUE(serial, tag, ring_timestamp, body)
);
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial TEXT,
    kind TEXT,
    value REAL,
    unit TEXT,
    captured_unix INTEGER
);
"""

SERIAL = "SAMPLE-0001"


def build_sample_db(db_path, hours=48, interval_seconds=900):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    now = int(time.time())
    start = now - hours * 3600

    conn.execute(
        "INSERT INTO device (serial, hardware_id, firmware, api_version, mac, updated_unix) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (SERIAL, "ring3-gen2", "2.9.1", "v1", "AA:BB:CC:DD:EE:FF", now),
    )
    conn.execute(
        "INSERT INTO sync_state (serial, next_cursor, last_sync_unix) VALUES (?, ?, ?)",
        (SERIAL, "cursor-123", now),
    )

    readings = []
    t = start
    step = 0
    battery = 92.0
    while t <= now:
        hr = 58 + 8 * math.sin(step / 6) + (step % 5)
        spo2 = 96 + (step % 3)
        readings.append((SERIAL, "hr", round(hr, 1), "bpm", t))
        readings.append((SERIAL, "spo2", round(spo2, 1), "%", t))
        if step % 4 == 0:
            battery = max(20.0, battery - 0.5)
            readings.append((SERIAL, "battery", round(battery, 1), "%", t))
        if step % 8 == 0:
            stage = ["awake", "light", "deep", "rem"][(step // 8) % 4]
            readings.append((SERIAL, f"sleep_stage_{stage}", 1.0, "epoch", t))
        if step % 6 == 0:
            readings.append((SERIAL, "activity_met", round(1.0 + (step % 7) * 0.3, 2), "met", t))
        t += interval_seconds
        step += 1

    conn.executemany(
        "INSERT INTO readings (serial, kind, value, unit, captured_unix) VALUES (?, ?, ?, ?, ?)",
        readings,
    )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="sample_oura.db", help="Output SQLite path")
    parser.add_argument("--hours", type=int, default=48, help="Hours of synthetic history")
    args = parser.parse_args()
    build_sample_db(args.db, hours=args.hours)
    print(f"Wrote sample database to {args.db}")


if __name__ == "__main__":
    main()

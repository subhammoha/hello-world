"""Read-only helpers for the SQLite database produced by open_oura's `sync` command."""
import os
import sqlite3

DEFAULT_DB_PATH = "oura.db"


def get_db_path():
    return os.environ.get("OURA_DB_PATH", DEFAULT_DB_PATH)


def connect(db_path=None):
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_device(conn):
    row = conn.execute(
        "SELECT serial, hardware_id, firmware, api_version, mac, updated_unix "
        "FROM device ORDER BY updated_unix DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def get_sync_state(conn):
    row = conn.execute(
        "SELECT serial, next_cursor, last_sync_unix FROM sync_state "
        "ORDER BY last_sync_unix DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def get_kinds(conn):
    rows = conn.execute("SELECT DISTINCT kind FROM readings ORDER BY kind").fetchall()
    return [r["kind"] for r in rows]


def get_latest_reading(conn, kind):
    row = conn.execute(
        "SELECT kind, value, unit, captured_unix FROM readings "
        "WHERE kind = ? ORDER BY captured_unix DESC LIMIT 1",
        (kind,),
    ).fetchone()
    return dict(row) if row else None


def get_readings(conn, kind=None, since=None, limit=None):
    query = "SELECT id, serial, kind, value, unit, captured_unix FROM readings"
    clauses = []
    params = []
    if kind:
        clauses.append("kind = ?")
        params.append(kind)
    if since is not None:
        clauses.append("captured_unix >= ?")
        params.append(since)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY captured_unix ASC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

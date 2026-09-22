"""Export readings from an open_oura SQLite database to CSV or JSON.

Usage:
    python -m oura_dashboard.export --db oura.db --format csv --out readings.csv
    python -m oura_dashboard.export --db oura.db --format json --out readings.json --kind hr --since 1700000000
"""
import argparse
import csv
import json

from oura_dashboard.db import connect, get_readings

FIELDNAMES = ["id", "serial", "kind", "value", "unit", "captured_unix"]


def export_csv(rows, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def export_json(rows, out_path):
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Path to open_oura's SQLite database")
    parser.add_argument("--format", choices=["csv", "json"], required=True)
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument("--kind", default=None, help="Filter to a single reading kind (e.g. hr, spo2, battery)")
    parser.add_argument("--since", type=int, default=None, help="Only rows with captured_unix >= SINCE")
    args = parser.parse_args()

    conn = connect(args.db)
    try:
        rows = get_readings(conn, kind=args.kind, since=args.since)
    finally:
        conn.close()

    if args.format == "csv":
        export_csv(rows, args.out)
    else:
        export_json(rows, args.out)

    print(f"Wrote {len(rows)} readings to {args.out}")


if __name__ == "__main__":
    main()

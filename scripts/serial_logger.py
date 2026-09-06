"""
serial_logger.py — Capture ESP32 serial output to CSV.

Usage:
    python scripts/serial_logger.py --port COM3 --baud 115200 --out ml/data/raw/real_measurements.csv

The ESP32 should print one JSON line per reading to Serial, e.g.:
  {"cap_raw":2.14,"opt_raw":0.71,"temp_c":38.5,"tof_raw":205.3}

This script prompts for sample metadata (fuel_base, adulterant, concentration_pct,
replicate) and prepends them to each row in the output CSV.
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import serial
except ImportError:
    print("Install pyserial: pip install pyserial")
    sys.exit(1)


CSV_COLUMNS = [
    "sample_id", "fuel_base", "adulterant", "concentration_pct",
    "temperature_c", "replicate",
    "capacitance_raw", "optical_raw", "tof_raw",
    "timestamp", "notes",
]


def prompt_metadata() -> dict:
    print("\n--- New sample batch ---")
    fuel     = input("fuel_base  [petrol/diesel]: ").strip().lower()
    adul     = input("adulterant [kerosene/diesel/water/none]: ").strip().lower()
    conc     = float(input("concentration_pct (e.g. 10): ").strip())
    rep      = int(input("replicate number (1/2/3): ").strip())
    notes    = input("notes (optional): ").strip()
    return {"fuel_base": fuel, "adulterant": adul,
            "concentration_pct": conc, "replicate": rep, "notes": notes}


def run(port: str, baud: int, out_path: Path, n_samples: int = 50) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = out_path.exists()

    meta     = prompt_metadata()
    sample_id = int(time.time())

    print(f"\nOpening {port} @ {baud} baud…  (Ctrl+C to stop)")
    with serial.Serial(port, baud, timeout=2) as ser, \
         open(out_path, "a", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()

        collected = 0
        while collected < n_samples:
            raw_line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not raw_line:
                continue
            try:
                data = json.loads(raw_line)
            except json.JSONDecodeError:
                print(f"  [skip] {raw_line}")
                continue

            row = {
                "sample_id":        sample_id,
                "fuel_base":        meta["fuel_base"],
                "adulterant":       meta["adulterant"],
                "concentration_pct": meta["concentration_pct"],
                "temperature_c":    data.get("temp_c", ""),
                "replicate":        meta["replicate"],
                "capacitance_raw":  data.get("cap_raw", ""),
                "optical_raw":      data.get("opt_raw", ""),
                "tof_raw":          data.get("tof_raw", ""),
                "timestamp":        datetime.now().isoformat(),
                "notes":            meta["notes"],
            }
            writer.writerow(row)
            f.flush()
            collected += 1
            print(f"  [{collected:>3}/{n_samples}] cap={row['capacitance_raw']}  "
                  f"opt={row['optical_raw']}  temp={row['temperature_c']}")

    print(f"\n✓ {collected} samples written → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FuelGuard serial logger")
    parser.add_argument("--port",    default="COM3",   help="Serial port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud",    default=115200, type=int)
    parser.add_argument("--out",     default="ml/data/raw/real_measurements.csv")
    parser.add_argument("--samples", default=50,    type=int, help="Readings per batch")
    args = parser.parse_args()
    run(args.port, args.baud, Path(args.out), args.samples)

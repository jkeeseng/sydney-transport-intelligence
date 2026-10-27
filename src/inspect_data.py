import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

folder = BASE_DIR / "data" / "raw" / "road_incidents"

latest_file = max(folder.glob("*.json"), key=lambda p: p.stat().st_mtime)

with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Data type:", type(data))

if isinstance(data, dict):
    print("Top-level keys:", list(data.keys()))
elif isinstance(data, list):
    print("Number of items:", len(data))

print("\nData preview:")
print(json.dumps(data, indent=2)[:2000])
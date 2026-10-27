
import os
import json
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("TFNSW_API_KEY")

if not API_KEY:
    raise ValueError("Missing TFNSW_API_KEY in .env")

RAW_DIR = BASE_DIR / "data" / "raw"

HEADERS = {
    "Authorization": f"apikey {API_KEY}",
    "Accept": "*/*"
}

API_CONFIG = {
    "traffic_stations": {
        "url": os.getenv("TFNSW_TRAFFIC_URL"),
        "format": "json",
        "params": {
            "format": "json",
            "q": (
                "SELECT * FROM "
                "road_traffic_counts_station_reference "
                "LIMIT 50"
            )
        }
    },

    "train_trip_updates": {
        "url": os.getenv("TFNSW_TRAIN_UPDATES_URL"),
        "format": "protobuf"
    },

    "train_positions": {
        "url": os.getenv("TFNSW_TRAIN_POSITIONS_URL"),
        "format": "protobuf"
    },

    "train_alerts": {
        "url": os.getenv("TFNSW_TRAIN_ALERTS_URL"),
        "format": "protobuf"
    },

    "road_incidents": {
        "url": os.getenv("TFNSW_ROAD_INCIDENTS_URL"),
        "format": "json"
    }
}


# ==========================================
# 2. SAVE JSON FILES
# ==========================================

def save_json(data, dataset_name):
    """Save API response into data/raw."""

    folder = RAW_DIR / dataset_name
    folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filepath = folder / f"{dataset_name}_{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved to: {filepath}")

    return str(filepath)


# ==========================================
# 3. FETCH API DATA
# ==========================================

def fetch_api(dataset_name, config):
    """Request and decode API response."""

    url = config.get("url")

    if not url:
        print(f"\nSKIPPED: {dataset_name} - URL missing")
        return {"status": "skipped"}

    print(f"\nFetching {dataset_name}...")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=config.get("params"),
            timeout=30
        )

        print("HTTP Status:", response.status_code)

        response.raise_for_status()

        # Decode JSON
        if config["format"] == "json":
            data = response.json()

        # Decode GTFS Realtime Protocol Buffers
        elif config["format"] == "protobuf":
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            data = MessageToDict(
                feed,
                preserving_proto_field_name=True
            )

        else:
            raise ValueError("Unsupported API format")

        # Save response
        filepath = save_json(data, dataset_name)

        # Count records
        if isinstance(data, dict):
            if "rows" in data:
                records = data["rows"]

            elif "entity" in data:
                records = data["entity"]

            elif "features" in data:
                records = data["features"]

            else:
                records = []

        elif isinstance(data, list):
            records = data

        else:
            records = []

        print("Records retrieved:", len(records))

        print("Records retrieved:", len(records))

        return {
            "status": "success",
            "records": len(records),
            "filepath": filepath
        }

    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)

        return {
            "status": "failed",
            "error": str(error)
        }

    except requests.exceptions.RequestException as error:
        print("Request error:", error)

        return {
            "status": "failed",
            "error": str(error)
        }

    except Exception as error:
        print("Unexpected error:", error)

        return {
            "status": "failed",
            "error": str(error)
        }


# ==========================================
# 4. MAIN PIPELINE
# ==========================================

def main():

    print("=" * 55)
    print("SYDNEY TRANSPORT DATA PIPELINE")
    print("=" * 55)

    start_time = datetime.now(timezone.utc)

    results = {}

    for dataset_name, config in API_CONFIG.items():
        results[dataset_name] = fetch_api(
            dataset_name,
            config
        )

    end_time = datetime.now(timezone.utc)

    summary = {
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "results": results
    }

    save_json(summary, "run_summaries")

    print("\n" + "=" * 55)
    print("PIPELINE SUMMARY")
    print("=" * 55)

    for name, result in results.items():
        print(f"{name}: {result['status'].upper()}")

    print("\nPipeline completed!")


if __name__ == "__main__":
    main()

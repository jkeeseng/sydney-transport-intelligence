
import os
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Works in a regular Python script or Jupyter notebook.
# Assumes this script/notebook is in the project's scripts/ folder.
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path.cwd()

# If running from a notebook elsewhere, set BASE_DIR explicitly:
# BASE_DIR = Path("/absolute/path/to/your/project")

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("TFNSW_API_KEY")

if not API_KEY:
    raise ValueError(
        f"Missing TFNSW_API_KEY in {BASE_DIR / '.env'}"
    )

RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Authorization": f"apikey {API_KEY}",
    "Accept": "*/*",
    "User-Agent": "SydneyTransportIntelligence/1.0",
}

# API configuration is read from .env.
# Missing URLs are skipped without stopping the pipeline.

API_CONFIG = {
    # Road traffic counts
    "traffic_stations": {
        "url": os.getenv("TFNSW_TRAFFIC_URL"),
        "format": "json",
        "params": {
            "format": "json",
            "q": (
                "SELECT * FROM "
                "road_traffic_counts_station_reference "
                "LIMIT 50"
            ),
        },
    },

    # Sydney Trains
    "train_trip_updates": {
        "url": os.getenv("TFNSW_TRAIN_UPDATES_URL"),
        "format": "protobuf",
    },
    "train_positions": {
        "url": os.getenv("TFNSW_TRAIN_POSITIONS_URL"),
        "format": "protobuf",
    },
    "train_alerts": {
        "url": os.getenv("TFNSW_TRAIN_ALERTS_URL"),
        "format": "protobuf",
    },

    # Sydney Metro
    "metro_trip_updates": {
        "url": os.getenv("TFNSW_METRO_UPDATES_URL"),
        "format": "protobuf",
    },

    # Light Rail
    "lightrail_cbd_southeast": {
        "url": os.getenv("TFNSW_LIGHTRAIL_CBD_SOUTHEAST_URL"),
        "format": "protobuf",
    },
    "lightrail_newcastle": {
        "url": os.getenv("TFNSW_LIGHTRAIL_NEWCASTLE_URL"),
        "format": "protobuf",
    },
    "lightrail_parramatta": {
        "url": os.getenv("TFNSW_LIGHTRAIL_PARRAMATTA_URL"),
        "format": "protobuf",
    },
    "lightrail_innerwest": {
        "url": os.getenv("TFNSW_LIGHTRAIL_INNERWEST_URL"),
        "format": "protobuf",
    },

    # Road incidents and hazards
    "road_incidents": {
        "url": os.getenv("TFNSW_ROAD_INCIDENTS_URL"),
        "format": "json",
    },
}


# ============================================================
# 2. FILE AND RECORD HELPERS
# ============================================================

def utc_timestamp():
    """Return a filesystem-friendly UTC timestamp."""
    return datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )


def save_json(data, dataset_name):
    """Save decoded API data as JSON."""
    folder = RAW_DIR / dataset_name
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{dataset_name}_{utc_timestamp()}.json"

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print(f"JSON saved: {filepath}")
    return str(filepath)


def count_records(data):
    """Estimate the number of records in common API response formats."""
    if isinstance(data, list):
        return len(data)

    if not isinstance(data, dict):
        return 0

    for key in (
        "entity",
        "rows",
        "features",
        "results",
        "data",
        "records",
    ):
        value = data.get(key)

        if isinstance(value, (list, dict)):
            return len(value)

    # Some APIs return one record or a metadata object.
    return 1 if data else 0


# ============================================================
# 3. FETCH AND DECODE API DATA
# ============================================================

def fetch_api(dataset_name, config):
    """Fetch a configured API and save its raw and decoded response."""

    url = config.get("url")

    if not url:
        print(f"\nSKIPPED: {dataset_name} — URL missing")
        return {
            "status": "skipped",
            "reason": "URL missing from .env",
        }

    print(f"\n{'-' * 60}")
    print(f"Fetching: {dataset_name}")
    print(f"URL: {url}")

    params = config.get("params")
    response = None

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=60,
        )

        print("HTTP status:", response.status_code)
        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", "unknown"
        )
        print("Content-Type:", content_type)
        print("Response size:", len(response.content), "bytes")

        folder = RAW_DIR / dataset_name
        folder.mkdir(parents=True, exist_ok=True)

        # Preserve the original response for troubleshooting.
        timestamp = utc_timestamp()
        format_type = config["format"]

        if format_type == "protobuf":
            raw_path = folder / f"{dataset_name}_{timestamp}.pb"
        elif format_type == "zip":
            raw_path = folder / f"{dataset_name}_{timestamp}.zip"
        else:
            raw_path = folder / f"{dataset_name}_{timestamp}.raw"

        raw_path.write_bytes(response.content)
        print("Raw response saved:", raw_path)

        # ----------------------------------------------------
        # Decode JSON
        # ----------------------------------------------------
        if format_type == "json":
            data = response.json()

        # ----------------------------------------------------
        # Decode GTFS-Realtime Protocol Buffers
        # ----------------------------------------------------
        elif format_type == "protobuf":
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            data = MessageToDict(
                feed,
                preserving_proto_field_name=True,
            )

            header = feed.header
            print(
                "GTFS-Realtime version:",
                header.gtfs_realtime_version,
            )

            if header.HasField("timestamp"):
                feed_timestamp = datetime.fromtimestamp(
                    header.timestamp,
                    tz=timezone.utc,
                )
                print("Feed timestamp (UTC):", feed_timestamp.isoformat())
            else:
                feed_timestamp = None
                print("Feed timestamp: not supplied")

            print("Feed entities:", len(feed.entity))

        # ----------------------------------------------------
        # ZIP response, e.g. static GTFS timetable
        # ----------------------------------------------------
        elif format_type == "zip":
            if not zipfile.is_zipfile(raw_path):
                raise ValueError(
                    "The API response is not a valid ZIP file."
                )

            with zipfile.ZipFile(raw_path) as archive:
                names = archive.namelist()

            data = {
                "archive_path": str(raw_path),
                "files": names,
            }

            print("Files inside ZIP:", len(names))
            for name in names[:30]:
                print(" -", name)

        else:
            raise ValueError(
                f"Unsupported format: {format_type}"
            )

        # Save decoded JSON as a separate artifact.
        json_path = save_json(data, dataset_name)

        records = count_records(data)
        print("Top-level records:", records)

        result = {
            "status": "success",
            "http_status": response.status_code,
            "content_type": content_type,
            "response_bytes": len(response.content),
            "records": records,
            "raw_filepath": str(raw_path),
            "json_filepath": json_path,
        }

        if format_type == "protobuf":
            result["feed_timestamp_utc"] = (
                feed_timestamp.isoformat()
                if feed_timestamp is not None
                else None
            )
            result["feed_entities"] = len(feed.entity)

        return result

    except requests.exceptions.HTTPError as error:
        status_code = (
            response.status_code if response is not None else None
        )

        # Avoid logging API credentials or sensitive headers.
        print("HTTP error:", error)
        if status_code in (401, 403):
            print(
                "Check the API key, permissions and endpoint access."
            )

        return {
            "status": "failed",
            "error_type": "HTTPError",
            "http_status": status_code,
            "error": str(error),
        }

    except requests.exceptions.Timeout as error:
        print("Request timed out:", error)
        return {
            "status": "failed",
            "error_type": "Timeout",
            "error": str(error),
        }

    except requests.exceptions.RequestException as error:
        print("Request error:", error)
        return {
            "status": "failed",
            "error_type": "RequestException",
            "error": str(error),
        }

    except (ValueError, json.JSONDecodeError) as error:
        print("Response decoding or validation error:", error)
        return {
            "status": "failed",
            "error_type": "DecodeError",
            "error": str(error),
        }

    except Exception as error:
        print("Unexpected error:", error)
        return {
            "status": "failed",
            "error_type": type(error).__name__,
            "error": str(error),
        }


# ============================================================
# 4. MAIN PIPELINE
# ============================================================

def main():
    print("=" * 60)
    print("SYDNEY TRANSPORT DATA PIPELINE")
    print("=" * 60)
    print("Project directory:", BASE_DIR)
    print("Raw data directory:", RAW_DIR)

    started_at = datetime.now(timezone.utc)
    results = {}

    for dataset_name, config in API_CONFIG.items():
        results[dataset_name] = fetch_api(
            dataset_name,
            config,
        )

    completed_at = datetime.now(timezone.utc)

    summary = {
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": round(
            (completed_at - started_at).total_seconds(),
            2,
        ),
        "results": results,
    }

    summary_path = save_json(summary, "run_summaries")

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    for name, result in results.items():
        status = result["status"].upper()
        print(f"{name}: {status}")

        if result["status"] == "failed":
            print("  Error:", result.get("error"))

        elif result["status"] == "success":
            print("  Records:", result.get("records", 0))

    success_count = sum(
        result["status"] == "success"
        for result in results.values()
    )
    failed_count = sum(
        result["status"] == "failed"
        for result in results.values()
    )
    skipped_count = sum(
        result["status"] == "skipped"
        for result in results.values()
    )

    print("\nSuccessful:", success_count)
    print("Failed:", failed_count)
    print("Skipped:", skipped_count)
    print("Summary saved:", summary_path)
    print("Pipeline completed.")


if __name__ == "__main__":
    main()

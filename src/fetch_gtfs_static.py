import os
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("TFNSW_API_KEY")
url = os.getenv("TFNSW_GTFS_STATIC_URL")

if not api_key or not url:
    raise ValueError("Missing API key or GTFS Static URL")

headers = {
    "Authorization": f"apikey {api_key}",
    "Accept": "application/zip"
}

output_dir = BASE_DIR / "data" / "raw" / "gtfs_static"
output_dir.mkdir(parents=True, exist_ok=True)

zip_path = output_dir / "gtfs_static.zip"

response = requests.get(
    url,
    headers=headers,
    timeout=120
)

print("HTTP Status:", response.status_code)
response.raise_for_status()

# Save ZIP file
zip_path.write_bytes(response.content)

# Verify the response is a ZIP file
if not zipfile.is_zipfile(zip_path):
    raise ValueError("API response is not a valid ZIP file")

# Inspect the ZIP contents
with zipfile.ZipFile(zip_path) as z:
    print("\nFiles inside GTFS ZIP:")
    for name in z.namelist():
        print(name)

print("\nDownloaded successfully:", zip_path)
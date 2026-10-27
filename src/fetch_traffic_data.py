import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TFNSW_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your .env file.")

url = "https://api.transport.nsw.gov.au/v1/traffic_volume"

headers = {
    "Authorization": f"apikey {api_key}",
    "Accept": "application/json"
}

params = {
    "format": "json",
    "q": "SELECT * FROM road_traffic_counts_station_reference LIMIT 50"
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30
)

print("Status code:", response.status_code)

response.raise_for_status()

data = response.json()

print("Response type:", type(data))
print("Response preview:", str(data)[:1500])
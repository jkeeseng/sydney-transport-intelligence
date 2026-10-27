# Sydney Transport Intelligence

A Python-based data analytics project exploring Sydney's public transport network using Transport for NSW (TfNSW) open data.

The project aims to combine real-time transport information with static network data to investigate train movements, service patterns, and transport performance through data analysis and interactive visualisations.

## Project Objectives

- Retrieve real-time public transport and traffic data using TfNSW APIs.
- Explore, clean, and transform transport datasets using Python and pandas.
- Map Sydney Trains services using GTFS geographical coordinates.
- Visualise train positions and data freshness using Folium.
- Build towards transport performance analysis and predictive modelling.

## Data Sources

**1. GTFS Realtime**

Retrieved using TfNSW APIs, including:

- Train vehicle positions
- Trip updates
- Service alerts

**2. GTFS Static**

Downloaded and extracted the TfNSW GTFS timetable dataset.

Key files used:

| File | Purpose |
|---|---|
| `routes.txt` | Identifies transport routes and operators |
| `trips.txt` | Links scheduled trips to routes and geographical shapes |
| `shapes.txt` | Provides ordered latitude and longitude coordinates |
| `stops.txt` | Contains public transport stop information for future analysis |

Additional datasets collected include road incidents and traffic station information.

## Work Completed

### 1. Data Collection

- Configured TfNSW API access using environment variables.
- Developed a Python script to retrieve transport datasets.
- Parsed GTFS Realtime Protocol Buffer responses.
- Stored timestamped JSON files under `data/raw/`.

### 2. Data Exploration and Cleaning

- Loaded real-time train vehicle positions into pandas.
- Extracted train identifiers, routes, coordinates, timestamps, and stop information.
- Calculated the age of train-position records to assess data freshness.
- Developed an initial interactive Folium map with train markers.

Marker colours indicate data freshness:

- Green: 60 seconds or less
- Orange: 61–300 seconds
- Grey: More than 300 seconds

### 3. Sydney Trains Network Extraction

Loaded the GTFS Static dataset and filtered routes belonging to Sydney Trains.

**Extraction results:**

| Metric | Result |
|---|---:|
| Sydney Trains route records | 10 |
| Scheduled train trip records | 48,298 |
| Unique railway shapes | 1,298 |
| Extracted geographical coordinates | 852,072 |

The 10 route records represent the T1–T9 train lines, with two records associated with T1.

Used pandas joins to connect routes, trips, and geographical shapes. Processed the large `shapes.txt` dataset in chunks to avoid loading the entire file into memory.

The resulting coordinates were sorted by shape ID and sequence, enabling geographical route reconstruction.

### 4. Data Storage

Implemented Parquet storage for processed railway shape data to support efficient reuse without repeatedly processing the original large GTFS file.

## Technology Stack

- Python
- pandas
- Folium
- Jupyter Notebook
- GTFS Realtime and GTFS Static
- TfNSW Open Data APIs
- PyArrow / Parquet

## Project Structure

```text
Traffic NSW project/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 01_data_exploration.ipynb
├── src/
│   └── fetch_transport_data.py
├── .env
└── README.md
```

The `.env` file contains local configuration and API credentials and must not be committed to GitHub.

## Next Steps

- Visualise Sydney Trains T1–T9 railway routes using GTFS shapes.
- Overlay real-time train positions onto the railway network.
- Investigate train movements and delays.
- Explore spatial and temporal patterns in train services.
- Develop analytical features for future machine learning experiments.

## Current Status

**In development — Data ingestion, initial exploration, and railway shape extraction completed.**

The next development phase focuses on integrating the static railway network with real-time train positions.
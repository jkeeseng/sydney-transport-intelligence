# Sydney Transport Intelligence

A Python-based data analytics project using Transport for NSW (TfNSW) open data to explore Sydney's public transport network, real-time service conditions, and journey recommendations.

## Project Objectives

- Collect and process real-time transport data from TfNSW APIs.
- Analyse train positions, service updates, delays, and disruptions.
- Reconstruct railway routes using GTFS timetable and geographical data.
- Develop journey recommendations considering travel time, transfers, and connection reliability.

## Work Completed

**1. Real-Time Data Pipeline**
- Built a Python pipeline to retrieve and decode TfNSW JSON and GTFS-Realtime Protocol Buffer feeds.
- Collected 10 datasets covering Sydney Trains, Metro, light rail, traffic stations, and road incidents.
- Saved timestamped raw data and pipeline execution summaries.

**2. Railway Network Analysis**
- Extracted Sydney Trains routes, trips, and geographical shapes from GTFS Static data.
- Processed large geographical datasets in chunks and stored processed data in Parquet format.

| Metric | Result |
|---|---:|
| Scheduled train trips | 48,298 |
| Unique railway shapes | 1,298 |
| Geographical coordinates extracted | 852,072 |

**3. Journey Planning**
- Developed timetable-based journey analysis for alternative routes and transfer stations.
- Evaluated journey duration, number of transfers, and connection buffers.
- Established a minimum five-minute transfer buffer for journey recommendations.

## Technology Stack

Python · pandas · Requests · GTFS Realtime · GTFS Static · Folium · Jupyter Notebook · PyArrow/Parquet

## Next Steps

- Visualise railway routes and real-time train positions on an interactive map.
- Calculate delays by comparing scheduled and predicted arrival times.
- Integrate service alerts and disruptions into journey recommendations.
- Rank alternative journeys using arrival times, transfer reliability, and real-time conditions.

## Current Status

**In development:** Data ingestion and initial timetable-based journey analysis are working. Real-time delay calculations and disruption-aware journey recommendations are the next development priorities.

## Setup

Configure your TfNSW API credentials in a local `.env` file, install the project dependencies, and run:

```bash
python src/fetch_transport_data.py
```

Keep `.env` and API credentials out of version control.

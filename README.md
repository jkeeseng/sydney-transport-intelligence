# Sydney Transport Intelligence

A Python-based transport analytics and journey planning project using Transport for NSW (TfNSW) open data, GTFS timetables and real-time feeds.

The project aims to develop an intelligent journey planner that considers travel time, transfers, connection reliability and real-time service conditions.

## Project Objectives

- Process scheduled and real-time TfNSW transport data.
- Analyse Sydney's train and metro networks.
- Develop journey recommendations based on travel time and transfer feasibility.
- Build an interactive journey planning application.

## Work Completed

**1. Transport Data Pipeline**
- Built Python pipelines to retrieve and decode TfNSW API and GTFS-Realtime data.
- Collected 10 transport datasets and processed GTFS Static timetable data.
- Analysed over 5.7 million stop-time records and 211,000 scheduled trips.

**2. Railway Network Analysis**
- Extracted railway routes, geographical shapes and station information.
- Developed station and platform mappings for journey planning.
- Processed large datasets using pandas and Parquet.

**3. Journey Planning Engine**
- Developed direct, one-transfer and initial two-transfer routing algorithms.
- Implemented Depart At and Arrive By journey searches.
- Added journey recommendations, alternatives and platform-level itineraries.
- Validated train direction, stop sequences and transfer feasibility for direct and one-transfer scheduled journeys.

**4. Date-Aware Timetable Planning**
- Added journey date selection in `DD/MM/YYYY` format.
- Used GTFS service calendars and exceptions to identify scheduled trips for selected dates.
- Built date-specific timetables for future journeys.
- Implemented a date-aware Arrive By planner, with real-time data structures prepared for further integration.

## Technology Stack

Python · pandas · NumPy · Requests · GTFS Static · GTFS-Realtime · Jupyter Notebook · Folium · PyArrow/Parquet · Git

## Next Steps

- Integrate Depart At and validated two-transfer routing into the date-aware planner.
- Incorporate real-time delays and service disruptions into journey recommendations.
- Improve transfer reliability and journey ranking.
- Build and deploy an interactive Streamlit application.
- Visualise transport routes and service conditions on maps.

## Current Status

**In development:** Data ingestion, scheduled timetable processing and date-aware Arrive By journey planning are working. Real-time journey integration and the interactive application are the next priorities.

## Setup

Configure TfNSW API credentials in a local `.env` file, install project dependencies, and run:

```bash
python src/fetch_transport_data.py
```

Keep API credentials and large raw datasets out of version control.

**Data source:** [Transport for NSW Open Data Hub](https://opendata.transport.nsw.gov.au/)
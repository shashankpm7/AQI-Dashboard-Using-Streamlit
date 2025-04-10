# Air Quality Index (AQI) Dashboard

A fully functional and responsive Air Quality Index Dashboard built with Streamlit. This dashboard allows users to visualize and analyze AQI data across multiple cities.

## Features

- **Data Upload**: Upload CSV files containing AQI data or use the built-in sample data generator
- **Interactive Filtering**: Filter data by date range, city, pollutant, and AQI range
- **Visualizations**:
  - Line charts showing AQI trends over time (Plotly)
  - Bar charts comparing average AQI values by city (Altair)
  - Calendar heatmap for daily AQI levels
- **KPI Cards**: Display current AQI, highest/lowest AQI, and most polluted city
- **Data Export**: Download filtered data as CSV

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app with:

```bash
python -m streamlit run main.py
```

The dashboard will open in your default web browser.

## Data Format

If you want to upload your own data, the CSV file should contain at least the following columns:
- `Date`: Date of the AQI measurement (should be convertible to datetime)
- `City`: Name of the city
- `AQI`: Air Quality Index value

Optional column:
- `Pollutant`: Type of pollutant (PM2.5, PM10, O3, etc.)

## Sample Data

The dashboard includes a sample data generator that creates realistic AQI data for demonstration purposes. This is useful if you don't have your own data to upload.

## Screenshots

- The dashboard features a clean, modern UI with interactive widgets
- KPI cards display key metrics at the top of the dashboard
- Multiple visualization tabs allow for different ways to analyze the data

## Dependencies

- Streamlit
- Pandas
- NumPy
- Plotly
- Altair

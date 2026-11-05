# WeatherVista — Historical Weather Data Analysis

Interactive Streamlit dashboard and Jupyter notebook for exploring historical weather features (temperature, humidity, rainfall, wind) from the NOAA GSOD–enriched COVID-19 training dataset (`weather_data.csv`).

## Features

- Sidebar filters for country and date range
- KPI cards: average temperature, highest temperature, average humidity, total days
- Charts: univariate distributions, temperature vs humidity, time series, country comparison, correlation heatmap
- Raw data table toggle and written key findings

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Key findings

1. Temperature varies widely across countries in early 2020; typical values sit in a moderate band after converting to °C.
2. Relative humidity is often moderate, and temperature vs humidity usually shows a mild negative correlation.
3. Most days are dry; measurable rainfall is the minority of observations, with a long wet-day tail.

## Live app

*(Add your Streamlit Cloud URL here after deploying)*

https://share.streamlit.io/

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `weather_data.csv` | Dataset |
| `weather_analysis.ipynb` | Full analysis notebook |
| `requirements.txt` | Python dependencies |

## Dataset source

[Weather Data for COVID-19 Data Analysis (Kaggle)](https://www.kaggle.com/datasets/davidbnn92/weather-data-for-covid19-data-analysis) — file originally named `training_data_with_weather_info_week_1.csv`.

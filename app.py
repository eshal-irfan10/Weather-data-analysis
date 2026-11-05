"""
WeatherVista — Historical Weather Analytics Dashboard
Dark glassmorphism UI over NOAA GSOD weather features.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Page + theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="WeatherVista | Historical Weather Analysis",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent / "weather_data.csv"

SENTINEL_MAP = {"wdsp": 999.9, "prcp": 99.99, "stp": 999.9}

# Palette matching WeatherVista mock
PINK = "#ff4d8d"
BLUE = "#3d9eff"
PURPLE = "#9b6dff"
YELLOW = "#ffc857"
CYAN = "#5eead4"
BG = "#0b0e1b"
CARD = "rgba(22, 27, 48, 0.72)"
TEXT = "#e8ecff"
MUTED = "#9aa3c7"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(12, 16, 32, 0.35)",
    font=dict(color=TEXT, family="Segoe UI, sans-serif", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(size=15, color=TEXT),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
    coloraxis_colorbar=dict(tickfont=dict(color=TEXT)),
)


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Outfit', 'Segoe UI', sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(155, 109, 255, 0.22), transparent 55%),
    radial-gradient(900px 500px at 100% 0%, rgba(61, 158, 255, 0.18), transparent 50%),
    radial-gradient(800px 400px at 50% 100%, rgba(255, 77, 141, 0.12), transparent 55%),
    linear-gradient(160deg, #070912 0%, #0b0e1b 40%, #12162b 100%);
  color: #e8ecff;
}

/* Hide default Streamlit chrome noise */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Sidebar glass */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(14, 18, 36, 0.95), rgba(10, 12, 24, 0.98));
  border-right: 1px solid rgba(155, 109, 255, 0.25);
  box-shadow: 8px 0 40px rgba(61, 158, 255, 0.08);
}
section[data-testid="stSidebar"] * { color: #e8ecff !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stCheckbox label {
  color: #c5cbe8 !important;
  font-weight: 500;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stDateInput input {
  background-color: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(155, 109, 255, 0.35) !important;
  border-radius: 12px !important;
  color: #fff !important;
}

.brand-wrap {
  text-align: center;
  padding: 0.4rem 0 1.2rem 0;
}
.brand-logo {
  font-size: 2.4rem;
  filter: drop-shadow(0 0 12px rgba(255, 200, 87, 0.55));
}
.brand-title {
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  background: linear-gradient(90deg, #fff, #9b6dff, #3d9eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0.15rem 0;
}
.brand-tag {
  color: #9aa3c7 !important;
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero {
  background:
    linear-gradient(120deg, rgba(22, 27, 48, 0.85), rgba(40, 24, 72, 0.55)),
    radial-gradient(circle at 85% 30%, rgba(255,255,255,0.12), transparent 40%);
  border: 1px solid rgba(155, 109, 255, 0.35);
  border-radius: 22px;
  padding: 1.35rem 1.6rem;
  margin-bottom: 1.1rem;
  box-shadow: 0 0 40px rgba(61, 158, 255, 0.12), inset 0 1px 0 rgba(255,255,255,0.08);
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: "☁️";
  position: absolute;
  right: 1.4rem;
  top: 0.9rem;
  font-size: 2.6rem;
  opacity: 0.55;
  filter: drop-shadow(0 0 10px rgba(255,255,255,0.35));
}
.hero h1 {
  margin: 0;
  font-size: 1.85rem;
  font-weight: 700;
  color: #fff;
}
.hero p {
  margin: 0.35rem 0 0 0;
  color: #b7bfd9;
  font-size: 0.98rem;
}

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.9rem; margin-bottom: 1.1rem; }
@media (max-width: 900px) { .kpi-row { grid-template-columns: 1fr 1fr; } }

.kpi {
  background: rgba(22, 27, 48, 0.72);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 1rem 1.05rem;
  box-shadow: 0 8px 28px rgba(0,0,0,0.28), 0 0 24px rgba(155, 109, 255, 0.08);
  backdrop-filter: blur(10px);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.35), 0 0 28px rgba(61, 158, 255, 0.18);
}
.kpi-top { display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-label { color: #9aa3c7; font-size: 0.82rem; font-weight: 500; }
.kpi-value { font-size: 1.65rem; font-weight: 700; color: #fff; margin-top: 0.25rem; }
.kpi-icon {
  width: 38px; height: 38px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.15rem;
}
.kpi-pink .kpi-icon { background: rgba(255, 77, 141, 0.18); box-shadow: 0 0 16px rgba(255, 77, 141, 0.35); }
.kpi-yellow .kpi-icon { background: rgba(255, 200, 87, 0.18); box-shadow: 0 0 16px rgba(255, 200, 87, 0.35); }
.kpi-blue .kpi-icon { background: rgba(61, 158, 255, 0.18); box-shadow: 0 0 16px rgba(61, 158, 255, 0.35); }
.kpi-purple .kpi-icon { background: rgba(155, 109, 255, 0.18); box-shadow: 0 0 16px rgba(155, 109, 255, 0.35); }
.kpi-spark { height: 28px; margin-top: 0.55rem; opacity: 0.9; }

.chart-card {
  background: rgba(22, 27, 48, 0.72);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 0.55rem 0.55rem 0.2rem 0.55rem;
  margin-bottom: 0.9rem;
  box-shadow: 0 8px 28px rgba(0,0,0,0.25), 0 0 22px rgba(61, 158, 255, 0.07);
  backdrop-filter: blur(10px);
}

.findings {
  background: rgba(22, 27, 48, 0.72);
  border: 1px solid rgba(155, 109, 255, 0.28);
  border-radius: 18px;
  padding: 1.2rem 1.35rem;
  box-shadow: 0 0 30px rgba(155, 109, 255, 0.12);
}
.findings h3 { margin: 0 0 0.7rem 0; color: #fff; }
.findings ul { margin: 0; padding-left: 1.1rem; color: #c5cbe8; }
.findings li { margin-bottom: 0.45rem; }

.cta {
  background: linear-gradient(135deg, rgba(155, 109, 255, 0.35), rgba(61, 158, 255, 0.25));
  border: 1px solid rgba(155, 109, 255, 0.45);
  border-radius: 18px;
  padding: 1.2rem 1.1rem;
  text-align: center;
  box-shadow: 0 0 28px rgba(155, 109, 255, 0.25);
}
.cta h4 { margin: 0.4rem 0; color: #fff; }
.cta p { margin: 0; color: #d0d6f0; font-size: 0.9rem; }

.sidebar-foot {
  margin-top: 1.5rem;
  text-align: center;
  color: #9aa3c7 !important;
  font-size: 0.78rem;
  line-height: 1.45;
}
.globe {
  font-size: 3.2rem;
  margin: 1.4rem auto 0.4rem auto;
  text-align: center;
  filter: drop-shadow(0 0 18px rgba(61, 158, 255, 0.65));
  animation: floaty 4s ease-in-out infinite;
}
@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

div[data-testid="stCheckbox"] { padding: 0.35rem 0; }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])

    for col, sentinel in SENTINEL_MAP.items():
        if col in df.columns:
            df[col] = df[col].replace(sentinel, np.nan)

    if "ah" in df.columns:
        df["ah"] = df["ah"].replace([np.inf, -np.inf], np.nan)

    keep = [
        "Country/Region",
        "Province/State",
        "Date",
        "temp",
        "min",
        "max",
        "rh",
        "wdsp",
        "prcp",
        "dewp",
        "fog",
    ]
    df = df[[c for c in keep if c in df.columns]].copy()

    for col in ["temp", "min", "max", "rh", "wdsp", "prcp", "dewp"]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Display helpers (UI shows °C + humidity %)
    df["temp_c"] = (df["temp"] - 32) * 5 / 9
    df["humidity_pct"] = df["rh"] * 100
    df["rainfall_mm"] = df["prcp"] * 25.4

    return df


def filter_data(df: pd.DataFrame, countries: list[str], start_date, end_date) -> pd.DataFrame:
    mask = (df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))
    if countries and "All Countries" not in countries:
        mask &= df["Country/Region"].isin(countries)
    return df.loc[mask].copy()


def kpi_card(label: str, value: str, icon: str, tone: str, spark_y: list[float], color: str) -> str:
    # Tiny inline SVG sparkline
    if len(spark_y) < 2:
        spark_y = [0, 1]
    w, h = 120, 28
    mn, mx = min(spark_y), max(spark_y)
    span = (mx - mn) or 1
    pts = []
    for i, y in enumerate(spark_y):
        x = i / (len(spark_y) - 1) * (w - 4) + 2
        yy = h - 3 - ((y - mn) / span) * (h - 8)
        pts.append(f"{x:.1f},{yy:.1f}")
    poly = " ".join(pts)
    svg = (
        f'<svg class="kpi-spark" viewBox="0 0 {w} {h}" width="100%" height="28" '
        f'preserveAspectRatio="none"><polyline fill="none" stroke="{color}" '
        f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" '
        f'points="{poly}"/></svg>'
    )
    return (
        f'<div class="kpi kpi-{tone}"><div class="kpi-top">'
        f'<div><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>'
        f'<div class="kpi-icon">{icon}</div></div>{svg}</div>'
    )


def style_fig(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=320)
    fig.update_layout(legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)))
    return fig


def main() -> None:
    inject_css()

    if not DATA_PATH.exists():
        st.error(f"Could not find `{DATA_PATH.name}`. Place it next to `app.py`.")
        st.stop()

    df = load_data(str(DATA_PATH))

    # ----- Sidebar -----
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-wrap">
              <div class="brand-logo">🌤️</div>
              <div class="brand-title">WeatherVista</div>
              <div class="brand-tag">Analyze • Explore • Discover</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_countries = sorted(df["Country/Region"].dropna().unique().tolist())
        country_options = ["All Countries"] + all_countries
        selected = st.selectbox("Select Country", options=country_options, index=0)
        countries = [] if selected == "All Countries" else [selected]

        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

        show_raw = st.checkbox("Show Raw Data Table", value=False)

        st.markdown('<div class="globe">🌐</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-foot">Weather Data Analysis<br/>Built with ❤️ using Streamlit</div>',
            unsafe_allow_html=True,
        )

    filtered = filter_data(df, countries, start_date, end_date)
    if filtered.empty:
        st.warning("No rows match the current filters. Broaden country or date range.")
        st.stop()

    # ----- Hero -----
    st.markdown(
        """
        <div class="hero">
          <h1>📊 Historical Weather Analysis</h1>
          <p>Explore weather patterns, discover insights and visualize data across the globe.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- KPIs -----
    daily = filtered.groupby("Date", as_index=False).agg(
        temp_c=("temp_c", "mean"),
        humidity_pct=("humidity_pct", "mean"),
        rainfall_mm=("rainfall_mm", "mean"),
    )
    spark_temp = daily["temp_c"].tolist()[-40:]
    spark_hum = daily["humidity_pct"].tolist()[-40:]
    spark_rain = daily["rainfall_mm"].tolist()[-40:]
    spark_days = list(range(1, min(41, daily.shape[0] + 1)))

    avg_temp = filtered["temp_c"].mean()
    max_temp = filtered["temp_c"].max()
    avg_hum = filtered["humidity_pct"].mean()
    n_days = filtered["Date"].nunique()

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card("Average Temperature", f"{avg_temp:.1f} °C", "🌡️", "pink", spark_temp, PINK)
        + kpi_card("Highest Temperature", f"{max_temp:.1f} °C", "☀️", "yellow", spark_temp, YELLOW)
        + kpi_card("Average Humidity", f"{avg_hum:.1f} %", "💧", "blue", spark_hum, BLUE)
        + kpi_card("Total Days", f"{n_days}", "📅", "purple", spark_days, PURPLE)
        + "</div>",
        unsafe_allow_html=True,
    )

    # ----- Charts row 1 -----
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.histogram(
            filtered,
            x="temp_c",
            nbins=30,
            color_discrete_sequence=[PINK],
        )
        fig.update_traces(marker_line_width=0, opacity=0.9)
        style_fig(fig, "Temperature Distribution")
        fig.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        sample = filtered.sample(n=min(2500, len(filtered)), random_state=42)
        fig = px.scatter(
            sample,
            x="temp_c",
            y="humidity_pct",
            color_discrete_sequence=[BLUE],
            opacity=0.45,
        )
        fig.update_traces(marker=dict(size=6))
        style_fig(fig, "Temperature vs Humidity")
        fig.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Humidity (%)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=daily["Date"],
                y=daily["temp_c"],
                mode="lines+markers",
                line=dict(color=PURPLE, width=2.5),
                marker=dict(size=5, color=PURPLE, line=dict(width=0)),
                fill="tozeroy",
                fillcolor="rgba(155, 109, 255, 0.15)",
            )
        )
        style_fig(fig, "Temperature Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ----- Charts row 2 -----
    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        by_country = (
            filtered.groupby("Country/Region")["temp_c"]
            .agg(["mean", "std", "count"])
            .reset_index()
            .query("count >= 5")
            .sort_values("mean", ascending=False)
            .head(8)
        )
        fig = go.Figure(
            go.Bar(
                x=by_country["Country/Region"],
                y=by_country["mean"],
                error_y=dict(type="data", array=by_country["std"].fillna(0), visible=True, color="rgba(255,255,255,0.35)"),
                marker=dict(
                    color=by_country["mean"],
                    colorscale=[[0, BLUE], [1, PURPLE]],
                    line=dict(width=0),
                ),
            )
        )
        style_fig(fig, "Average Temperature by Country")
        fig.update_layout(xaxis_title="Country", yaxis_title="Avg Temperature (°C)", showlegend=False)
        fig.update_xaxes(tickangle=-25)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        corr_df = filtered[["temp_c", "humidity_pct", "rainfall_mm", "wdsp"]].rename(
            columns={
                "temp_c": "Temperature",
                "humidity_pct": "Humidity",
                "rainfall_mm": "Rainfall",
                "wdsp": "Wind Speed",
            }
        )
        corr = corr_df.corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        style_fig(fig, "Correlation Heatmap")
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        rain = filtered["rainfall_mm"].clip(upper=filtered["rainfall_mm"].quantile(0.98))
        fig = px.histogram(rain, nbins=35, color_discrete_sequence=[PURPLE])
        fig.update_traces(marker_line_width=0, opacity=0.9)
        style_fig(fig, "Rainfall Distribution")
        fig.update_layout(xaxis_title="Rainfall (mm)", yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ----- Findings -----
    temp_rh_corr = filtered[["temp_c", "humidity_pct"]].corr().iloc[0, 1]
    q25, q75 = filtered["temp_c"].quantile([0.25, 0.75])
    rainy_share = (filtered["rainfall_mm"] > 0).mean() * 100
    top_country = filtered.groupby("Country/Region")["temp_c"].mean().idxmax()

    left, right = st.columns([2.2, 1])
    with left:
        st.markdown(
            f"""
            <div class="findings">
              <h3>💡 Key Findings</h3>
              <ul>
                <li>✅ Temperature usually ranges between <b>{q25:.0f}°C</b> and <b>{q75:.0f}°C</b> in the filtered view.</li>
                <li>✅ Average humidity sits near <b>{avg_hum:.1f}%</b> across selected places and dates.</li>
                <li>✅ Temperature vs humidity correlation is <b>{temp_rh_corr:.2f}</b>
                    ({'strong negative' if temp_rh_corr <= -0.5 else 'mild / weak'} link).</li>
                <li>✅ About <b>{rainy_share:.0f}%</b> of days show measurable rainfall; dry days dominate.</li>
                <li>✅ Warmest average among current filters: <b>{top_country}</b>.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="cta">
              <div style="font-size:1.8rem">⭐</div>
              <h4>Keep exploring</h4>
              <p>Switch country and date filters in the sidebar to reshape every chart and KPI.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if show_raw:
        st.markdown("### Raw Data")
        st.dataframe(
            filtered[
                [
                    "Country/Region",
                    "Province/State",
                    "Date",
                    "temp_c",
                    "humidity_pct",
                    "rainfall_mm",
                    "wdsp",
                ]
            ].rename(
                columns={
                    "temp_c": "Temperature (°C)",
                    "humidity_pct": "Humidity (%)",
                    "rainfall_mm": "Rainfall (mm)",
                    "wdsp": "Wind Speed",
                }
            ),
            use_container_width=True,
            height=360,
        )


if __name__ == "__main__":
    main()

"""Generate weather_analysis.ipynb with all assignment steps."""

import json
from pathlib import Path


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip("\n").splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip("\n").splitlines(keepends=True),
    }


cells = []

cells.append(
    md(
        """
# Historical Weather Data Analysis

**Dataset:** `weather_data.csv`  
(source: `training_data_with_weather_info_week_1.csv` — NOAA GSOD weather joined with COVID-19 locations)

---

## Final analysis questions

### Univariate (one column at a time)
1. **How is temperature (`temp`) spread across all locations and days?** What is typical, and how wide is the range?
2. **What does relative humidity (`rh`) look like?** Is the air usually dry, moderate, or humid?
3. **How is precipitation (`prcp`) distributed?** Are most days dry, or do heavy-rain days dominate?

### Bivariate (two columns together)
4. **Is there a relationship between temperature and relative humidity?**
5. **How does average temperature compare across countries?**

### Extra (supported by the data)
6. **How does average temperature change over time (Jan–Mar 2020)?**
7. **Which weather variables are most strongly correlated with each other?**

> Removed / not asked: questions about long-term climate trends or seasons beyond this window — the file only covers **2020-01-22 to 2020-03-23**.
"""
    )
)

cells.append(
    md(
        """
## Setup and first look (Part 1)

Load the file and inspect `head()`, `info()`, and `columns` to identify place, date, and weather fields.
"""
    )
)

cells.append(
    code(
        """
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.figsize"] = (8, 4)
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10

df_raw = pd.read_csv("weather_data.csv")
print("Shape:", df_raw.shape)
df_raw.head()
"""
    )
)

cells.append(
    md(
        "**Explanation:** The table has one row per place per day. Early rows are Afghanistan in late January 2020 with temperature and other weather fields."
    )
)

cells.append(
    code(
        """
df_raw.info()
print("\\nColumns:")
print(list(df_raw.columns))
"""
    )
)

cells.append(
    md(
        """
**Explanation — column groups**
- **Place:** `Country/Region`, `Province/State`, `Lat`, `Long`
- **Date:** `Date`, `day_from_jan_first`
- **Weather:** `temp`, `min`, `max`, `stp`, `slp`, `dewp`, `rh`, `ah`, `wdsp`, `prcp`, `fog`
- **Other (COVID context, not used for weather questions):** `Id`, `ConfirmedCases`, `Fatalities`

Temperatures are in **°F** (NOAA GSOD). `rh` is relative humidity on a 0–1 scale. Sentinel values like `999.9` / `99.99` mean missing.
"""
    )
)

# Step 1
cells.append(md("## Step 1: Basic analysis"))

cells.append(
    code(
        """
print("Shape:", df_raw.shape)
print("\\nData types:\\n", df_raw.dtypes)
df_raw.describe().T
"""
    )
)

cells.append(
    md(
        "**Explanation:** `describe()` shows central tendency and spread. Watch for impossible highs such as `wdsp`/`stp` near 999.9 and `prcp` near 99.99 — those are missing-data codes, not real storms."
    )
)

cells.append(
    code(
        """
df = df_raw.copy()
df["Date"] = pd.to_datetime(df["Date"])

print("First date:", df["Date"].min().date())
print("Last date:", df["Date"].max().date())
print("Number of countries/places:", df["Country/Region"].nunique())
print("Number of province/state values (incl. blank):", df["Province/State"].nunique(dropna=False))
"""
    )
)

cells.append(
    md(
        "**Explanation:** The window is short (about two months in early 2020). Place grain is mostly country; some rows also have a province/state (e.g. US, China)."
    )
)

cells.append(
    code(
        """
# Keep only columns needed for our questions
keep_cols = [
    "Country/Region", "Province/State", "Date",
    "temp", "min", "max", "rh", "wdsp", "prcp", "dewp", "fog",
]
df = df[keep_cols].copy()
print("Kept columns:", list(df.columns))
df.head()
"""
    )
)

cells.append(
    md(
        "**Explanation:** Dropping COVID case counts and station-pressure fields keeps the notebook focused on the weather questions above."
    )
)

# Step 2
cells.append(md("## Step 2: Missing values"))

cells.append(
    code(
        """
# Convert known sentinel / invalid codes to NaN before counting missing values
df["wdsp"] = df["wdsp"].replace(999.9, np.nan)
df["prcp"] = df["prcp"].replace(99.99, np.nan)
df.loc[df["ah"] == np.inf, "ah"] = np.nan if "ah" in df.columns else None

missing = df.isna().sum().sort_values(ascending=False)
missing_pct = (df.isna().mean() * 100).round(2)
missing_table = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
print(missing_table)

fig, ax = plt.subplots()
missing[missing > 0].plot(kind="bar", color="#bc4749", ax=ax)
ax.set_title("Missing Values per Column")
ax.set_xlabel("Column")
ax.set_ylabel("Number of missing values")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """
**Explanation:** After replacing NOAA sentinel codes, some weather fields still have gaps.

| Column | Decision | Why |
|---|---|---|
| `Province/State` | **Keep as-is / leave blank** | Missing means the row is country-level, not an error. |
| `rh`, `dewp`, `min`, `max` | **Fill with median** | Continuous weather; median is robust to extremes. |
| `wdsp`, `prcp` | **Fill with median** after sentinel→NaN | Sensor gaps; previous-day fill is less reliable across countries. |
| Fully empty rows (if any) | **Drop** | A row with no usable weather adds no value. |
"""
    )
)

cells.append(
    code(
        """
for col in ["temp", "min", "max", "rh", "wdsp", "prcp", "dewp"]:
    if col in df.columns and df[col].isna().any():
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"Filled {col} NaNs with median = {median_val:.4f}")

print("\\nMissing after cleaning:")
print(df.isna().sum())
"""
    )
)

cells.append(
    md(
        "**Explanation:** Medians restore complete numeric series for plots and correlations without inventing country-specific time series."
    )
)

# Step 3
cells.append(md("## Step 3: Repeated values"))

cells.append(
    code(
        """
dup_rows = df.duplicated().sum()
print("Fully duplicate rows:", dup_rows)

# One row per place per day: country + province + date should be unique
place_date_dups = df.duplicated(subset=["Country/Region", "Province/State", "Date"]).sum()
print("Duplicate place-date combinations:", place_date_dups)

if place_date_dups == 0 and dup_rows == 0:
    print("\\nno duplicates found")
else:
    before = len(df)
    df = df.drop_duplicates(subset=["Country/Region", "Province/State", "Date"]).copy()
    print(f"Removed {before - len(df)} repeated place-date rows.")
"""
    )
)

cells.append(
    md(
        "**Explanation:** Proof of uniqueness is the duplicate count on `(Country/Region, Province/State, Date)`. If that count is 0, each place has at most one row per day."
    )
)

# Step 4
cells.append(md("## Step 4: Outliers"))

cells.append(
    code(
        """
fig, axes = plt.subplots(2, 3, figsize=(12, 7))

for i, col in enumerate(["temp", "prcp", "wdsp"]):
    sns.boxplot(y=df[col], ax=axes[0, i], color="#457b9d")
    axes[0, i].set_title(f"Box plot — {col}")
    axes[0, i].set_ylabel(col)

    sns.histplot(df[col], bins=40, ax=axes[1, i], color="#2a6f97")
    axes[1, i].set_title(f"Histogram — {col}")
    axes[1, i].set_xlabel(col)

plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        "**Explanation:** Box plots flag points beyond the whiskers; histograms show whether those points form a long realistic tail (storms / deserts / polar cold) or a spike at a bad code."
    )
)

cells.append(
    code(
        """
def iqr_bounds(series: pd.Series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    return q1, q3, iqr, low, high

for col in ["temp", "wdsp"]:
    q1, q3, iqr, low, high = iqr_bounds(df[col])
    mask = (df[col] < low) | (df[col] > high)
    print(f"\\n=== IQR rule for {col} ===")
    print(f"Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f}")
    print(f"Lower={low:.2f}, Upper={high:.2f}")
    print(f"Outlier count: {mask.sum()} ({mask.mean()*100:.1f}%)")
    print(df.loc[mask, ["Country/Region", "Date", col]].sort_values(col).head(3))
    print(df.loc[mask, ["Country/Region", "Date", col]].sort_values(col).tail(3))
"""
    )
)

cells.append(
    md(
        """
**Outlier judgment**
- **`temp` outliers:** Mostly real climate extremes (very cold high-latitude / winter days, or hot tropical days). **Keep them.**
- **`wdsp` outliers:** After removing 999.9, remaining high winds can be real stormy days. **Keep them** unless values are still near the old sentinel.
- **`prcp`:** Heavy rain tails are expected; many zeros are also normal. **Do not delete** storm days.

We **do not remove** weather outliers for the rest of the analysis — they are physically plausible.
"""
    )
)

# Step 5
cells.append(md("## Step 5: Univariate analysis"))

cells.append(
    code(
        """
key_cols = ["temp", "rh", "prcp", "wdsp"]

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes = axes.ravel()
for ax, col in zip(axes, key_cols):
    sns.histplot(df[col], bins=35, kde=True, ax=ax, color="#1b4332")
    ax.set_title(f"Univariate: {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
plt.tight_layout()
plt.show()

summary = df[key_cols].agg(["mean", "median", "std", "min", "max"]).T
summary
"""
    )
)

cells.append(
    md(
        """
**Typical values and spread**
- **`temp`:** Mean/median near the mid-50s °F; standard deviation shows a wide global mix of climates.
- **`rh`:** Often around 0.6–0.7 (moderately humid); spread is smaller than temperature.
- **`prcp`:** Strongly right-skewed — many dry days, few wet extremes.
- **`wdsp`:** Most days have moderate wind; a long right tail covers windy events.
"""
    )
)

# Step 6
cells.append(md("## Step 6: Bivariate analysis"))

cells.append(
    code(
        """
sample = df.sample(n=min(3000, len(df)), random_state=42)

fig, ax = plt.subplots()
ax.scatter(sample["temp"], sample["rh"], alpha=0.35, s=12, c="#2a6f97")
ax.set_title("Scatter: Temperature vs Relative Humidity")
ax.set_xlabel("Temperature (°F)")
ax.set_ylabel("Relative Humidity (0–1)")
plt.show()

print("Pearson correlation (temp vs rh):", df["temp"].corr(df["rh"]).round(3))
"""
    )
)

cells.append(
    md(
        "**Explanation:** The cloud often slopes gently downward: warmer observations tend to be a bit drier on average, but the link is not perfect."
    )
)

cells.append(
    code(
        """
weather_cols = ["temp", "min", "max", "rh", "wdsp", "prcp", "dewp"]
corr = df[weather_cols].corr()

fig, ax = plt.subplots(figsize=(7, 5.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Heatmap of Weather Variables")
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        "**Explanation:** `temp`, `min`, and `max` are strongly linked (same day’s thermal range). `dewp` tracks moisture with temperature; `prcp` and `wdsp` are usually weakly correlated with mean temperature."
    )
)

cells.append(
    code(
        """
daily_temp = df.groupby("Date", as_index=False)["temp"].mean()

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(daily_temp["Date"], daily_temp["temp"], color="#bc4749", linewidth=2)
ax.set_title("Line Chart: Global Average Temperature Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Average Temperature (°F)")
fig.autofmt_xdate()
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        "**Explanation:** The series moves with the calendar from deep winter toward early spring in the Northern Hemisphere (most rows), so averages tend to rise slowly."
    )
)

cells.append(
    code(
        """
top_countries = (
    df.groupby("Country/Region")["temp"]
      .mean()
      .sort_values(ascending=False)
      .head(15)
)

fig, ax = plt.subplots(figsize=(8, 5))
top_countries.sort_values().plot(kind="barh", color="#457b9d", ax=ax)
ax.set_title("Bar Chart: Average Temperature by Country (Top 15)")
ax.set_xlabel("Average Temperature (°F)")
ax.set_ylabel("Country / Region")
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        "**Explanation:** Tropical and subtropical countries sit at the top; high-latitude countries are cooler on average in this winter–spring window."
    )
)

# Step 7
cells.append(md("## Step 7: Answers to the questions"))

cells.append(
    code(
        """
# Q1 — Temperature spread
fig, ax = plt.subplots()
sns.histplot(df["temp"], bins=30, kde=True, color="#2a6f97", ax=ax)
ax.set_title("Q1: How is temperature spread?")
ax.set_xlabel("Temperature (°F)")
ax.set_ylabel("Count")
plt.show()
print(df["temp"].describe())
"""
    )
)

cells.append(
    md(
        "**Answer (Q1):** Temperature is roughly bell-shaped but wide. Typical values sit near the mid-50s °F, while the full range runs from well below freezing to near 100 °F because the file mixes polar, temperate, and tropical places."
    )
)

cells.append(
    code(
        """
# Q2 — Humidity
fig, ax = plt.subplots()
sns.boxplot(x=df["rh"], color="#1b4332", ax=ax)
ax.set_title("Q2: Relative humidity spread")
ax.set_xlabel("Relative Humidity (0–1)")
plt.show()
print(df["rh"].describe())
"""
    )
)

cells.append(
    md(
        "**Answer (Q2):** Relative humidity is typically moderate (often around 0.6–0.7). Very dry and near-saturated days exist, but the middle of the distribution is not extreme."
    )
)

cells.append(
    code(
        """
# Q3 — Precipitation
fig, ax = plt.subplots()
sns.histplot(df["prcp"].clip(upper=3), bins=40, color="#4a4e69", ax=ax)
ax.set_title("Q3: Precipitation distribution (clipped at 3 in)")
ax.set_xlabel("Precipitation (inches)")
ax.set_ylabel("Count")
plt.show()
print("Share of dry days (prcp == 0):", f"{(df['prcp'] == 0).mean()*100:.1f}%")
print(df["prcp"].describe())
"""
    )
)

cells.append(
    md(
        "**Answer (Q3):** Precipitation is heavily skewed. Most days are dry or nearly dry; a minority of wet days create the long right tail. Heavy-rain days are real but uncommon."
    )
)

cells.append(
    code(
        """
# Q4 — temp vs rh
fig, ax = plt.subplots()
sns.scatterplot(data=sample, x="temp", y="rh", alpha=0.35, s=20, ax=ax)
ax.set_title("Q4: Temperature vs humidity")
ax.set_xlabel("Temperature (°F)")
ax.set_ylabel("Relative Humidity")
plt.show()
print("Correlation:", round(df["temp"].corr(df["rh"]), 3))
"""
    )
)

cells.append(
    md(
        "**Answer (Q4):** Temperature and humidity are usually weakly negatively correlated. Warmer rows trend slightly less humid, but humidity still varies a lot at any given temperature."
    )
)

cells.append(
    code(
        """
# Q5 — average temperature by country
avg_by_country = df.groupby("Country/Region")["temp"].mean().sort_values(ascending=False)
display_df = avg_by_country.head(10).to_frame("avg_temp_F")
print(display_df)

fig, ax = plt.subplots(figsize=(8, 4))
avg_by_country.head(10).sort_values().plot(kind="barh", ax=ax, color="#457b9d")
ax.set_title("Q5: Top 10 countries by average temperature")
ax.set_xlabel("Average Temperature (°F)")
ax.set_ylabel("Country")
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        "**Answer (Q5):** Average temperature differs sharply by country. Low-latitude countries dominate the warmest averages; colder averages belong to higher-latitude or winter-heavy regions."
    )
)

cells.append(
    code(
        """
# Q6 — temperature over time (already plotted; short numeric answer)
print(daily_temp.head(3))
print(daily_temp.tail(3))
print("Change (last - first day avg):", round(daily_temp["temp"].iloc[-1] - daily_temp["temp"].iloc[0], 2), "°F")
"""
    )
)

cells.append(
    md(
        "**Answer (Q6):** Global average temperature drifts upward from late January into March 2020, consistent with Northern Hemisphere seasonal warming in this sample."
    )
)

cells.append(
    code(
        """
# Q7 — strongest correlations
c = corr.copy()
np.fill_diagonal(c.values, np.nan)
pairs = (
    c.stack()
     .abs()
     .sort_values(ascending=False)
     .drop_duplicates()
     .head(5)
)
print("Strongest |correlation| pairs:")
print(pairs)
"""
    )
)

cells.append(
    md(
        "**Answer (Q7):** The strongest links are among `temp` / `min` / `max` (same-day thermal measures). Moisture variables (`dewp`, `rh`) form a second group; wind and rainfall are weaker partners of temperature."
    )
)

# Step 8
cells.append(
    md(
        """
## Step 8: Conclusion

1. The dataset covers **many countries** over a short early-2020 window, with **one weather snapshot per place per day**.
2. **Temperature** varies widely because cold and hot climates are mixed in the same file; typical values sit in the **50s °F**.
3. **Humidity** is usually moderate; **rainfall** is skewed toward dry days with occasional wet extremes.
4. **Temperature vs humidity** shows a mild inverse pattern, not a strict rule.
5. **Country averages** reflect geography: tropical places run warmer than high-latitude places in this season.
6. After fixing NOAA sentinel missing codes, remaining “outliers” look like **real weather**, so they were kept for analysis and for the Streamlit dashboard.
"""
    )
)

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

out = Path("weather_analysis.ipynb")
out.write_text(json.dumps(nb, indent=2), encoding="utf-8")
print(f"Wrote {out.resolve()} with {len(cells)} cells")

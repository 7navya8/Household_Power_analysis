"""
Household Energy Analysis - UCI Household Electric Power Consumption dataset
Run:  python energy_analysis.py
Put household_power_consumption.txt in the same folder as this script.
Requires: pip install pandas matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt

FILE = "household_power_consumption.txt"

# ASSUMPTIONS - update these and cite your sources in the README
EMISSION_FACTOR = 0.71   # kg CO2 per kWh. Replace with the latest CEA CO2 Baseline Database value
TARIFF = 7.0             # Rs per kWh. Replace with your BESCOM average cost per unit

# ---------------------------------------------------------------
# 1. LOAD AND CLEAN
# ---------------------------------------------------------------
df = pd.read_csv(FILE, sep=";", na_values=["?", ""], low_memory=False)
print("Rows loaded:", len(df))
print("Missing values per column:\n", df.isna().sum(), "\n")

df["datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S"
)
df = df.drop(columns=["Date", "Time"]).set_index("datetime").sort_index()

before = len(df)
df = df[~df.index.duplicated(keep="first")]
print("Duplicate timestamps removed:", before - len(df))

num_cols = [
    "Global_active_power", "Global_reactive_power", "Voltage",
    "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3",
]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

missing_rows = df["Global_active_power"].isna().sum()
print(f"Rows with missing readings: {missing_rows} ({missing_rows / len(df):.2%})")
df = df.dropna(subset=["Global_active_power"])
df = df[df["Global_active_power"] >= 0]

# ---------------------------------------------------------------
# 2. CONVERT TO kWh
# Global_active_power is in kW (average over 1 minute) -> kWh = kW / 60
# Sub_metering values are in Wh per minute -> kWh = Wh / 1000
# ---------------------------------------------------------------
df["total_kwh"] = df["Global_active_power"] / 60
df["kitchen_kwh"] = df["Sub_metering_1"] / 1000
df["laundry_kwh"] = df["Sub_metering_2"] / 1000
df["heater_ac_kwh"] = df["Sub_metering_3"] / 1000
df["other_kwh"] = (
    df["total_kwh"] - df["kitchen_kwh"] - df["laundry_kwh"] - df["heater_ac_kwh"]
).clip(lower=0)

energy_cols = ["total_kwh", "kitchen_kwh", "laundry_kwh", "heater_ac_kwh", "other_kwh"]

# ---------------------------------------------------------------
# 3. DAILY AND MONTHLY TOTALS
# ---------------------------------------------------------------
daily = df[energy_cols].resample("D").sum()
monthly = df[energy_cols].resample("MS").sum()

# Drop incomplete first/last months so they don't distort the trend
monthly = monthly.iloc[1:-1]

monthly["cost_rs"] = monthly["total_kwh"] * TARIFF
monthly["co2_kg"] = monthly["total_kwh"] * EMISSION_FACTOR

# ---------------------------------------------------------------
# 4. PEAK HOURS
# ---------------------------------------------------------------
hourly_profile = df["total_kwh"].groupby(df.index.hour).mean() * 60  # average kW by hour
peak_hour = hourly_profile.idxmax()
print(f"\nPeak usage hour: {peak_hour}:00 (avg {hourly_profile.max():.2f} kW)")

# ---------------------------------------------------------------
# 5. ANOMALY DETECTION (daily kWh above mean + 2 std)
# ---------------------------------------------------------------
mean, std = daily["total_kwh"].mean(), daily["total_kwh"].std()
threshold = mean + 2 * std
daily["is_anomaly"] = daily["total_kwh"] > threshold
print(f"Daily mean: {mean:.2f} kWh | threshold: {threshold:.2f} kWh")
print("Anomalous days:", int(daily["is_anomaly"].sum()))

# ---------------------------------------------------------------
# 6. APPLIANCE-AREA SHARE
# ---------------------------------------------------------------
share = (df[energy_cols[1:]].sum() / df["total_kwh"].sum() * 100).round(1)
print("\nShare of consumption (%):\n", share)

# ---------------------------------------------------------------
# 7. SUMMARY NUMBERS FOR THE README / RESUME
# ---------------------------------------------------------------
total_kwh = df["total_kwh"].sum()
print(f"\nTotal consumption: {total_kwh:,.0f} kWh")
print(f"Estimated CO2: {total_kwh * EMISSION_FACTOR / 1000:,.1f} tonnes")
print(f"Estimated cost: Rs {total_kwh * TARIFF:,.0f}")

# ---------------------------------------------------------------
# 8. SAVE TABLES
# ---------------------------------------------------------------
daily.to_csv("daily_summary.csv")
monthly.to_csv("monthly_summary.csv")

# ---------------------------------------------------------------
# 9. CHARTS
# ---------------------------------------------------------------
plt.figure(figsize=(10, 4))
plt.plot(monthly.index, monthly["total_kwh"], marker="o")
plt.title("Monthly electricity consumption")
plt.ylabel("kWh")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("chart_monthly_trend.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 4))
plt.bar(hourly_profile.index, hourly_profile.values)
plt.title("Average load by hour of day")
plt.xlabel("Hour")
plt.ylabel("Average kW")
plt.tight_layout()
plt.savefig("chart_peak_hours.png", dpi=150)
plt.close()

plt.figure(figsize=(12, 4))
plt.plot(daily.index, daily["total_kwh"], linewidth=0.6, label="Daily kWh")
an = daily[daily["is_anomaly"]]
plt.scatter(an.index, an["total_kwh"], color="red", s=12, label="Anomaly")
plt.axhline(threshold, color="gray", linestyle="--", label="Mean + 2 SD")
plt.title("Daily consumption with anomalies")
plt.ylabel("kWh")
plt.legend()
plt.tight_layout()
plt.savefig("chart_anomalies.png", dpi=150)
plt.close()

plt.figure(figsize=(6, 4))
share.plot(kind="bar")
plt.title("Share of consumption by circuit (%)")
plt.ylabel("%")
plt.tight_layout()
plt.savefig("chart_share.png", dpi=150)
plt.close()

print("\nDone. Saved daily_summary.csv, monthly_summary.csv and 4 charts.")
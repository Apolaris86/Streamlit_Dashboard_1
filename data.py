"""Dummy data generation for the Inbound Delivery Visibility Dashboard."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

SUPPLIERS = ["Eaton", "ABB", "Siemens", "Legrand", "Schneider", "Honeywell"]
PLANTS = ["Plant A - Lyon", "Plant B - Nashville", "Plant C - Chennai", "Plant D - Wroclaw"]
CARRIERS = ["DHL", "FedEx", "Maersk", "DB Schenker", "Kuehne+Nagel"]
MATERIAL_CATEGORIES = ["Electronics", "Mechanical", "Raw Material", "Packaging", "Electrical"]
RISK_LEVELS = ["Low", "Medium", "High"]

SUPPLIER_RISK_BASE = {
    "Eaton": {"delay": 5.0, "risk": "High", "score": 90},
    "ABB": {"delay": 4.0, "risk": "High", "score": 80},
    "Siemens": {"delay": 3.0, "risk": "Medium", "score": 55},
    "Legrand": {"delay": 1.0, "risk": "Low", "score": 20},
    "Schneider": {"delay": 1.8, "risk": "Low", "score": 25},
    "Honeywell": {"delay": 2.6, "risk": "Medium", "score": 45},
}

def _delay_bucket(days):
    if days <= 0:
        return "On Time"
    if days <= 1:
        return "0 - 1 Day"
    if days <= 3:
        return "1 - 3 Days"
    if days <= 5:
        return "3 - 5 Days"
    return "> 5 Days"

def generate_deliveries(n=120, start_date=datetime(2025, 7, 1), days_span=31):
    rows = []
    for i in range(n):
        supplier = np.random.choice(SUPPLIERS)
        base = SUPPLIER_RISK_BASE[supplier]
        eta = start_date + timedelta(days=int(np.random.randint(0, days_span)))
        delay = max(0, int(np.round(np.random.normal(base["delay"], 1.5))))
        actual = eta + timedelta(days=delay)
        status = "On Time" if delay <= 0 else "Delayed"
        rows.append({
            "PO": f"45{1200 + i}",
            "Supplier": supplier,
            "Plant": np.random.choice(PLANTS),
            "Carrier": np.random.choice(CARRIERS),
            "Material Category": np.random.choice(MATERIAL_CATEGORIES),
            "ETA": eta,
            "Actual Arrival": actual,
            "Delay (Days)": delay,
            "Delay Bucket": _delay_bucket(delay),
            "Status": status,
            "Risk Level": base["risk"],
        })
    return pd.DataFrame(rows)

def supplier_risk_table(df):
    grp = df.groupby("Supplier").agg(
        **{"Average Delay (Days)": ("Delay (Days)", "mean")}
    ).reset_index()
    grp["Risk Level"] = grp["Supplier"].map(lambda s: SUPPLIER_RISK_BASE[s]["risk"])
    grp["Risk Score"] = grp["Supplier"].map(lambda s: SUPPLIER_RISK_BASE[s]["score"])
    grp = grp.sort_values("Risk Score", ascending=False)
    grp["Average Delay (Days)"] = grp["Average Delay (Days)"].round(2)
    return grp

def delay_trend(df):
    trend = df.groupby(df["ETA"].dt.date).agg(
        **{"Average Delay (Days)": ("Delay (Days)", "mean")}
    ).reset_index().rename(columns={"ETA": "Date"})
    trend = trend.sort_values("Date")
    trend["Average Delay (Days)"] = trend["Average Delay (Days)"].round(2)
    return trend

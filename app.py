import streamlit as st
import pandas as pd
import numpy as np
import json

st.set_page_config(page_title="AgriConnect+", layout="centered")

st.title("🌾 AgriConnect+")
st.subheader("Crop vs Lease Income Analysis")

# -------------------------------
# SAFE DATA LOAD
# -------------------------------
@st.cache_data
def load_data():
    prices = pd.read_csv("crop_prices.csv")
    yields = pd.read_csv("crop_yield.csv")

    # Fix string issues
    for col in ["state", "district", "crop"]:
        prices[col] = prices[col].astype(str)

    for col in ["state", "crop"]:
        yields[col] = yields[col].astype(str)

    with open("lease_rates.json") as f:
        lease = json.load(f)

    with open("district_lease_rates.json") as f:
        dlease = json.load(f)

    return prices, yields, lease, dlease


price_df, yield_df, STATE_LEASE, DISTRICT_LEASE = load_data()

# -------------------------------
# HELPERS (SAFE)
# -------------------------------
def get_price(state, district, crop):
    row = price_df[
        (price_df["state"].str.lower() == state.lower()) &
        (price_df["district"].str.lower() == district.lower()) &
        (price_df["crop"].str.lower() == crop.lower())
    ]
    if row.empty:
        return None
    return float(row.iloc[0]["avg_price_quintal"])


def get_yield(state, crop):
    row = yield_df[
        (yield_df["state"].str.lower() == state.lower()) &
        (yield_df["crop"].str.lower() == crop.lower())
    ]
    if row.empty:
        return 4000
    return float(row.iloc[0]["avg_yield_kg_ha"])


def get_lease(state, district):
    return DISTRICT_LEASE.get(district, STATE_LEASE.get(state, {"avg": 25000}))["avg"]


# -------------------------------
# INPUTS
# -------------------------------
states = sorted(price_df["state"].unique())
state = st.selectbox("State", states)

districts = sorted(price_df[price_df["state"] == state]["district"].unique())
district = st.selectbox("District", districts)

crops = sorted(price_df[
    (price_df["state"] == state) &
    (price_df["district"] == district)
]["crop"].unique())

crop = st.selectbox("Crop", crops)

years = st.slider("Years", 1, 10, 3)
acres = st.number_input("Land (Acres)", 1.0, 100.0, 2.0)

if st.button("Generate Report"):

    price = get_price(state, district, crop)
    yield_kg = get_yield(state, crop)
    lease = get_lease(state, district)

    if price is None:
        st.error("Price data not available")
        st.stop()

    # -------------------------------
    # CALCULATIONS
    # -------------------------------
    yield_quintal = (yield_kg / 100) / 2.47
    revenue = yield_quintal * price
    cost = 15000

    profit_per_year = revenue - cost
    total_crop = profit_per_year * acres * years
    total_lease = lease * acres * years

    diff = total_crop - total_lease

    # -------------------------------
    # SIMPLE REPORT (MAIN PART)
    # -------------------------------
    st.markdown("## 📄 Farmer Income Report")

    st.markdown(f"""
    **Location:** {district}, {state}  
    **Crop:** {crop}  
    **Land Size:** {acres} acres  
    **Duration:** {years} years  
    """)

    st.markdown("### 💰 Income Comparison")

    st.markdown(f"""
    - Crop Farming Income: **₹{total_crop:,.0f}**  
    - Lease Income: **₹{total_lease:,.0f}**
    """)

    st.markdown("### 📊 Final Analysis")

    if diff > 0:
        st.success(f"""
        ✅ Crop farming is more profitable.

        You will earn approximately **₹{diff:,.0f} more** than leasing.

        This is because the market price and yield are favorable for this crop.
        """)
    else:
        st.warning(f"""
        ⚠️ Leasing is a better option.

        You will earn approximately **₹{abs(diff):,.0f} more** by leasing your land.

        This reduces risk and ensures stable income.
        """)

    st.markdown("### 📌 Recommendation")

    if diff > 0:
        st.markdown("👉 Go for **Crop Farming**")
    else:
        st.markdown("👉 Go for **Leasing**")

    st.markdown("---")
    st.caption("AgriConnect+ | Simple Decision Support for Farmers")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np

# ═══════════════════════════════════════════════════════
# Load Data
# ═══════════════════════════════════════════════════════
@st.cache_data
def load_data():
    prices = pd.read_csv("crop_prices.csv")
    yields = pd.read_csv("crop_yield.csv")
    with open("lease_rates.json") as f:
        lease_rates = json.load(f)
    with open("district_lease_rates.json") as f:
        district_rates = json.load(f)
    return prices, yields, lease_rates, district_rates

price_df, yield_df, STATE_LEASE_RATES, DISTRICT_LEASE_RATES = load_data()
DEFAULT_LEASE = {"min": 15000, "avg": 25000, "max": 40000}

# ═══════════════════════════════════════════════════════
# Crop Growing Cycles per Year
# ═══════════════════════════════════════════════════════
CROP_CYCLES = {
    'Amaranthus': 3, 'Banana': 1, 'Beans': 2, 'Beetroot': 2,
    'Bitter Gourd': 2, 'Bottle Gourd': 2, 'Brinjal': 2,
    'Cabbage': 2, 'Capsicum': 2, 'Carrot': 2, 'Cauliflower': 2,
    'Coconut': 1, 'Cotton': 1, 'Garlic': 1, 'Grapes': 1,
    'Green Chilli': 2, 'Groundnut': 2, 'Guava': 1, 'Lemon': 1,
    'Maize': 2, 'Mango': 1, 'Mustard': 1, 'Onion': 2,
    'Orange': 1, 'Papaya': 1, 'Pomegranate': 1, 'Potato': 2,
    'Pumpkin': 2, 'Rice': 2, 'Soyabean': 1, 'Spinach': 3,
    'Sugarcane': 1, 'Sunflower': 2, 'Tomato': 3,
    'Turmeric': 1, 'Wheat': 1,
}

# ═══════════════════════════════════════════════════════
# Farming Cost per Acre per Cycle (Rs)
# ═══════════════════════════════════════════════════════
FARMING_COSTS = {
    'Amaranthus': 4000, 'Banana': 35000, 'Beans': 6000,
    'Beetroot': 5000, 'Bitter Gourd': 6000, 'Bottle Gourd': 5000,
    'Brinjal': 6000, 'Cabbage': 6000, 'Capsicum': 9000,
    'Carrot': 7500, 'Cauliflower': 7000, 'Coconut': 20000,
    'Cotton': 18000, 'Garlic': 25000, 'Grapes': 45000,
    'Green Chilli': 7500, 'Groundnut': 9000, 'Guava': 20000,
    'Lemon': 18000, 'Maize': 6000, 'Mango': 20000,
    'Mustard': 10000, 'Onion': 9000, 'Orange': 20000,
    'Papaya': 22000, 'Pomegranate': 35000, 'Potato': 10000,
    'Pumpkin': 5000, 'Rice': 11000, 'Soyabean': 10000,
    'Spinach': 2700, 'Sugarcane': 25000, 'Sunflower': 5000,
    'Tomato': 6000, 'Turmeric': 22000, 'Wheat': 12000,
}

# ═══════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════
def get_districts(state):
    rows = price_df[price_df["state"].str.lower() == state.lower()]
    return sorted(rows["district"].dropna().unique().tolist())

def get_crops(state, district):
    rows = price_df[
        (price_df["state"].str.lower()    == state.lower()) &
        (price_df["district"].str.lower() == district.lower())
    ]
    return sorted(rows["crop"].dropna().unique().tolist())

def get_price(state, district, crop):
    row = price_df[
        (price_df["state"].str.lower()    == state.lower()) &
        (price_df["district"].str.lower() == district.lower()) &
        (price_df["crop"].str.lower()     == crop.lower())
    ]
    return float(row["avg_price_quintal"].values[0]) if not row.empty else None

def get_yield(state, crop, irrigation):
    row = yield_df[
        (yield_df["state"].str.lower() == state.lower()) &
        (yield_df["crop"].str.lower()  == crop.lower())
    ]
    if not row.empty:
        base = float(row["avg_yield_kg_ha"].values[0])
    else:
        nat  = yield_df[yield_df["crop"].str.lower() == crop.lower()]
        base = float(nat["avg_yield_kg_ha"].mean()) if not nat.empty else 4000
    return base * 0.8 if irrigation == "Rainfed" else base * 1.2

def get_lease_rate(state, district):
    if district in DISTRICT_LEASE_RATES:
        return DISTRICT_LEASE_RATES[district]
    return STATE_LEASE_RATES.get(state, DEFAULT_LEASE)

# ═══════════════════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════════════════
st.set_page_config(page_title="AgriConnect+", page_icon="🌾", layout="centered")
st.title("🌾 AgriConnect+")
st.subheader("Crop Income vs Lease Income Comparison")
st.markdown("**Find whether farming or leasing gives you more profit — year by year!**")
st.divider()

# ═══════════════════════════════════════════════════════
# Inputs
# ═══════════════════════════════════════════════════════
available_states = sorted(price_df["state"].dropna().unique().tolist())

col1, col2 = st.columns(2)
with col1:
    state    = st.selectbox("📍 State", available_states)
with col2:
    districts = get_districts(state)
    district  = st.selectbox("🏘️ District", districts)

col3, col4 = st.columns(2)
with col3:
    crops = get_crops(state, district)
    crop  = st.selectbox("🌱 Crop", crops if crops else ["No crops found"])
with col4:
    irrigation = st.selectbox("💧 Irrigation Type", ["Irrigated", "Rainfed"])

col5, col6 = st.columns(2)
with col5:
    year_options = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0,
                    6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0]
    years = st.selectbox("📅 Number of Years",
                         options=year_options,
                         index=1,
                         format_func=lambda x: f"{x} {'year' if x == 1 else 'years'}")
with col6:
    acres = st.number_input("🏡 Land Size (Acres)", 0.5, 1000.0, 2.0, step=0.5)

st.divider()

# ═══════════════════════════════════════════════════════
# Price, Yield, Cycles
# ═══════════════════════════════════════════════════════
price    = get_price(state, district, crop)
yield_kg = get_yield(state, crop, irrigation)
cycles   = CROP_CYCLES.get(crop, 1)

risk = st.radio("📊 Market Scenario",
                ["Low (Bad Season)", "Average", "High (Good Season)"],
                index=1, horizontal=True)

if price:
    if "Low"  in risk: price_used = price * 0.8
    elif "High" in risk: price_used = price * 1.2
    else:               price_used = price
else:
    price_used = st.number_input("Enter price manually (Rs/quintal)",
                                  0.0, 100000.0, 2500.0)

c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"📊 **Mandi Price**\n\n₹{price_used:,.0f}/quintal")
with c2:
    st.info(f"🌾 **Yield**\n\n{yield_kg:,.0f} kg/ha")
with c3:
    st.info(f"🔄 **Cycles/Year**\n\n{cycles} {'cycle' if cycles==1 else 'cycles'}")

st.divider()

# ═══════════════════════════════════════════════════════
# Lease Rate
# ═══════════════════════════════════════════════════════
lease_data = get_lease_rate(state, district)
lease_min  = lease_data["min"]
lease_avg  = lease_data["avg"]
lease_max  = lease_data["max"]

st.markdown("### 🏠 Lease Rate")
location   = f"{district}, {state}"
st.info(f"📍 **{location}** lease rates per acre/year:\n\n"
        f"Min: ₹{lease_min:,} | Avg: ₹{lease_avg:,} | Max: ₹{lease_max:,}\n\n"
        f"*(Source: NITI Aayog Agricultural Land Leasing Report)*")

lease_choice   = st.radio("Select lease rate:",
                           ["Minimum", "Average", "Maximum", "Enter Manually"],
                           index=1, horizontal=True)

if lease_choice == "Enter Manually":
    lease_per_acre = st.number_input(
        "Enter your actual local lease rate (Rs/acre/year):",
        min_value=1000,
        max_value=500000,
        value=lease_avg,
        step=1000,
        help="Ask local farmers or check with your taluk office"
    )
else:
    lease_per_acre = {"Minimum": lease_min,
                      "Average": lease_avg,
                      "Maximum": lease_max}[lease_choice]

st.divider()

# ═══════════════════════════════════════════════════════
# Compare Button
# ═══════════════════════════════════════════════════════
if st.button("🔍 Compare Income", use_container_width=True, type="primary"):

    yield_quintal_acre   = (yield_kg / 100) / 2.47
    gross_per_cycle_acre = yield_quintal_acre * price_used
    cost_per_cycle_acre  = FARMING_COSTS.get(crop, 15000)
    net_per_cycle_acre   = gross_per_cycle_acre - cost_per_cycle_acre
    net_per_year_acre    = net_per_cycle_acre * cycles

    total_crop  = net_per_year_acre  * acres * years
    total_lease = lease_per_acre     * acres * years
    total_diff  = total_crop - total_lease
    better      = "🌾 Crop Farming" if total_diff > 0 else "🏠 Leasing Land"
    margin_pct  = abs(total_diff / total_lease) * 100 if total_lease > 0 else 0

    # Metrics
    st.markdown("## 📊 Results")
    m1, m2, m3 = st.columns(3)
    m1.metric("🌾 Total Crop Income",  f"₹{total_crop:,.0f}",
              f"₹{net_per_year_acre*acres:,.0f}/year")
    m2.metric("🏠 Total Lease Income", f"₹{total_lease:,.0f}",
              f"₹{lease_per_acre*acres:,.0f}/year")
    m3.metric("💰 Difference",         f"₹{abs(total_diff):,.0f}",
              f"{margin_pct:.1f}% advantage")

    st.divider()

    if total_diff > 0:
        st.success(f"✅ **Best Option: {better}**\n\n"
                   f"Growing **{crop}** on your {acres}-acre land in "
                   f"**{location}** over {years} years gives "
                   f"**₹{abs(total_diff):,.0f} MORE** than leasing!")
    else:
        st.warning(f"⚠️ **Best Option: {better}**\n\n"
                   f"Leasing your {acres}-acre land in **{location}** "
                   f"over {years} years gives "
                   f"**₹{abs(total_diff):,.0f} MORE** than growing {crop}.")

    st.divider()

    # Year-by-Year Breakdown
    st.markdown("### 📅 Year-by-Year Breakdown")

    step    = 0.5 if years <= 3 else 1.0
    periods = np.arange(step, years + step/2, step)

    year_labels   = []
    crop_incomes  = []
    lease_incomes = []

    for y in periods:
        label = f"Year {y:.1f}" if step == 0.5 else f"Year {int(y)}"
        year_labels.append(label)
        crop_incomes.append(net_per_year_acre * acres * step)
        lease_incomes.append(lease_per_acre   * acres * step)

    cum_crop  = np.cumsum(crop_incomes)
    cum_lease = np.cumsum(lease_incomes)

    breakdown_df = pd.DataFrame({
        "Period":                year_labels,
        "Crop Income (Period)":  [f"₹{v:,.0f}" for v in crop_incomes],
        "Lease Income (Period)": [f"₹{v:,.0f}" for v in lease_incomes],
        "Cumulative Crop":       [f"₹{v:,.0f}" for v in cum_crop],
        "Cumulative Lease":      [f"₹{v:,.0f}" for v in cum_lease],
        "Better Option":         ["🌾 Farm" if c > l else "🏠 Lease"
                                  for c, l in zip(crop_incomes, lease_incomes)]
    })
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.divider()

    # Charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    x     = np.arange(len(year_labels))
    width = 0.35
    ax1.bar(x - width/2, crop_incomes,  width, label="Crop Income",
            color="#2ecc71")
    ax1.bar(x + width/2, lease_incomes, width, label="Lease Income",
            color="#e74c3c")
    ax1.set_title(f"{crop} — {location}\nPeriod Income ({acres} acres)",
                  fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(year_labels, rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Income (₹)")
    ax1.legend()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    ax2.plot(year_labels, cum_crop,  "o-", color="#2ecc71",
             linewidth=2, markersize=5, label="Cumulative Crop")
    ax2.plot(year_labels, cum_lease, "s-", color="#e74c3c",
             linewidth=2, markersize=5, label="Cumulative Lease")
    ax2.fill_between(range(len(year_labels)), cum_crop, cum_lease,
                     alpha=0.1,
                     color="#2ecc71" if total_diff > 0 else "#e74c3c")
    ax2.set_title(f"Cumulative Income over {years} Years",
                  fontsize=11, fontweight="bold")
    ax2.set_xticks(range(len(year_labels)))
    ax2.set_xticklabels(year_labels, rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Cumulative Income (₹)")
    ax2.legend()
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

    st.divider()

    # Summary
    st.markdown("### 📋 Summary")
    summary = pd.DataFrame({
        "Parameter": [
            "State", "District", "Crop", "Years", "Land Size",
            "Irrigation", "Market Scenario", "Mandi Price",
            "Yield", "Crop Cycles/Year", "Cost/Cycle/Acre",
            "Net Crop/Year", "Lease Rate/Acre/Year",
            "Total Crop Income", "Total Lease Income",
            "Difference", "Best Option"
        ],
        "Value": [
            state, district, crop, f"{years} years",
            f"{acres} acres", irrigation, risk,
            f"₹{price_used:,.0f}/quintal", f"{yield_kg:,.0f} kg/ha",
            str(cycles), f"₹{cost_per_cycle_acre:,}",
            f"₹{net_per_year_acre*acres:,.0f}",
            f"₹{lease_per_acre:,}",
            f"₹{total_crop:,.0f}", f"₹{total_lease:,.0f}",
            f"₹{abs(total_diff):,.0f}", better
        ]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption(f"ℹ️ Lease rates for {location}: "
               f"₹{lease_min:,}–₹{lease_max:,}/acre/year. "
               f"Using **{lease_choice.lower()}** rate of ₹{lease_per_acre:,}/acre.")
    

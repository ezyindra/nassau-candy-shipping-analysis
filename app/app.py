
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Nassau Candy | Shipping Analytics",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Nassau Candy")
st.subheader("Factory-to-Customer Shipping Route Efficiency")
st.caption("Shipping analytics • Factory performance • Route intelligence")

# ---------------- LOAD DATA ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "Nassau Candy Distributor.csv"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    for column in ["Order Date", "Ship Date"]:
        data[column] = pd.to_datetime(
            data[column], format="mixed", dayfirst=True, errors="coerce"
        )

    numeric_columns = ["Sales", "Units", "Gross Profit", "Cost"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    factory_mapping = {
        "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
        "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
        "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
        "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
        "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
        "Laffy Taffy": "Sugar Shack",
        "SweeTARTS": "Sugar Shack",
        "Nerds": "Sugar Shack",
        "Fun Dip": "Sugar Shack",
        "Fizzy Lifting Drinks": "Sugar Shack",
        "Everlasting Gobstopper": "Secret Factory",
        "Lickable Wallpaper": "Secret Factory",
        "Wonka Gum": "Secret Factory",
        "Hair Toffee": "The Other Factory",
        "Kazookles": "The Other Factory",
    }

    data["Factory"] = data["Product Name"].map(factory_mapping)
    data["Lead Time (Days)"] = (
        data["Ship Date"] - data["Order Date"]
    ).dt.days

    data["Route"] = (
        data["Factory"].fillna("Unknown Factory")
        + " → "
        + data["State/Province"].fillna("Unknown State").astype(str)
    )

    return data


try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.info(f"Expected CSV location: {DATA_PATH}")
    st.stop()

if df.empty:
    st.error("The dataset is empty.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Dashboard Filters")

regions = sorted(df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Region", regions, default=regions
)

ship_modes = sorted(df["Ship Mode"].dropna().unique())
selected_modes = st.sidebar.multiselect(
    "Shipping mode", ship_modes, default=ship_modes
)

factories = sorted(df["Factory"].dropna().unique())
selected_factories = st.sidebar.multiselect(
    "Factory", factories, default=factories
)

filtered = df[
    df["Region"].isin(selected_regions)
    & df["Ship Mode"].isin(selected_modes)
    & df["Factory"].isin(selected_factories)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Change your selections.")
    st.stop()

# ---------------- DATA QUALITY WARNING ----------------
st.subheader("Data Quality")

valid_lead = filtered["Lead Time (Days)"].dropna()
long_shipments = int((valid_lead > 30).sum())
median_lead = valid_lead.median() if not valid_lead.empty else float("nan")

st.warning(
    "Important: the supplied dates produce unusually long shipping lead times. "
    "The original dates are preserved; no dates have been silently corrected. "
    "Treat lead-time and delay metrics as provisional until the source dates "
    "are verified."
)

quality1, quality2, quality3 = st.columns(3)
quality1.metric("Records over 30 days", f"{long_shipments:,}")
quality2.metric("Median lead time", f"{median_lead:,.0f} days" if pd.notna(median_lead) else "N/A")
quality3.metric("Missing factory mappings", f"{filtered['Factory'].isna().sum():,}")

# ---------------- KPI CARDS ----------------
st.divider()
st.subheader("Shipping Overview")

total_sales = filtered["Sales"].sum()
total_profit = filtered["Gross Profit"].sum()
total_units = filtered["Units"].sum()
shipment_records = len(filtered)
unique_orders = filtered["Order ID"].nunique()
avg_lead = valid_lead.mean() if not valid_lead.empty else float("nan")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sales", f"${total_sales:,.0f}")
k2.metric("Gross Profit", f"${total_profit:,.0f}")
k3.metric("Units", f"{total_units:,.0f}")
k4.metric("Unique Orders", f"{unique_orders:,}")
k5.metric("Avg. Lead Time", f"{avg_lead:,.0f} days" if pd.notna(avg_lead) else "N/A")

# ---------------- FACTORY PERFORMANCE ----------------
st.divider()
st.subheader("Factory Performance")

factory_summary = (
    filtered.groupby("Factory", dropna=False)
    .agg(
        Shipment_Records=("Order ID", "size"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
    )
    .reset_index()
)

factory_summary["Gross Margin (%)"] = (
    factory_summary["Gross_Profit"]
    / factory_summary["Sales"].replace(0, float("nan"))
    * 100
).round(2)

left, right = st.columns(2)

with left:
    fig_factory = px.bar(
        factory_summary.sort_values("Sales", ascending=True),
        x="Sales",
        y="Factory",
        orientation="h",
        title="Sales by Factory",
        text_auto=".2s",
    )
    fig_factory.update_layout(yaxis_title="", xaxis_title="Sales ($)")
    st.plotly_chart(fig_factory, use_container_width=True)

with right:
    fig_margin = px.bar(
        factory_summary.sort_values("Gross Margin (%)", ascending=True),
        x="Gross Margin (%)",
        y="Factory",
        orientation="h",
        title="Gross Margin by Factory",
        text_auto=".1f",
    )
    fig_margin.update_layout(yaxis_title="", xaxis_title="Gross margin (%)")
    st.plotly_chart(fig_margin, use_container_width=True)

st.dataframe(
    factory_summary.sort_values("Sales", ascending=False),
    use_container_width=True,
    hide_index=True,
)

# ---------------- SHIP MODE COMPARISON ----------------
st.divider()
st.subheader("Shipping Mode Comparison")

ship_summary = (
    filtered.groupby("Ship Mode")
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Lead_Time=("Lead Time (Days)", "mean"),
    )
    .reset_index()
)

ship_summary["Average_Lead_Time"] = ship_summary["Average_Lead_Time"].round(2)

c1, c2 = st.columns(2)

with c1:
    fig_modes = px.bar(
        ship_summary,
        x="Ship Mode",
        y="Shipment_Records",
        color="Ship Mode",
        title="Shipment Records by Shipping Mode",
        text_auto=True,
    )
    st.plotly_chart(fig_modes, use_container_width=True)

with c2:
    fig_mode_sales = px.bar(
        ship_summary,
        x="Ship Mode",
        y="Sales",
        color="Ship Mode",
        title="Sales by Shipping Mode",
        text_auto=".2s",
    )
    st.plotly_chart(fig_mode_sales, use_container_width=True)

st.dataframe(ship_summary, use_container_width=True, hide_index=True)

# ---------------- GEOGRAPHIC SHIPPING MAP ----------------
st.divider()
st.subheader("Geographic Shipping Demand")

country = st.selectbox(
    "Choose country",
    sorted(filtered["Country/Region"].dropna().unique()),
)

country_df = filtered[filtered["Country/Region"] == country].copy()

state_summary = (
    country_df.groupby("State/Province")
    .agg(
        Shipments=("Order ID", "size"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
    )
    .reset_index()
)

if country == "United States":
    fig_map = px.choropleth(
        state_summary,
        locations="State/Province",
        locationmode="USA-states",
        color="Shipments",
        scope="usa",
        hover_data=["Units", "Sales"],
        color_continuous_scale="Blues",
        title="US Shipping Demand by State",
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info(
        "The current map is configured for US states. "
        "Canadian province-level mapping can be added as a separate view."
    )

# ---------------- ROUTE ANALYSIS ----------------
st.divider()
st.subheader("Route Efficiency Analysis")

route_summary = (
    filtered.groupby("Route")
    .agg(
        Route_Volume=("Order ID", "size"),
        Average_Lead_Time=("Lead Time (Days)", "mean"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
    )
    .reset_index()
)

route_summary["Average_Lead_Time"] = route_summary["Average_Lead_Time"].round(2)

route_summary["Delayed_Shipments"] = (
    filtered.assign(
        Provisional_Delay=filtered["Lead Time (Days)"] > 30
    )
    .groupby("Route")["Provisional_Delay"]
    .sum()
    .reindex(route_summary["Route"])
    .fillna(0)
    .to_numpy()
)

route_summary["Delay_Frequency (%)"] = (
    route_summary["Delayed_Shipments"]
    / route_summary["Route_Volume"].replace(0, float("nan"))
    * 100
).round(2)

st.caption(
    "Delay frequency currently uses a provisional 30-day threshold because "
    "the dataset does not provide a promised delivery date. This is not a "
    "verified carrier-delay measurement."
)

min_volume = st.slider(
    "Minimum route shipment records",
    min_value=1,
    max_value=max(1, int(route_summary["Route_Volume"].max())),
    value=1,
)

route_view = route_summary[
    route_summary["Route_Volume"] >= min_volume
].sort_values("Route_Volume", ascending=False)

st.dataframe(route_view, use_container_width=True, hide_index=True)

route_options = sorted(filtered["Route"].dropna().unique())
selected_route = st.selectbox("Inspect a route", route_options)

detail = filtered[filtered["Route"] == selected_route]
st.markdown(f"**Selected route:** {selected_route}")

d1, d2, d3 = st.columns(3)
d1.metric("Shipment records", f"{len(detail):,}")
d2.metric("Sales", f"${detail['Sales'].sum():,.2f}")
d3.metric("Gross profit", f"${detail['Gross Profit'].sum():,.2f}")

st.dataframe(
    detail[
        [
            "Order ID",
            "Order Date",
            "Ship Date",
            "Ship Mode",
            "Product Name",
            "Units",
            "Sales",
            "Lead Time (Days)",
        ]
    ].sort_values("Order Date"),
    use_container_width=True,
    hide_index=True,
)

# ---------------- DOWNLOADS ----------------
st.divider()
st.subheader("Export Results")

csv_data = route_view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download route analysis (CSV)",
    data=csv_data,
    file_name="nassau_route_analysis.csv",
    mime="text/csv",
)

st.download_button(
    "Download filtered records (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="nassau_filtered_shipments.csv",
    mime="text/csv",
)

st.caption(
    "Nassau Candy Distributor | Internship analytics project. "
    "Results describe the supplied dataset and should not be interpreted "
    "as verified real-world delivery performance until date anomalies are resolved."
)

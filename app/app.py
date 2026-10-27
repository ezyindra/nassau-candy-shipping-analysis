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

st.title("📦 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Analysis")
st.caption("Shipping analytics • Factory performance • Route intelligence")


# ---------------- PATHS AND CONFIG ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "Nassau Candy Distributor.csv"

REQUIRED_COLUMNS = [
    "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
    "Country/Region", "State/Province", "Region", "Product ID",
    "Product Name", "Sales", "Units", "Gross Profit", "Cost",
]

# Exact product names from the supplied CSV are used here.
FACTORY_MAPPING = {
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

# Plotly's USA-states mode expects postal abbreviations, not full state names.
US_STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    data = pd.read_csv(csv_path)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(
            "The CSV is missing required columns: " + ", ".join(missing_columns)
        )

    # Parse mixed date formats without changing the original CSV.
    for column in ["Order Date", "Ship Date"]:
        data[column] = pd.to_datetime(
            data[column].astype("string").str.strip(),
            format="mixed",
            dayfirst=True,
            errors="coerce",
        )

    for column in ["Sales", "Units", "Gross Profit", "Cost"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Trim accidental spaces while preserving the actual product wording.
    data["Product Name"] = data["Product Name"].astype("string").str.strip()
    data["Factory"] = data["Product Name"].map(FACTORY_MAPPING)

    data["Lead Time (Days)"] = (
        data["Ship Date"] - data["Order Date"]
    ).dt.days

    data["Route"] = (
        data["Factory"].fillna("Unknown Factory").astype(str)
        + " → "
        + data["State/Province"].fillna("Unknown State").astype(str)
    )

    return data


if not DATA_PATH.exists():
    st.error("Dataset file not found.")
    st.write("Expected location:", str(DATA_PATH))
    st.info(
        "Keep `Nassau Candy Distributor.csv` inside the project's `data` folder. "
        "The `data` folder should sit beside the `app` folder."
    )
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load or validate the dataset: {exc}")
    st.stop()

if df.empty:
    st.error("The dataset contains no records.")
    st.stop()


# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Dashboard Filters")

region_values = sorted(df["Region"].dropna().astype(str).unique().tolist())
mode_values = sorted(df["Ship Mode"].dropna().astype(str).unique().tolist())
factory_values = sorted(df["Factory"].dropna().astype(str).unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Region", region_values, default=region_values
)
selected_modes = st.sidebar.multiselect(
    "Shipping mode", mode_values, default=mode_values
)
selected_factories = st.sidebar.multiselect(
    "Factory", factory_values, default=factory_values
)

filtered = df[
    df["Region"].astype("string").isin(selected_regions)
    & df["Ship Mode"].astype("string").isin(selected_modes)
    & df["Factory"].astype("string").isin(selected_factories)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Change your selections in the sidebar.")
    st.stop()


# ---------------- DATA QUALITY ----------------
st.divider()
st.subheader("⚠️ Data Quality Check")

valid_lead = filtered["Lead Time (Days)"].dropna()
long_shipments = int((valid_lead > 30).sum())
missing_dates = int(filtered[["Order Date", "Ship Date"]].isna().any(axis=1).sum())
negative_lead = int((valid_lead < 0).sum())
missing_factory = int(filtered["Factory"].isna().sum())
median_lead = valid_lead.median() if not valid_lead.empty else float("nan")

st.warning(
    "The source dates show an unusual gap: shipment dates are several years after "
    "order dates. The original dates are preserved and have not been silently changed. "
    "Lead-time and delay results are therefore provisional and should not be presented "
    "as verified carrier performance until the source dates are confirmed."
)

q1, q2, q3, q4 = st.columns(4)
q1.metric("Records with lead time > 30 days", f"{long_shipments:,}")
q2.metric(
    "Median lead time",
    f"{median_lead:,.0f} days" if pd.notna(median_lead) else "N/A",
)
q3.metric("Records with missing dates", f"{missing_dates:,}")
q4.metric("Missing factory mappings", f"{missing_factory:,}")

if negative_lead:
    st.error(f"{negative_lead:,} record(s) have a negative lead time; review the source dates.")


# ---------------- SHIPPING OVERVIEW ----------------
st.divider()
st.subheader("📊 Shipping Overview")

total_sales = filtered["Sales"].sum()
total_profit = filtered["Gross Profit"].sum()
total_units = filtered["Units"].sum()
record_count = len(filtered)
unique_orders = filtered["Order ID"].nunique()
avg_lead = valid_lead.mean() if not valid_lead.empty else float("nan")
gross_margin = (total_profit / total_sales * 100) if total_sales else float("nan")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Sales", f"${total_sales:,.2f}")
k2.metric("Gross Profit", f"${total_profit:,.2f}")
k3.metric("Gross Margin", f"{gross_margin:.2f}%" if pd.notna(gross_margin) else "N/A")
k4.metric("Units", f"{total_units:,.0f}")
k5.metric("Shipment Records", f"{record_count:,}")
k6.metric("Unique Orders", f"{unique_orders:,}")

st.caption(
    f"Average calculated lead time: {avg_lead:,.1f} days."
    if pd.notna(avg_lead)
    else "Average calculated lead time is unavailable."
)


# ---------------- FACTORY PERFORMANCE ----------------
st.divider()
st.subheader("🏭 Factory Performance")

factory_summary = (
    filtered.groupby("Factory", dropna=False)
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
        Average_Lead_Time=("Lead Time (Days)", "mean"),
    )
    .reset_index()
)

factory_summary["Gross Margin (%)"] = (
    factory_summary["Gross_Profit"]
    / factory_summary["Sales"].replace(0, float("nan"))
    * 100
).round(2)
factory_summary["Average_Lead_Time"] = factory_summary["Average_Lead_Time"].round(2)

left, right = st.columns(2)
with left:
    fig_factory_sales = px.bar(
        factory_summary.sort_values("Sales", ascending=True),
        x="Sales",
        y="Factory",
        orientation="h",
        title="Sales by Factory",
        text_auto=".2s",
    )
    fig_factory_sales.update_layout(yaxis_title="", xaxis_title="Sales ($)")
    st.plotly_chart(fig_factory_sales, use_container_width=True)

with right:
    fig_factory_margin = px.bar(
        factory_summary.sort_values("Gross Margin (%)", ascending=True),
        x="Gross Margin (%)",
        y="Factory",
        orientation="h",
        title="Gross Margin by Factory",
        text_auto=".1f",
    )
    fig_factory_margin.update_layout(yaxis_title="", xaxis_title="Gross margin (%)")
    st.plotly_chart(fig_factory_margin, use_container_width=True)

st.dataframe(
    factory_summary.sort_values("Sales", ascending=False),
    use_container_width=True,
    hide_index=True,
)


# ---------------- SHIP MODE COMPARISON ----------------
st.divider()
st.subheader("🚚 Shipping Mode Comparison")

ship_summary = (
    filtered.groupby("Ship Mode", dropna=False)
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
ship_summary["Gross Margin (%)"] = (
    ship_summary["Gross_Profit"]
    / ship_summary["Sales"].replace(0, float("nan"))
    * 100
).round(2)

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
st.subheader("🗺️ Geographic Shipping Demand")

countries = sorted(filtered["Country/Region"].dropna().astype(str).unique().tolist())
if countries:
    selected_country = st.selectbox("Choose country", countries)
    country_df = filtered[
        filtered["Country/Region"].astype("string") == selected_country
    ].copy()

    state_summary = (
        country_df.groupby("State/Province", dropna=False)
        .agg(
            Shipments=("Order ID", "size"),
            Units=("Units", "sum"),
            Sales=("Sales", "sum"),
        )
        .reset_index()
    )

    if selected_country == "United States":
        state_summary["State_Code"] = (
            state_summary["State/Province"].astype(str).str.strip()
            .map(US_STATE_ABBR)
        )
        # If the source already uses two-letter state codes, keep them.
        already_abbreviated = state_summary["State/Province"].astype(str).str.fullmatch(r"[A-Z]{2}")
        state_summary.loc[already_abbreviated, "State_Code"] = state_summary.loc[
            already_abbreviated, "State/Province"
        ]

        map_data = state_summary.dropna(subset=["State_Code"]).copy()
        if map_data.empty:
            st.info(
                "No recognizable US state names/codes were found for the map. "
                "The state-level data table is shown below."
            )
        else:
            fig_map = px.choropleth(
                map_data,
                locations="State_Code",
                locationmode="USA-states",
                color="Shipments",
                scope="usa",
                hover_name="State/Province",
                hover_data={"Units": True, "Sales": ":$,.2f", "State_Code": False},
                color_continuous_scale="Blues",
                title="US Shipping Demand by State",
            )
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info(
            "The map currently visualizes US states. Province-level Canadian mapping "
            "is not included; the province summary remains available below."
        )

    st.dataframe(
        state_summary.sort_values("Shipments", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No country values are available after filtering.")


# ---------------- ROUTE ANALYSIS ----------------
st.divider()
st.subheader("🧭 Route Efficiency Analysis")

route_summary = (
    filtered.groupby("Route", dropna=False)
    .agg(
        Route_Volume=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Average_Lead_Time=("Lead Time (Days)", "mean"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
    )
    .reset_index()
)

# A >30-day flag is only a provisional indicator, not verified carrier delay.
delay_by_route = (
    filtered.assign(Provisional_Delay=filtered["Lead Time (Days)"] > 30)
    .groupby("Route")["Provisional_Delay"]
    .sum()
)
route_summary["Delayed_Shipments"] = (
    route_summary["Route"].map(delay_by_route).fillna(0).astype(int)
)
route_summary["Delay_Frequency (%)"] = (
    route_summary["Delayed_Shipments"]
    / route_summary["Route_Volume"].replace(0, float("nan"))
    * 100
).round(2)
route_summary["Average_Lead_Time"] = route_summary["Average_Lead_Time"].round(2)

st.caption(
    "Provisional delay frequency uses a 30-day lead-time threshold because the dataset "
    "does not contain a promised delivery date. It is not a verified carrier-delay rate."
)

max_volume = max(1, int(route_summary["Route_Volume"].max()))
min_volume = st.slider(
    "Minimum route shipment records",
    min_value=1,
    max_value=max_volume,
    value=1,
)
route_view = route_summary[
    route_summary["Route_Volume"] >= min_volume
].sort_values("Route_Volume", ascending=False)

st.dataframe(route_view, use_container_width=True, hide_index=True)

route_options = sorted(filtered["Route"].dropna().astype(str).unique().tolist())
if route_options:
    selected_route = st.selectbox("Inspect a route", route_options)
    detail = filtered[filtered["Route"].astype(str) == selected_route].copy()

    st.markdown(f"**Selected route:** {selected_route}")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Shipment records", f"{len(detail):,}")
    d2.metric("Unique orders", f"{detail['Order ID'].nunique():,}")
    d3.metric("Sales", f"${detail['Sales'].sum():,.2f}")
    d4.metric("Gross profit", f"${detail['Gross Profit'].sum():,.2f}")

    detail_columns = [
        "Order ID", "Order Date", "Ship Date", "Ship Mode",
        "Product Name", "Units", "Sales", "Lead Time (Days)",
    ]
    st.dataframe(
        detail[detail_columns].sort_values("Order Date", na_position="last"),
        use_container_width=True,
        hide_index=True,
    )


# ---------------- EXPORTS ----------------
st.divider()
st.subheader("⬇️ Export Results")

st.download_button(
    "Download route analysis (CSV)",
    data=route_view.to_csv(index=False).encode("utf-8"),
    file_name="nassau_route_analysis.csv",
    mime="text/csv",
)

st.download_button(
    "Download filtered records (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="nassau_filtered_shipments.csv",
    mime="text/csv",
)

st.download_button(
    "Download factory summary (CSV)",
    data=factory_summary.to_csv(index=False).encode("utf-8"),
    file_name="nassau_factory_summary.csv",
    mime="text/csv",
)

st.caption(
    "Nassau Candy Distributor | Unified Mentor internship project. "
    "Results describe the supplied dataset. Shipping lead-time conclusions are "
    "provisional until the source date anomaly is resolved."
)

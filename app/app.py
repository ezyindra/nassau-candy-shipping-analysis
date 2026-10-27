
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy | Shipping Analysis",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.07);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 14px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "Nassau Candy Distributor.csv"

FACTORY_MAPPING = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Scrumdiddlyumptious": "Lot's O' Nuts",
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

US_STATE_CODES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ",
    "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC",
}


# ---------------------------------------------------------
# Data loading and preparation
# ---------------------------------------------------------
@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    data = pd.read_csv(csv_path)

    required_columns = [
        "Order ID", "Order Date", "Ship Date", "Ship Mode",
        "Country/Region", "State/Province", "Region",
        "Product ID", "Product Name", "Sales", "Units",
        "Gross Profit", "Cost",
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "The CSV is missing required columns: "
            + ", ".join(missing)
        )

    # The source contains mixed date formats.
    for column in ("Order Date", "Ship Date"):
        data[column] = pd.to_datetime(
            data[column].astype(str).str.strip(),
            format="mixed",
            dayfirst=True,
            errors="coerce",
        )

    for column in ("Sales", "Units", "Gross Profit", "Cost"):
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        )

    data["Factory"] = (
        data["Product Name"].map(FACTORY_MAPPING)
        .fillna("Unmapped")
    )

    data["Lead Time Days"] = (
        data["Ship Date"] - data["Order Date"]
    ).dt.days

    data["State_Code"] = data["State/Province"].map(
        US_STATE_CODES
    )

    return data


st.title("Nassau Candy")
st.subheader("Factory-to-customer shipping analysis")
st.caption(
    "An exploratory look at shipment volume, sales, shipping modes "
    "and factory-to-state routes."
)

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Place 'Nassau Candy Distributor.csv' inside the project's "
        "'data' folder."
    )
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("The dataset contains no records.")
    st.stop()


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Analysis filters")

countries = sorted(
    df["Country/Region"].dropna().unique().tolist()
)
selected_countries = st.sidebar.multiselect(
    "Country",
    countries,
    default=countries,
)

regions = sorted(
    df["Region"].dropna().unique().tolist()
)
selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions,
)

ship_modes = sorted(
    df["Ship Mode"].dropna().unique().tolist()
)
selected_modes = st.sidebar.multiselect(
    "Shipping mode",
    ship_modes,
    default=ship_modes,
)

factories = sorted(
    df["Factory"].dropna().unique().tolist()
)
selected_factories = st.sidebar.multiselect(
    "Factory",
    factories,
    default=factories,
)

filtered = df[
    df["Country/Region"].isin(selected_countries)
    & df["Region"].isin(selected_regions)
    & df["Ship Mode"].isin(selected_modes)
    & df["Factory"].isin(selected_factories)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Change your selections.")
    st.stop()


# ---------------------------------------------------------
# Overview KPIs
# ---------------------------------------------------------
st.divider()
st.header("Shipping overview")

total_sales = filtered["Sales"].sum()
total_units = filtered["Units"].sum()
total_profit = filtered["Gross Profit"].sum()
shipment_records = len(filtered)
unique_orders = filtered["Order ID"].nunique()

valid_lead_times = filtered["Lead Time Days"].dropna()
average_lead_time = (
    valid_lead_times.mean()
    if not valid_lead_times.empty else None
)

gross_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Sales", f"${total_sales:,.2f}")
k2.metric("Shipment records", f"{shipment_records:,}")
k3.metric("Unique orders", f"{unique_orders:,}")
k4.metric("Units shipped", f"{total_units:,.0f}")
k5.metric("Gross profit", f"${total_profit:,.2f}")

k6, k7 = st.columns(2)
k6.metric("Gross margin", f"{gross_margin:.1f}%")
k7.metric(
    "Average recorded lead time",
    (
        f"{average_lead_time:,.1f} days"
        if average_lead_time is not None
        else "Unavailable"
    ),
)

st.caption(
    "Shipment records count dataset rows. Unique orders count distinct "
    "Order IDs; an order can contain multiple records."
)


# ---------------------------------------------------------
# Data quality notes
# ---------------------------------------------------------
st.header("Data quality")

invalid_dates = int(
    (filtered["Order Date"].isna()
     | filtered["Ship Date"].isna()).sum()
)

negative_lead_times = int(
    (filtered["Lead Time Days"] < 0).sum()
)

long_lead_times = int(
    (filtered["Lead Time Days"] > 30).sum()
)

q1, q2, q3 = st.columns(3)
q1.metric("Rows with missing/invalid dates", f"{invalid_dates:,}")
q2.metric("Negative lead times", f"{negative_lead_times:,}")
q3.metric("Lead times over 30 days", f"{long_lead_times:,}")

if not valid_lead_times.empty and valid_lead_times.median() > 30:
    st.warning(
        "The recorded shipping lead times are unusually long. "
        "Check the source dates before using lead time to judge "
        "real-world delivery performance. The original dates have "
        "not been automatically corrected."
    )

with st.expander("About the lead-time calculation"):
    st.write(
        "Lead time is calculated as Ship Date minus Order Date. "
        "Invalid dates are excluded from lead-time statistics. "
        "The analysis preserves the source values rather than "
        "guessing replacement dates."
    )


# ---------------------------------------------------------
# Geographic shipping demand
# ---------------------------------------------------------
st.divider()
st.header("Geographic shipping demand")

available_countries = sorted(
    filtered["Country/Region"].dropna().unique().tolist()
)

if available_countries:
    map_country = st.selectbox(
        "Choose a country",
        available_countries,
        key="map_country",
    )

    geo_data = filtered[
        filtered["Country/Region"] == map_country
    ].copy()

    state_summary = (
        geo_data.groupby("State/Province", dropna=False)
        .agg(
            Shipments=("Order ID", "size"),
            Units=("Units", "sum"),
            Sales=("Sales", "sum"),
        )
        .reset_index()
        .sort_values("Shipments", ascending=False)
    )

    if map_country == "United States":
        state_summary["State_Code"] = (
            state_summary["State/Province"].map(US_STATE_CODES)
        )
        map_data = state_summary.dropna(
            subset=["State_Code"]
        ).copy()

        if not map_data.empty:
            fig_map = px.choropleth(
                map_data,
                locations="State_Code",
                locationmode="USA-states",
                color="Shipments",
                scope="usa",
                color_continuous_scale="Blues",
                hover_name="State/Province",
                hover_data={
                    "Shipments": ":,",
                    "Units": ":,",
                    "Sales": ":$,.2f",
                    "State_Code": False,
                },
                title="US shipping demand by state",
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(
                fig_map, use_container_width=True
            )
        else:
            st.info(
                "No recognized US state names are available "
                "for the map with the current filters."
            )
    else:
        st.info(
            "The map currently visualizes US states. "
            "Canadian province-level mapping is not included; "
            "the province summary is available below."
        )

    st.subheader(f"{map_country}: state/province summary")
    st.dataframe(
        state_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download geographic summary",
        data=state_summary.to_csv(index=False).encode("utf-8"),
        file_name="geographic_shipping_summary.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------
# Shipping mode comparison
# ---------------------------------------------------------
st.divider()
st.header("Shipping mode comparison")

mode_summary = (
    filtered.groupby("Ship Mode")
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Lead_Time=("Lead Time Days", "mean"),
    )
    .reset_index()
    .sort_values("Shipment_Records", ascending=False)
)

left, right = st.columns(2)

with left:
    fig_modes = px.bar(
        mode_summary,
        x="Ship Mode",
        y="Shipment_Records",
        color="Ship Mode",
        title="Shipment records by shipping mode",
        labels={
            "Ship Mode": "Shipping mode",
            "Shipment_Records": "Shipment records",
        },
    )
    fig_modes.update_layout(showlegend=False)
    st.plotly_chart(
        fig_modes, use_container_width=True
    )

with right:
    fig_mode_sales = px.bar(
        mode_summary,
        x="Ship Mode",
        y="Sales",
        color="Ship Mode",
        title="Sales by shipping mode",
        labels={"Sales": "Sales ($)"},
    )
    fig_mode_sales.update_layout(showlegend=False)
    st.plotly_chart(
        fig_mode_sales, use_container_width=True
    )

st.dataframe(
    mode_summary.round(2),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download shipping-mode summary",
    data=mode_summary.to_csv(index=False).encode("utf-8"),
    file_name="shipping_mode_summary.csv",
    mime="text/csv",
)


# ---------------------------------------------------------
# Factory performance
# ---------------------------------------------------------
st.divider()
st.header("Factory performance")

factory_summary = (
    filtered.groupby("Factory")
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
    )
    .reset_index()
    .sort_values("Sales", ascending=False)
)

factory_summary["Gross_Margin_Percent"] = (
    factory_summary["Gross_Profit"]
    .div(factory_summary["Sales"].replace(0, pd.NA))
    .mul(100)
)

left, right = st.columns(2)

with left:
    fig_factory_sales = px.bar(
        factory_summary,
        x="Factory",
        y="Sales",
        color="Factory",
        title="Sales by factory",
        labels={"Sales": "Sales ($)"},
    )
    fig_factory_sales.update_layout(showlegend=False)
    st.plotly_chart(
        fig_factory_sales, use_container_width=True
    )

with right:
    fig_factory_units = px.bar(
        factory_summary,
        x="Factory",
        y="Units",
        color="Factory",
        title="Units by factory",
    )
    fig_factory_units.update_layout(showlegend=False)
    st.plotly_chart(
        fig_factory_units, use_container_width=True
    )

st.dataframe(
    factory_summary.round(2),
    use_container_width=True,
    hide_index=True,
)

if (filtered["Factory"] == "Unmapped").any():
    st.warning(
        "Some product names do not have a factory mapping. "
        "Review the mapping before drawing factory-level conclusions."
    )


# ---------------------------------------------------------
# Factory-to-customer route analysis
# ---------------------------------------------------------
st.divider()
st.header("Factory-to-customer route analysis")

route_summary = (
    filtered.groupby(
        ["Factory", "State/Province"], dropna=False
    )
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Lead_Time=("Lead Time Days", "mean"),
    )
    .reset_index()
    .sort_values("Shipment_Records", ascending=False)
)

route_summary["Average_Lead_Time"] = (
    route_summary["Average_Lead_Time"].round(2)
)

st.caption(
    "Routes are grouped by the product's mapped factory and the "
    "customer's recorded state or province. The dataset does not "
    "provide factory coordinates or actual transport paths."
)

route_search = st.text_input(
    "Search factory or state/province",
    placeholder="For example: Sugar Shack or California",
)

if route_search.strip():
    search_mask = (
        route_summary["Factory"].astype(str).str.contains(
            route_search, case=False, na=False
        )
        | route_summary["State/Province"].astype(str).str.contains(
            route_search, case=False, na=False
        )
    )
    displayed_routes = route_summary[search_mask]
else:
    displayed_routes = route_summary

st.dataframe(
    displayed_routes,
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download route analysis",
    data=route_summary.to_csv(index=False).encode("utf-8"),
    file_name="factory_customer_route_analysis.csv",
    mime="text/csv",
)


# ---------------------------------------------------------
# Product drill-down
# ---------------------------------------------------------
st.divider()
st.header("Product drill-down")

product_summary = (
    filtered.groupby(
        ["Product ID", "Product Name", "Factory"],
        dropna=False,
    )
    .agg(
        Shipment_Records=("Order ID", "size"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
    )
    .reset_index()
    .sort_values("Sales", ascending=False)
)

product_options = product_summary["Product Name"].dropna().tolist()

if product_options:
    selected_product = st.selectbox(
        "Choose a product",
        product_options,
    )

    product_details = filtered[
        filtered["Product Name"] == selected_product
    ]

    p1, p2, p3 = st.columns(3)
    p1.metric(
        "Product sales",
        f"${product_details['Sales'].sum():,.2f}",
    )
    p2.metric(
        "Units",
        f"{product_details['Units'].sum():,.0f}",
    )
    p3.metric(
        "Gross profit",
        f"${product_details['Gross Profit'].sum():,.2f}",
    )

    product_routes = (
        product_details.groupby(
            ["Factory", "State/Province"], dropna=False
        )
        .agg(
            Shipment_Records=("Order ID", "size"),
            Units=("Units", "sum"),
            Sales=("Sales", "sum"),
        )
        .reset_index()
        .sort_values("Shipment_Records", ascending=False)
    )

    st.write("Recorded destinations for this product")
    st.dataframe(
        product_routes,
        use_container_width=True,
        hide_index=True,
    )

st.subheader("All products")
st.dataframe(
    product_summary.round(2),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download product summary",
    data=product_summary.to_csv(index=False).encode("utf-8"),
    file_name="product_summary.csv",
    mime="text/csv",
)


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.divider()
st.caption(
    "Nassau Candy Distributor | Exploratory shipping analysis. "
    "Results describe the supplied dataset and should be validated "
    "before operational decisions are made."
)

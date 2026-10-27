## Live Dashboard

**Streamlit App:** [Open the Nassau Candy Shipping Analysis Dashboard](https://qrj6tagzjn243yhzrq6ljy.streamlit.app/)

The dashboard provides interactive filters, shipment KPIs, geographic shipping summaries, shipping-mode comparisons, factory and product analysis, and downloadable summary data.

## Running Locally

From the repository root:

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

The application reads the dataset from `data/Nassau Candy Distributor.csv`.

**Data note:** The recorded order and ship dates produce unusually long lead times. These values are retained as supplied, and the findings should not be interpreted as verified real-world delivery performance without validating the source dates.

# Factory-to-Customer Shipping Route Efficiency Analysis

## Nassau Candy Distributor

### Unified Mentor - Machine Learning Internship Project

---

## 📌 Project Overview

This project focuses on analyzing the efficiency of factory-to-customer
shipping routes for Nassau Candy Distributor.

The objective is to analyze shipment data, identify inefficient shipping
routes and geographic bottlenecks, compare different shipping modes, and
provide useful business insights through an interactive Streamlit dashboard.

The project uses Python-based data analysis and visualization techniques
to evaluate shipping performance and support data-driven decision making.

---

## 🎯 Objectives

The main objectives of this project are:

- Clean and validate the shipment dataset.
- Analyze order and shipment dates.
- Calculate shipping lead time.
- Map products to their respective factories.
- Analyze factory-to-customer shipping routes.
- Identify efficient and inefficient routes.
- Analyze regional and state-level shipping performance.
- Identify geographic shipping bottlenecks.
- Compare different shipping modes.
- Develop an interactive Streamlit dashboard.
- Provide actionable business insights and recommendations.

---

## 📊 Dataset

### Dataset Name

Nassau Candy Distributor Dataset

### Dataset Size

- Records: 10,194
- Columns: 18

### Main Features

| Feature | Description |
|---|---|
| Row ID | Unique row identifier |
| Order ID | Unique order identifier |
| Order Date | Date on which the order was placed |
| Ship Date | Date on which the order was shipped |
| Ship Mode | Shipping method used |
| Customer ID | Customer identifier |
| Country/Region | Customer country or region |
| City | Customer city |
| State/Province | Customer state or province |
| Postal Code | Customer postal code |
| Division | Product division |
| Region | Customer region |
| Product ID | Unique product identifier |
| Product Name | Product name |
| Sales | Total sales value |
| Units | Number of units ordered |
| Gross Profit | Gross profit generated |
| Cost | Product manufacturing cost |

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Scikit-learn
- Streamlit
- Jupyter Notebook

---

## 🔍 Project Workflow

The project follows the workflow below:

### 1. Data Collection

Load the Nassau Candy Distributor dataset and inspect its structure.

### 2. Data Cleaning and Validation

- Check missing values.
- Check duplicate records.
- Validate date formats.
- Validate shipping dates.
- Identify invalid lead times.
- Standardize geographic fields.
- Validate numerical fields.

### 3. Feature Engineering

New analytical features will be created, including:

- Shipping Lead Time
- Factory
- Factory-to-Region Route
- Factory-to-State Route
- Delay Flag
- Data Quality Flag

### 4. Exploratory Data Analysis

Analyze:

- Shipment volume
- Regions
- States
- Product divisions
- Products
- Shipping modes
- Sales
- Units
- Gross profit
- Shipping lead time

### 5. Route Efficiency Analysis

Calculate route-level KPIs such as:

- Route volume
- Average lead time
- Median lead time
- Lead-time variability
- Delay frequency
- Route efficiency score

### 6. Geographic Bottleneck Analysis

Identify:

- High-delay regions
- High-delay states
- High-volume states
- Poor-performing routes
- Geographic bottlenecks

### 7. Ship Mode Analysis

Compare:

- Standard Class
- Second Class
- First Class
- Same Day

using shipping performance metrics.

### 8. Interactive Dashboard

A Streamlit dashboard will be developed to provide:

- Route efficiency overview
- Route performance leaderboard
- Geographic shipping map
- Regional bottleneck visualization
- Ship-mode comparison
- Route drill-down
- State-level analysis
- Order-level shipment analysis

---

## 📈 Key Performance Indicators

The main KPIs used in the analysis include:

### Average Lead Time

Average number of days between order date and ship date.

### Route Volume

Number of shipments handled by a particular route.

### Delay Frequency

Percentage of shipments exceeding the defined lead-time threshold.

### Route Efficiency Score

A normalized score used to compare shipping performance between routes.

---

## 🏭 Factory Mapping

Products will be mapped to their respective manufacturing factories based
on the project specifications.

The factory mapping will be used to construct factory-to-customer routes
and evaluate route efficiency.

---

## 📂 Project Structure

```text
Nassau_Candy_Shipping_Analysis/
│
├── data/
│   └── Nassau Candy Distributor.csv
│
├── notebook/
│   └── 01_EDA_and_Data_Cleaning.ipynb
│
├── outputs/
│   ├── cleaned_nassau_candy.csv
│   ├── route_analysis.csv
│   ├── state_analysis.csv
│   └── ship_mode_analysis.csv
│
├── app/
│   └── app.py
│
├── reports/
│   ├── research_report.docx
│   └── executive_summary.docx
│
├── README.md
└── requirements.txt

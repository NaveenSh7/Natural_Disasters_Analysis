import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --------------------
#  Load Data from SQLite
# --------------------
conn = sqlite3.connect("database/disasters.db") 
df = pd.read_sql("SELECT * FROM disasters", conn)
conn.close()

# Convert dates
df["Start_Date"] = pd.to_datetime(df["Start_Date"])
df["End_Date"] = pd.to_datetime(df["End_Date"])

# --------------------
# Streamlit Page Config
# --------------------
st.set_page_config(page_title="Natural Disaster Analytics Dashboard ", layout="wide")
st.title("🌍 Natural Disaster Dashboard 2010 - 2025")

st.markdown(
    '<p style="font-size:18px;"> Developed by <a href="https://github.com/NaveenSh7" target="_blank">Naveen S H</a></p>',
    unsafe_allow_html=True
)


# --------------------
#  Sidebar Filters
# --------------------
st.sidebar.header("Filters")

# Disaster Type filter
disaster_types = df["Disaster_Type"].unique()
selected_types = st.sidebar.multiselect("Select Disaster Type", disaster_types, disaster_types)

# Country filter
countries = df["Country"].unique()
selected_countries = st.sidebar.multiselect("Select Countries", countries, countries)

# Date range filter
min_date = df["Start_Date"].min()
max_date = df["Start_Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Apply filters
filtered_df = df[
    (df["Disaster_Type"].isin(selected_types)) &
    (df["Country"].isin(selected_countries)) &
    (df["Start_Date"] >= pd.to_datetime(date_range[0])) &
    (df["Start_Date"] <= pd.to_datetime(date_range[1]))
]

# --------------------
# Summary Metrics
# --------------------
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Disasters", len(filtered_df))
col2.metric("Total Fatalities", int(filtered_df["Fatalities"].sum()))
col3.metric("Total Affected", int(filtered_df["Affected"].sum()))

# --------------------
#  Disaster Type Distribution
# --------------------
st.markdown("## Disaster Type Distribution")
fig1 = px.histogram(
    filtered_df,
    x="Disaster_Type",
    color="Disaster_Type",
    title="Disaster Count by Type",
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# --------------------
# 6. Disaster Analysis Section
# --------------------
st.markdown("## Disaster Analysis")

# Fatalities by Disaster Type
fig2 = px.box(
    filtered_df,
    x="Disaster_Type",
    y="Fatalities",
    color="Disaster_Type",
    title="Fatalities by Disaster Type",
    template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)



# --------------------
#  Disaster vs Country (Top 7 Only)
# --------------------

st.subheader("🌍 Disaster vs Country (Top 7 Only)")
# Get top 7 countries
top7_countries = filtered_df["Country"].value_counts().nlargest(7).index
# Filter only top 7
country_df = filtered_df[filtered_df["Country"].isin(top7_countries)]
# Group data
country_data = (
    country_df.groupby(["Disaster_Type", "Country"])
    .size()
    .reset_index(name="Count")
)
# Plot
fig_country = px.bar(
    country_data,
    x="Disaster_Type",
    y="Count",
    color="Country",
    barmode="group",
    title="Disaster Count by Country (Top 7 Only)",
    template="plotly_dark"
)
st.plotly_chart(fig_country, use_container_width=True)


# --------------------
# 7. Timeline Analysis
# --------------------

st.markdown("## Timeline Analysis")

# Ensure Year is numeric
filtered_df["Year"] = pd.to_numeric(filtered_df["Year"], errors="coerce")

# Group and sort by Year
timeline_fatalities = (
    filtered_df.groupby(["Year", "Disaster_Type"])["Fatalities"]
    .sum()
    .reset_index()
    .sort_values("Year")
)

# Pick which Disaster Types to show by default
default_visible = ["Flood", "Storm", "Drought", "Volcanic activity"]   # ✅ only these visible
all_types = timeline_fatalities["Disaster_Type"].unique()

fig5 = px.line(
    timeline_fatalities,
    x="Year",
    y="Fatalities",
    color="Disaster_Type",
    title="Fatalities Over Time",
    template="plotly_dark",
    markers=True
)

# Update traces: only keep default_visible on
for trace in fig5.data:
    if trace.name not in default_visible:
        trace.visible = "legendonly"   # ✅ others hidden by default

st.plotly_chart(fig5, use_container_width=True)

st.subheader("📅 Yearly Disaster Trend")

# Exclude 2025
yearly_trend = (
    filtered_df[filtered_df["Year"] != 2025]
    .groupby("Year")
    .size()
    .reset_index(name="Count")
)

fig_yearly = px.line(
    yearly_trend, 
    x="Year", 
    y="Count", 
    markers=True,
    title="Number of Disasters per Year (Excluding 2025)",
    template="plotly_dark"
)

st.plotly_chart(fig_yearly, use_container_width=True)


# --------------------
# World Map: Disasters by Country
# --------------------
st.header("🌍 World Map: Disasters by Country")
#  Count disasters per country
country_counts = df.groupby("Country").size().reset_index(name="Disaster_Count")

fig_Disasters_Country = px.choropleth(
    country_counts,
    locations="Country",
    locationmode="country names",
    color="Disaster_Count",
    hover_name="Country",
    color_continuous_scale="Blues",   
    title="Number of Disasters by Country"
)
st.plotly_chart(fig_Disasters_Country, use_container_width=True)


# --------------------
# World Map: Fatalities by Country"
# --------------------
st.header("🌍 World Map: Fatalities by Country")
#  Sum fatalities per country
fatalities_counts = (
    df.groupby("Country")["Fatalities"].sum().reset_index(name="Fatalities_Count")
)

fig_Fatalities_Country = px.choropleth(
    fatalities_counts,
    locations="Country",
    locationmode="country names",
    color="Fatalities_Count",
    hover_name="Country",
    color_continuous_scale="Reds",  
    title="Number of Fatalities by Country"
)
st.plotly_chart(fig_Fatalities_Country, use_container_width=True)


# --------------------
# World Map: Affected Population by Country
# --------------------
# 🌍 World Map: Affected Population by Country
st.header("👥 Affected Population by Country")
affected_counts = df.groupby("Country")["Affected"].sum().reset_index(name="Affected_Count")

fig_Affected_Country = px.choropleth(
    affected_counts,
    locations="Country",
    locationmode="country names",
    color="Affected_Count",
    hover_name="Country",
    color_continuous_scale="Greens",  
    title="Total Affected Population by Country"
)
st.plotly_chart(fig_Affected_Country, use_container_width=True)


# --------------------
# Top 10s
# --------------------

st.subheader("💀 Top 10 Deadliest Disasters")
top_deadliest = filtered_df.sort_values(by="Fatalities", ascending=False).head(10)
st.table(top_deadliest[["Year", "Disaster_Type", "Country", "Fatalities"]])

st.subheader("👥 Top 10 Most Affecting Disasters")
top_affected = filtered_df.sort_values(by="Affected", ascending=False).head(10)
st.table(top_affected[["Year", "Disaster_Type", "Country", "Affected"]])
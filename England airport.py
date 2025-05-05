import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns

"""
Name: Jean Kadadihi
CS230: Section 
Data: New England Airports
URL: (Add your Streamlit Cloud link here if deployed)

Description:  
This app lets users explore airport data from New England (MA, CT, RI, NH, VT, ME). It includes data filtering by state, elevation, and airport type. Charts, tables, and interactive maps allow visual analysis. The app demonstrates Streamlit widgets, pandas queries, matplotlib/seaborn charts, and a custom PyDeck map.
"""

# Load dataset
df = pd.read_csv("new_england_airports.csv")

# [DA1] Clean and enrich data (drop missing geo or type info)
df.dropna(subset=['name', 'iso_region', 'latitude_deg', 'longitude_deg', 'elevation_ft', 'type'], inplace=True)

# [DA7] Add a derived column: elevation category
df['elevation_category'] = pd.cut(df['elevation_ft'], bins=[-10, 0, 500, 2000], labels=['Sea Level', 'Low', 'High'])

# [ST1] Dropdown for region/state selection
states = sorted(df['iso_region'].unique())
selected_state = st.sidebar.selectbox("Choose a State (iso_region)", states)

# [ST2] Slider for minimum elevation
min_elev = st.sidebar.slider("Minimum Elevation (ft)", int(df['elevation_ft'].min()), int(df['elevation_ft'].max()), 0)

# [ST3] Multiselect for airport type
types = df['type'].unique()
selected_types = st.sidebar.multiselect("Airport Type", types, default=list(types))

# [PY1] Filtering function
@st.cache_data
def filter_data(region, elev_min, types):
    filtered = df[
        (df['iso_region'] == region) &
        (df['elevation_ft'] >= elev_min) &
        (df['type'].isin(types))
    ]
    return filtered

filtered_df = filter_data(selected_state, min_elev, selected_types)

st.title("Explore New England Airports")
st.markdown("Filter and visualize airport data across MA, CT, RI, NH, VT, and ME.")

# [CHART1] Bar chart of number of airports by type
st.subheader("Airport Counts by Type")
type_counts = filtered_df['type'].value_counts()
fig1, ax1 = plt.subplots()
type_counts.plot(kind='bar', ax=ax1)
ax1.set_xlabel("Airport Type")
ax1.set_ylabel("Count")
ax1.set_title("Filtered Airport Type Counts")
st.pyplot(fig1)

# [MAP] Interactive map of filtered airports
st.subheader("Airport Locations")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=filtered_df['latitude_deg'].mean(),
        longitude=filtered_df['longitude_deg'].mean(),
        zoom=6,
        pitch=0
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude_deg, latitude_deg]',
            get_radius=10000,
            get_color='[0, 0, 255, 160]',
            pickable=True
        )
    ],
    tooltip={"text": "{name}\nElevation: {elevation_ft} ft"}
))

# [CHART2] Seaborn elevation boxplot
st.subheader("Elevation Distribution by Airport Type")
fig2, ax2 = plt.subplots()
sns.boxplot(data=filtered_df, x="type", y="elevation_ft", ax=ax2)
ax2.set_title("Elevation by Airport Type")
st.pyplot(fig2)

# [DA6] Pivot table: count by type and elevation category
st.subheader("Pivot Table: Airport Type vs Elevation Category")
pivot_table = pd.pivot_table(filtered_df, values='id', index='type', columns='elevation_category', aggfunc='count', fill_value=0)
st.dataframe(pivot_table)

# [PY4] Dictionary example: count airports per state
airport_counts = {region: count for region, count in df['iso_region'].value_counts().items()}
st.write("### Airport Counts per State (All Data)", airport_counts)

# [DA2] Sorting example: top 5 highest elevation airports
st.subheader("Top 5 Airports by Elevation")
top5 = df.sort_values("elevation_ft", ascending=False).head(5)
st.dataframe(top5[['name', 'iso_region', 'elevation_ft']])

# [DA5] Filter by two conditions
st.subheader("Airports Over 500 ft and Type 'small_airport'")
st.dataframe(df[(df['elevation_ft'] > 500) & (df['type'] == 'small_airport')][['name', 'iso_region', 'elevation_ft']])

# [CHART3] Filtered table
st.subheader("Filtered Airports Table")
st.dataframe(filtered_df)

# [EXTRA][PY1], [PY4], [DA7], [SEA1], [MAP] -- additional features included

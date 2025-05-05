"""Name:       Your Name
CS230:      Section XXX
Data:       New England Airports
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:
This program creates an interactive Streamlit app to explore New England airports. It allows users to filter airports by state, elevation, and type, displaying results in a bar chart, table, and interactive map. The app uses Pandas for data manipulation, Matplotlib for charts, and PyDeck for maps, with a user-friendly interface and custom styling.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# [PY1] Function with 2+ parameters
def filter_airports(df, state, elev_range, types):
    """Filter airports based on state, elevation range, and type."""
    filtered = df[df['state'].isin([state]) & 
                  (df['elevation_ft'] >= elev_range[0]) & 
                  (df['elevation_ft'] <= elev_range[1]) & 
                  df['type'].isin(types)]
    return filtered, len(filtered)  # [PY2] Return multiple values

# [PY4] Function using dictionary
def get_state_counts(df):
    """Return a dictionary of airport counts by state."""
    state_counts = df['state'].value_counts().to_dict()
    return state_counts

def main():
    # [ST4] Custom page design
    st.set_page_config(page_title="New England Airports Explorer", layout="wide")
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content { background-color: #f0f2f6; }
        .main { font-family: Arial, sans-serif; }
        h1 { color: #1f77b4; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Explore New England Airports")
    st.write("Filter and visualize airport data across MA, CT, RI, NH, VT, and ME.")

    # Load data
    try:
        df = pd.read_csv('new_england_airports.csv')  # Adjust filename as needed
    except FileNotFoundError:
        st.error("Please upload the New England Airports CSV file.")
        return

    # [DA1] Clean data
    df = df.dropna(subset=['name', 'state', 'latitude_deg', 'longitude_deg', 'elevation_ft', 'type'])
    df['elevation_ft'] = pd.to_numeric(df['elevation_ft'], errors='coerce').fillna(0)

    # [DA9] Create new column
    df['elevation_category'] = pd.cut(df['elevation_ft'], 
                                     bins=[0, 500, 1000, float('inf')], 
                                     labels=['Low', 'Medium', 'High'])

    # [ST4] Sidebar for navigation
    with st.sidebar:
        st.header("Filter Options")
        # [ST1] Dropdown for state
        states = ['MA', 'CT', 'RI', 'NH', 'VT', 'ME']
        selected_state = st.selectbox("Select State", states, key="state_select")
        
        # [ST2] Slider for elevation
        min_elev = int(df['elevation_ft'].min())
        max_elev = int(df['elevation_ft'].max())
        elev_range = st.slider("Elevation Range (ft)", min_elev, max_elev, (min_elev, max_elev), key="elev_slider")
        
        # [ST3] Multiselect for airport type
        types = df['type'].unique().tolist()
        selected_types = st.multiselect("Airport Types", types, default=types[:2], key="type_multiselect")

    # Query 1: Filter airports
    filtered_df, count = filter_airports(df, selected_state, elev_range, selected_types)
    st.subheader(f"Airports in {selected_state} ({count} found)")
    
    # [CHART2] Display filtered data as table
    if not filtered_df.empty:
        st.dataframe(filtered_df[['name', 'type', 'elevation_ft', 'elevation_category']])
    else:
        st.warning("No airports match the selected criteria.")

    # Query 2: Airport counts by type
    # [DA2] Sort data
    type_counts = filtered_df['type'].value_counts().sort_values(ascending=False)
    
    # [CHART1] Bar chart
    if not type_counts.empty:
        fig, ax = plt.subplots()
        type_counts.plot(kind='bar', ax=ax, color='#1f77b4')
        ax.set_title(f"Airport Types in {selected_state}", fontsize=14)
        ax.set_xlabel("Airport Type", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    else:
        st.warning("No data to display for the bar chart.")

    # Query 3: Map of airports
    # [MAP] PyDeck map
    if not filtered_df.empty:
        view_state = pdk.ViewState(
            latitude=filtered_df['latitude_deg'].mean(),
            longitude=filtered_df['longitude_deg'].mean(),
            zoom=6,
            pitch=0
        )
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position=['longitude_deg', 'latitude_deg'],
            get_color=[31, 119, 180, 160],
            get_radius=5000,
            pickable=True
        )
        tooltip = {
            "html": "<b>Name:</b> {name}<br><b>Type:</b> {type}<br><b>Elevation:</b> {elevation_ft} ft",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
        st.pydeck_chart(deck)
    else:
        st.warning("No data to display on the map.")

    # [DA4] Filter by condition (e.g., large airports)
    large_airports = df[df['type'] == 'large_airport']
    st.subheader("Summary: Large Airports")
    st.write(f"Total large airports in dataset: {len(large_airports)}")

    # [PY4] Display state counts
    state_counts = get_state_counts(df)
    st.subheader("Airports by State")
    for state, count in state_counts.items():
        st.write(f"{state}: {count} airports")

if __name__ == "__main__":
    main()
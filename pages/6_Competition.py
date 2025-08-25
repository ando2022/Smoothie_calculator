# smoothie_locator.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Load smoothie competitor data
path = "zurich_smoothie_places_with_ids.csv"
df = pd.read_csv(path)

st.set_page_config(layout="wide")
st.title("🥤 Smoothie Competitor Map – Zurich")

# Sidebar controls
st.sidebar.header("🔧 Location Criteria")
show_suggestions = st.sidebar.checkbox("💡 Show Suggested Locations", value=True)
min_rating = st.sidebar.slider("Minimum Nearby Avg Rating", 3.0, 5.0, 4.3, 0.1)
max_competitors = st.sidebar.slider("Max Nearby Competitors", 0, 5, 1)
scan_radius = st.sidebar.slider("Search Radius (meters)", 100, 1000, 400, 50)

# Define utility function for float range
def frange(start, stop, step):
    while start < stop:
        yield round(start, 6)
        start += step

# Define Zurich grid
lat_min, lat_max = 47.34, 47.42
lon_min, lon_max = 8.49, 8.57
step = 0.005

# Create map
m = folium.Map(location=[47.3769, 8.5417], zoom_start=13)
marker_cluster = MarkerCluster().add_to(m)

# Add competitor smoothie places
for _, row in df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"{row['name']} (⭐ {row['rating']})",
        icon=folium.Icon(color="blue", icon="cutlery", prefix='fa')
    ).add_to(marker_cluster)

# Compute and show candidate locations
if show_suggestions:
    candidates = []
    for lat in frange(lat_min, lat_max, step):
        for lon in frange(lon_min, lon_max, step):
            nearby_count = 0
            ratings = []

            for _, row in df.iterrows():
                dist = geodesic((lat, lon), (row["lat"], row["lon"])).meters
                if dist < scan_radius:
                    nearby_count += 1
                    if not pd.isna(row["rating"]):
                        ratings.append(row["rating"])

            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                if nearby_count <= max_competitors and avg_rating >= min_rating:
                    candidates.append((lat, lon, avg_rating, nearby_count))

    for lat, lon, avg_rating, count in candidates:
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color = 'green' if (count <= max_competitors and avg_rating >= min_rating) else 'orange',
            fill=True,
            fill_opacity=0.6,
            popup=f"Suggested Spot 🟢\nRating Nearby: {avg_rating:.2f}\nCompetitors: {count}"
        ).add_to(m)

# Display final map
st_folium(m, width=1000)
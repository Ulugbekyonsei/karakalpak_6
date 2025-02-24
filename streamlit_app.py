import streamlit as st
import requests, json
import plotly.io as pio
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static

st.title("Qoraqalpog'iston Respublikasida mahallar bo'yicha tahlil")

# URL to your JSON file hosted on GitHub (raw link)
json_url = "https://raw.githubusercontent.com/Ulugbekyonsei/karakalpak_5/master/myplotly_fig.json"

# Fetch the JSON file
response = requests.get(json_url)
response.raise_for_status()  # Ensure the request was successful
fig_json = response.text

# Convert JSON string back to a plotly figure
fig = pio.from_json(fig_json, skip_invalid=True)

# Option 1: Update layout colorway
fig.update_layout(colorway=['red', 'green', 'blue'])

# Option 2: Alternatively, update each trace individually


# Display the updated plot in Streamlit
st.plotly_chart(fig)



st.title("Qoraqalpog'iston Respublikasida mahallar bo'yicha tahlil")

# URL to your GeoJSON file hosted on GitHub (replace with your actual URL)
geojson_url = "https://raw.githubusercontent.com/yourusername/yourrepo/main/karakalpak_sf_clustered.geojson"

# Read the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file(geojson_url)

# Ensure the 'cluster' column is treated as string for our color mapping
gdf['cluster'] = gdf['cluster'].astype(str)

# Define the color mapping for clusters (adjust the keys as needed based on your data)
color_mapping = {
    "1": "green",
    "2": "blue",
    "3": "red"
}

# Create a Folium map centered on your data.
centroid = gdf.geometry.centroid.unary_union.centroid
m = folium.Map(location=[centroid.y, centroid.x], zoom_start=8)

# Define a style function to apply colors based on the cluster
def style_function(feature):
    cluster_val = feature['properties']['cluster']
    return {
        'fillColor': color_mapping.get(cluster_val, 'gray'),
        'color': 'black',
        'weight': 2,
        'dashArray': '3',
        'fillOpacity': 0.7,
    }

# Add the GeoJSON layer with tooltips showing the region name (mahalla_no) and cluster
folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['mahalla_no', 'cluster'],
        aliases=['Mahalla No:', 'Cluster:'],
        localize=True
    )
).add_to(m)

# Optionally add a legend manually
legend_html = """
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 100px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     padding: 10px;
     ">
<strong>Cluster Legend</strong><br>
<i style="background:green;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 1<br>
<i style="background:blue;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 2<br>
<i style="background:red;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 3
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Render the map in Streamlit
folium_static(m)

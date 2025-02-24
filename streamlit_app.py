import streamlit as st
import geopandas as gpd
import requests
import folium
from streamlit_folium import folium_static
from fiona.io import MemoryFile

st.title("Qoraqalpog'iston Respublikasida mahallar bo'yicha tahlil")

# Replace with the correct URL for your GeoJSON file
geojson_url = "https://raw.githubusercontent.com/Ulugbekyonsei/karakalpak_5/master/karakalpak_sf_clustered.geojson"

# Fetch the GeoJSON file manually
response = requests.get(geojson_url)
if response.status_code != 200:
    st.error(f"Error fetching GeoJSON file: HTTP {response.status_code}")
else:
    # Use Fiona's MemoryFile to load the GeoJSON from bytes
    with MemoryFile(response.content) as memfile:
        with memfile.open() as src:
            gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)

    # Ensure the 'cluster' column is treated as a string for our color mapping
    gdf['cluster'] = gdf['cluster'].astype(str)

    # Define the color mapping for clusters
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

    # Add the GeoJSON layer with tooltips showing the region name and cluster
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

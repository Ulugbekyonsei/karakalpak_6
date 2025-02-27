import streamlit as st
import requests, json
import plotly.io as pio
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from fiona.io import MemoryFile

st.title("Qoraqalpog'iston Respublikasida mahallar bo'yicha tahlil")
st.write("""
Qoraqalpog'iston Respublikasidagi 423 ta mahallalarni 2024-yilda vegitatsiya darajasi, 
tungi yorug’lik darajasi va aholi zichligini hisobga olgan holda quyidagi 3 guruhga bo’lindi*:

1) Aholi zichligi, tungi yorug’lik darajasi hamda vegitatsiya darajasi past hududlar 
   (to'q ko'k): juda chekka hududlar

2) Aholi zichligi, tungi yorug’lik darajasi past ammo vegitatsiya darajasi nisbatan yuqori hududlar 
   (och ko'k): qishloq xo’jaligi potensiali yuqori hududlar

3) Aholi zichligi, tungi yorug’lik darajasi yuqori ammo vegitatsiya darajasi past hududlar 
   (o'rta ko’k): shaharlashgan hududlar
   
*Tahlil uchun K-means klasterlash usulidan foydalanildi
""")

# -----------------------------------------------------------
# Section 1: Plotly Figure from JSON on GitHub
# -----------------------------------------------------------
json_url = "https://raw.githubusercontent.com/Ulugbekyonsei/karakalpak_6/master/myplotly_fig1.json"

# Fetch the JSON file for the Plotly figure
response = requests.get(json_url)
response.raise_for_status()  # Ensure the request was successful
fig_json = response.text

# Convert JSON string back to a Plotly figure and update colors
fig = pio.from_json(fig_json, skip_invalid=True)
fig.update_layout(colorway=['red', 'green', 'blue'])

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)

# -----------------------------------------------------------
# Section 2: Interactive Map with Folium using GeoJSON
# -----------------------------------------------------------
st.title("Xaritada ko'rinishi")

# URL for your GeoJSON file on GitHub
geojson_url = "https://raw.githubusercontent.com/Ulugbekyonsei/karakalpak_6/master/karakalpak_sf_clustered.geojson"

# Fetch the GeoJSON file manually
response_geo = requests.get(geojson_url)
if response_geo.status_code != 200:
    st.error(f"Error fetching GeoJSON file: HTTP {response_geo.status_code}")
else:
    # Use Fiona's MemoryFile to load the GeoJSON from bytes
    with MemoryFile(response_geo.content) as memfile:
        with memfile.open() as src:
            gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)
    
    # Ensure the 'cluster' column is treated as a string for our color mapping
    gdf['cluster'] = gdf['cluster'].astype(str)

    # Define the color mapping for clusters
    color_mapping = {
        "1": "#DEEBF7",  # Light blue
        "2": "#4292C6",  # Dark blue 
        "3": "#08306B"   # Mid blue 
    }

    # Create a Folium map centered on your data
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
    <i style="background:#DEEBF7;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 1 (Light Blue)<br>
    <i style="background:#08306B;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 2 (Dark Blue)<br>
    <i style="background:#4292C6;width:10px;height:10px;display:inline-block;"></i>&nbsp;Cluster 3 (Mid Blue)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Render the Folium map in Streamlit
    folium_static(m)

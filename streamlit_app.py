import streamlit as st
import requests, json
import plotly.io as pio

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

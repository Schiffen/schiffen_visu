import streamlit as st
import pandas as pd
from io import StringIO
import requests

st.set_page_config(
    page_title="Cultural Evolution of Popularity Dashboard",
    page_icon=":musical_note:"
)

@st.cache_data
def get_cloned_data():
    """Load and clone the dataset."""
    DATA_URL = "https://raw.githubusercontent.com/Schiffen/schiffen_visu/main/data%20project.csv"

    response = requests.get(DATA_URL)
    if response.status_code != 200:
        st.error("Failed to load data.")
        return None

    original_data = pd.read_csv(StringIO(response.text))
    cloned_data = original_data.copy()
    cloned_data['Release.Date'] = pd.to_datetime(cloned_data['Release.Date'], errors='coerce')
    cloned_data['Year'] = cloned_data['Release.Date'].dt.year

    return cloned_data

data = get_cloned_data()

if data is not None:
    st.title("🎵 Cultural Evolution of Popularity Dashboard")
    st.subheader("Streams/Views Over Time by Platform")

    min_year, max_year = 2014, 2024
    data = data[(data['Year'] >= min_year) & (data['Year'] <= max_year)]

    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    for feature in features:
        data = data[data[feature] != -1]

    platforms = []
    for feature in features:
        explicit_data = data[data['Explicit.Track'] == 1][['Year', feature]].groupby('Year').sum()
        explicit_data['Platform'] = f"{feature} (Explicit)"
        platforms.append(explicit_data)

        non_explicit_data = data[data['Explicit.Track'] == 0][['Year', feature]].groupby('Year').sum()
        non_explicit_data['Platform'] = f"{feature} (Non-Explicit)"
        platforms.append(non_explicit_data)

    combined_data = pd.concat(platforms)
    combined_data.reset_index(inplace=True)
    combined_data.rename(columns={combined_data.columns[1]: "Streams/Views"}, inplace=True)

    st.line_chart(
        combined_data,
        x='Year',
        y='Streams/Views',
        color='Platform'
    )
else:
    st.error("No data available. Please check the source.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import requests

# Set the page title and favicon
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

    # Ensure Release.Date is in datetime format and extract Year
    cloned_data['Release.Date'] = pd.to_datetime(cloned_data['Release.Date'], errors='coerce')
    cloned_data['Year'] = cloned_data['Release.Date'].dt.year

    return cloned_data

data = get_cloned_data()

if data is not None:
    st.title("🎵 Cultural Evolution of Popularity Dashboard")
    st.subheader("Streams/Views Over Time by Platform")

    # Filter by years 2014–2024
    data = data[(data['Year'] >= 2014) & (data['Year'] <= 2024)]

    # Drop rows with -1 in relevant columns
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    for feature in features:
        data = data[data[feature] != -1]

    # Remove any remaining null values
    data.dropna(inplace=True)

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = {
        'Spotify.Streams': 'blue',
        'YouTube.Views': 'red',
        'TikTok.Views': 'green',
        'Pandora.Streams': 'orange'
    }

    for feature in features:
        # Group by year for explicit tracks
        explicit_data = data[data['Explicit.Track'] == 1].groupby('Year')[feature].sum()
        non_explicit_data = data[data['Explicit.Track'] == 0].groupby('Year')[feature].sum()

        # Plot explicit tracks
        ax.plot(
            explicit_data.index, explicit_data.values,
            label=f"{feature} (Explicit)", linestyle='-', color=colors[feature]
        )

        # Plot non-explicit tracks
        ax.plot(
            non_explicit_data.index, non_explicit_data.values,
            label=f"{feature} (Non-Explicit)", linestyle='--', color=colors[feature]
        )

    # Customize the plot
    ax.set_title("Number of Views/Streams by Platform and Explicitness (2014–2024)", fontsize=16)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Views/Streams", fontsize=12)
    ax.set_xticks(range(2014, 2025))  # Set x-axis ticks to show only 2014–2024
    ax.set_yticks(range(0, int(data[features].max().max()), 500_000))  # Y-axis increments
    ax.legend(fontsize=10)
    ax.grid(True)

    # Show the plot
    st.pyplot(fig)
else:
    st.error("No data available. Please check the source.")

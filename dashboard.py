import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import requests

# Set the title and favicon that appear in the browser's tab bar.
st.set_page_config(
    page_title="Cultural Evolution of Popularity Dashboard",
    page_icon=":musical_note:",  # Emoji to reflect music/popularity theme
)

# ---------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_data():
    """Load the project data from GitHub.

    This uses caching to avoid downloading the file every time the app refreshes.
    """

    # URL to the raw CSV file in your GitHub repository
    DATA_URL = "https://raw.githubusercontent.com/Schiffen/schiffen_visu/main/data%20project.csv"

    # Download the file from GitHub
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        st.error("Failed to load data. Please check the GitHub URL or network connection.")
        return None

    # Load the data into a Pandas DataFrame
    data = pd.read_csv(StringIO(response.text))

    # Ensure Release.Date is in datetime format and extract Year
    data['Release.Date'] = pd.to_datetime(data['Release.Date'], errors='coerce')
    data['Year'] = data['Release.Date'].dt.year

    return data

# Load data
data = get_data()

if data is not None:
    # ---------------------------------------------------------------------------
    # Draw the actual page

    # Set the title that appears at the top of the page.
    '''
    # :musical_note: Cultural Evolution of Popularity Dashboard

    Explore how explicitness correlates with popularity across years on various streaming platforms.
    '''

    # Filter the data to the years 2014 to 2024
    data = data[(data['Year'] >= 2014) & (data['Year'] <= 2024)]

    # Filter out rows where stream/view counts are -1 for any feature
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    for feature in features:
        data = data[data[feature] != -1]

    # Create a plot for each feature
    st.header("Views/Streams Over Time by Platform")

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        'Spotify.Streams': 'blue',
        'YouTube.Views': 'red',
        'TikTok.Views': 'green',
        'Pandora.Streams': 'orange'
    }

    for feature in features:
        # Separate explicit and non-explicit tracks
        explicit_data = data[data['Explicit.Track'] == 1]
        non_explicit_data = data[data['Explicit.Track'] == 0]

        # Group data by year and sum the views/streams
        explicit_grouped = explicit_data.groupby('Year')[feature].sum()
        non_explicit_grouped = non_explicit_data.groupby('Year')[feature].sum()

        # Plot explicit tracks as solid lines
        ax.plot(explicit_grouped.index, explicit_grouped.values,
                label=f"{feature} (Explicit)", linestyle='-', color=colors[feature])

        # Plot non-explicit tracks as dashed lines
        ax.plot(non_explicit_grouped.index, non_explicit_grouped.values,
                label=f"{feature} (Non-Explicit)", linestyle='--', color=colors[feature])

    # Customize the plot
    ax.set_title("Number of Views/Streams (2014–2024)", fontsize=14)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Views/Streams", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True)

    # Show the plot
    st.pyplot(fig)

else:
    st.warning("No data available to display. Please check the data source.")

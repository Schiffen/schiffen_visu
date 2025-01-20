import streamlit as st
import pandas as pd
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

    # Add some spacing
    ''
    ''

    # Slider for selecting year range
    min_year = int(data['Year'].min())
    max_year = int(data['Year'].max())

    from_year, to_year = st.slider(
        "Select the year range:",
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year]
    )

    # ---------------------------------------------------------------------------
    # Further visualization or data operations will be added later.
    # For now, this dashboard establishes the foundational setup for filtering.

else:
    st.warning("No data available to display. Please check the data source.")

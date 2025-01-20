import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon that appear in the browser's tab bar.
st.set_page_config(
    page_title="Cultural Evolution of Popularity Dashboard",
    page_icon=":musical_note:",  # Emoji to reflect music/popularity theme
)

# ---------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_data():
    """Load the project data from a CSV file.

    This uses caching to avoid reading the file every time the app refreshes.
    """

    # Full path to the project data file
    DATA_FILENAME = Path(r"C:\Users\97254\Downloads\data project.csv")
    data = pd.read_csv(DATA_FILENAME)

    # Ensure Release.Date is in datetime format and extract Year
    data['Release.Date'] = pd.to_datetime(data['Release.Date'], errors='coerce')
    data['Year'] = data['Release.Date'].dt.year

    return data

# Load data
data = get_data()

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

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import requests

st.set_page_config(
    page_title="Cultural Evolution of Popularity Dashboard",
    page_icon=":musical_note:"
)

@st.cache_data
def get_cloned_data():
    """Load and clean the dataset."""
    DATA_URL = "https://raw.githubusercontent.com/Schiffen/schiffen_visu/main/data%20project.csv"

    # Fetch the data from the provided URL
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        st.error("Failed to load data from the provided URL.")
        return None

    # Load the data into a DataFrame
    raw_data = pd.read_csv(StringIO(response.text))
    st.write("Raw Data Loaded:", raw_data.head())  # Debug: Check raw data

    # Print all column names for debugging
    st.write("Column Names:", raw_data.columns)

    # Ensure the required columns are present
    expected_columns = [
        'Release.Date', 'Explicit.Track',
        'Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams'
    ]
    missing_columns = [col for col in expected_columns if col not in raw_data.columns]
    if missing_columns:
        st.error(f"Missing columns in data: {missing_columns}")
        return None

    # Clean the data
    cloned_data = raw_data.copy()

    # Convert Release.Date to datetime and extract Year
    cloned_data['Release.Date'] = pd.to_datetime(cloned_data['Release.Date'], errors='coerce')
    cloned_data['Year'] = cloned_data['Release.Date'].dt.year

    # Replace -1 with NaN in the relevant features and ensure numeric conversion
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    for feature in features:
        cloned_data[feature] = cloned_data[feature].replace(-1, pd.NA)  # Replace -1 with NaN
        cloned_data[feature] = pd.to_numeric(cloned_data[feature], errors='coerce')  # Convert to numeric
        st.write(f"Sample of {feature} after cleaning:", cloned_data[feature].head())  # Debug: Check feature values

    st.write("Cleaned Data Sample:", cloned_data.head())  # Debug: Check cleaned data

    return cloned_data

# Load the cleaned data
data = get_cloned_data()

if data is not None:
    st.title("🎵 Cultural Evolution of Popularity Dashboard")
    st.subheader("Streams/Views Over Time by Platform")

    # Filter data for years 2014–2024
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    temp_data = data[(data['Year'] >= 2014) & (data['Year'] <= 2024)].copy()
    st.write("Filtered Data Sample:", temp_data.head())  # Debug: Check filtered data

    # Prepare grouped data for plotting
    plot_data = []
    for feature in features:
        # Group explicit and non-explicit data by year
        explicit_grouped = temp_data[temp_data['Explicit.Track'] == 1].groupby('Year')[feature].sum()
        non_explicit_grouped = temp_data[temp_data['Explicit.Track'] == 0].groupby('Year')[feature].sum()

        st.write(f"Grouped Data for {feature} (Explicit):", explicit_grouped)  # Debug: Check grouping
        st.write(f"Grouped Data for {feature} (Non-Explicit):", non_explicit_grouped)

        # Add to plot data
        plot_data.append(pd.DataFrame({
            'Year': explicit_grouped.index,
            'Streams/Views': explicit_grouped.values,
            'Platform': f"{feature} (Explicit)"
        }))
        plot_data.append(pd.DataFrame({
            'Year': non_explicit_grouped.index,
            'Streams/Views': non_explicit_grouped.values,
            'Platform': f"{feature} (Non-Explicit)"
        }))

    # Combine all platform data into one DataFrame
    combined_data = pd.concat(plot_data)
    st.write("Combined Data for Plotting:", combined_data.head())  # Debug: Check combined data

    # Adjust Y-axis scaling
    combined_data.dropna(subset=['Streams/Views'], inplace=True)
    max_value = combined_data['Streams/Views'].max()

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = {
        'Spotify.Streams': 'blue',
        'YouTube.Views': 'red',
        'TikTok.Views': 'green',
        'Pandora.Streams': 'orange'
    }

    # Plot each platform's data with explicit/non-explicit lines
    for platform in combined_data['Platform'].unique():
        platform_data = combined_data[combined_data['Platform'] == platform]
        linestyle = '-' if 'Explicit' in platform else '--'
        color = colors[platform.split()[0]]
        ax.plot(
            platform_data['Year'],
            platform_data['Streams/Views'],
            label=platform,
            linestyle=linestyle,
            color=color
        )

    # Customize the x-axis and y-axis
    ax.set_xticks(range(2014, 2025))
    ax.set_xlim(2014, 2024)
    ax.set_yticks(range(0, int(max_value) + 500_000, 500_000))
    ax.set_ylim(0, max_value + 500_000)

    # Add title, labels, and legend
    ax.set_title("Number of Views/Streams by Platform and Explicitness (2014–2024)", fontsize=16)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Views/Streams", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True)

    # Show the plot
    st.pyplot(fig)
else:
    st.error("No data available. Please check the source.")

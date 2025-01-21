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

    response = requests.get(DATA_URL)
    if response.status_code != 200:
        st.error("Failed to load data.")
        return None

    original_data = pd.read_csv(StringIO(response.text))
    cloned_data = original_data.copy()

    # Ensure Release.Date is in datetime format and extract Year
    cloned_data['Release.Date'] = pd.to_datetime(cloned_data['Release.Date'], errors='coerce')
    cloned_data['Year'] = cloned_data['Release.Date'].dt.year

    # Convert relevant columns to numeric, coercing errors to NaN
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    for feature in features:
        cloned_data[feature] = pd.to_numeric(cloned_data[feature], errors='coerce')

    return cloned_data

data = get_cloned_data()

if data is not None:
    st.title("🎵 Cultural Evolution of Popularity Dashboard")
    st.subheader("Streams/Views Over Time by Platform")

    # Debug: Check if raw data is loaded
    st.write("Raw Data Sample:", data.head())
    st.write("Raw Data Shape:", data.shape)

    # Filter data for years 2014–2024
    features = ['Spotify.Streams', 'YouTube.Views', 'TikTok.Views', 'Pandora.Streams']
    temp_data = data[(data['Year'] >= 2014) & (data['Year'] <= 2024)].copy()

    # Replace -1 with NaN and drop invalid values for each feature
    for feature in features:
        temp_data[feature] = temp_data[feature].replace(-1, pd.NA)

    # Debug: Check the filtered data
    st.write("Filtered Data Sample:", temp_data.head())
    st.write("Filtered Data Shape:", temp_data.shape)

    # Prepare grouped data for plotting
    plot_data = []
    for feature in features:
        # Group explicit and non-explicit data by year, summing up streams/views
        explicit_grouped = temp_data[temp_data['Explicit.Track'] == 1].groupby('Year')[feature].sum()
        non_explicit_grouped = temp_data[temp_data['Explicit.Track'] == 0].groupby('Year')[feature].sum()

        # Debug: Log grouped data
        st.write(f"Explicit Data for {feature}:", explicit_grouped)
        st.write(f"Non-Explicit Data for {feature}:", non_explicit_grouped)

        # Store results in a structured DataFrame for plotting
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

    # Debug: Check the combined data for plotting
    st.write("Combined Data for Plotting:", combined_data.head())
    st.write("Combined Data Shape:", combined_data.shape)

    # Adjust Y-axis scaling
    combined_data.dropna(subset=['Streams/Views'], inplace=True)  # Ensure no NaN values remain
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
    ax.set_xticks(range(2014, 2025))  # Ensure years from 2014 to 2024
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

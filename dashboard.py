import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Artist Popularity Analysis 2015-2023",
    page_icon="🎵",
    layout="wide"
)

# Title and description
st.title("🎵 Artist Popularity Trends (2015-2023)")
st.markdown("""
This dashboard explores the popularity trends of top music artists from 2015 to 2023. 
The analysis focuses on track scores and release patterns to understand artist performance over time.
""")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv("data project.csv")
    # Convert Release.Date to datetime
    df['Release.Date'] = pd.to_datetime(df['Release.Date'])
    # Extract year
    df['Year'] = df['Release.Date'].dt.year
    return df

df = load_data()

# List of artists to analyze
ARTISTS = [
    "Drake", "Taylor Swift", "Justin Bieber", "Miley Cyrus", 
    "Dua Lipa", "Billie Eilish", "Bad Bunny", "The Weeknd", 
    "Future", "Post Malone", "KAROL G"
]

# Filter data for selected artists and years
filtered_df = df[
    (df['Artist'].isin(ARTISTS)) & 
    (df['Year'] >= 2015) & 
    (df['Year'] <= 2023)
]

# Calculate yearly averages for each artist
yearly_stats = filtered_df.groupby(['Artist', 'Year']).agg({
    'Track.Score': 'mean',
    'Track': 'count'  # Count of tracks per year
}).reset_index()

# Main visualization section
st.header("Artist Performance Analysis")

# Create two columns for filters
col1, col2 = st.columns(2)

with col1:
    selected_artists = st.multiselect(
        "Select Artists to Compare",
        ARTISTS,
        default=ARTISTS[:5]  # Default to first 5 artists
    )

with col2:
    selected_years = st.slider(
        "Select Year Range",
        min_value=2015,
        max_value=2023,
        value=(2015, 2023)
    )

# Filter based on selection
plot_data = yearly_stats[
    (yearly_stats['Artist'].isin(selected_artists)) &
    (yearly_stats['Year'].between(selected_years[0], selected_years[1]))
]

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Popularity Trends", "Release Patterns", "Comparative Analysis"])

with tab1:
    # Line chart for popularity trends
    fig1 = px.line(
        plot_data,
        x='Year',
        y='Track.Score',
        color='Artist',
        title='Artist Popularity Trends Over Time',
        labels={'Track.Score': 'Average Track Score', 'Year': 'Year'},
        line_shape='spline',
        markers=True
    )
    
    fig1.update_layout(
        height=600,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # Stacked bar chart for number of releases
    fig2 = px.bar(
        plot_data,
        x='Year',
        y='Track',
        color='Artist',
        title='Number of Tracks Released per Year',
        labels={'Track': 'Number of Tracks', 'Year': 'Year'},
        barmode='stack'
    )
    
    fig2.update_layout(
        height=600,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    # Create a scatter plot with size representing number of tracks
    fig3 = px.scatter(
        plot_data,
        x='Year',
        y='Track.Score',
        size='Track',
        color='Artist',
        title='Artist Performance Matrix',
        labels={
            'Track.Score': 'Average Track Score',
            'Year': 'Year',
            'Track': 'Number of Tracks Released'
        }
    )
    
    fig3.update_layout(
        height=600,
        template='plotly_white',
        hovermode='closest'
    )
    
    st.plotly_chart(fig3, use_container_width=True)

# Summary statistics
st.header("Artist Performance Summary")
st.markdown("### Key Statistics")

# Calculate summary statistics
summary_stats = filtered_df.groupby('Artist').agg({
    'Track.Score': ['mean', 'max', 'count']
}).round(2)

summary_stats.columns = ['Average Score', 'Peak Score', 'Total Tracks']
summary_stats = summary_stats.sort_values('Average Score', ascending=False)

# Display summary table
st.dataframe(
    summary_stats,
    use_container_width=True,
    hide_index=False
)

# Footer with data information
st.markdown("---")
st.markdown("""
**Data Notes:**
- Track scores range from 0 to 100, with 100 being the highest possible score
- Analysis includes tracks released between 2015 and 2023
- Some artists may have incomplete data for certain years
""")

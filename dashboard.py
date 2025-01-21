import pandas as pd
import plotly.graph_objects as go

# Load and prepare data
DATA_URL = "https://raw.githubusercontent.com/Schiffen/schiffen_visu/main/data%20project.csv"

# Load data directly from your GitHub repository
try:
    df = pd.read_csv(DATA_URL, encoding='utf-8')
except Exception as e:
    print(f"Error loading data: {e}")

# Ensure column names match expected format
expected_columns = [
    "Track", "Album.Name", "Artist", "Release.Date", "All.Time.Rank", "Track.Score",
    "Spotify.Streams", "Spotify.Playlist.Count", "Spotify.Playlist.Reach", "Spotify.Popularity",
    "YouTube.Views", "YouTube.Likes", "TikTok.Posts", "TikTok.Likes", "TikTok.Views",
    "YouTube.Playlist.Reach", "Apple.Music.Playlist.Count", "AirPlay.Spins", "SiriusXM.Spins",
    "Deezer.Playlist.Count", "Deezer.Playlist.Reach", "Amazon.Playlist.Count", "Pandora.Streams",
    "Pandora.Track.Stations", "Soundcloud.Streams", "Shazam.Counts", "Explicit.Track"
]

# Check for missing columns
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    print(f"Warning: Missing columns in dataset - {missing_columns}")

# Ensure Release.Date is in datetime format
df['Release.Date'] = pd.to_datetime(df['Release.Date'], errors='coerce')
df.set_index('Release.Date', inplace=True)

# Replace -1 with NaN for relevant columns
numeric_cols = [
    "Spotify.Streams", "YouTube.Views", "TikTok.Views", "Pandora.Streams"
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').replace(-1, pd.NA)
    else:
        print(f"Warning: Column {col} missing from dataset.")

# Add aggregated column for other platforms
other_platforms = ["AirPlay.Spins", "SiriusXM.Spins", "Pandora.Streams", "Deezer.Playlist.Reach", "Soundcloud.Streams"]
if all(platform in df.columns for platform in other_platforms):
    df["other"] = df[other_platforms].sum(axis=1)
else:
    print(f"Warning: One or more columns in {other_platforms} are missing. 'other' column will be incomplete.")

# Fill NaN values in Explicit.Track with 0 and convert to integer
df["Explicit.Track"] = df["Explicit.Track"].fillna(0).astype(int)

# Define columns for analysis
analysis_columns = ["YouTube.Views", "Spotify.Streams", "TikTok.Views", "other"]

# Resample data to monthly sums
explicit_data = df[df["Explicit.Track"] == 1].resample("MS").sum()
non_explicit_data = df[df["Explicit.Track"] == 0].resample("MS").sum()

# Calculate the number of songs in each month
explicit_counts = df[df["Explicit.Track"] == 1].resample("MS").size()
non_explicit_counts = df[df["Explicit.Track"] == 0].resample("MS").size()

# Apply a 6-month moving average
explicit_smoothed = explicit_data[analysis_columns].rolling(window=6, center=True).mean()
non_explicit_smoothed = non_explicit_data[analysis_columns].rolling(window=6, center=True).mean()

# Create the plot using Plotly
fig = go.Figure()

# Define line colors for the platforms
colors = ["red", "green", "#4A90A4", "purple"]

# Add explicit and non-explicit data
for i, col in enumerate(analysis_columns):
    # Explicit line
    fig.add_trace(go.Scatter(
        x=explicit_smoothed.index,
        y=explicit_smoothed[col],
        mode="lines",
        name=f"{col.replace('.', ' ')} (Explicit)",
        line=dict(width=2.5, color=colors[i % len(colors)], dash="solid"),
        hovertemplate="%{x}<br>Explicit Streams: %{y:,.0f}<extra></extra>",
    ))

    # Add line thickness based on song counts
    fig.add_trace(go.Scatter(
        x=explicit_smoothed.index,
        y=explicit_smoothed[col],
        mode="lines",
        name=f"{col.replace('.', ' ')} (Explicit Songs)",
        line=dict(width=(explicit_counts / explicit_counts.max()) * 5, color=colors[i % len(colors)], dash="solid"),
        hovertemplate="%{x}<br>Number of Explicit Songs: %{customdata}<extra></extra>",
        customdata=explicit_counts.values
    ))

    # Non-explicit line
    fig.add_trace(go.Scatter(
        x=non_explicit_smoothed.index,
        y=non_explicit_smoothed[col],
        mode="lines",
        name=f"{col.replace('.', ' ')} (Non-Explicit)",
        line=dict(width=2.5, color=colors[i % len(colors)], dash="dash"),
        hovertemplate="%{x}<br>Non-Explicit Streams: %{y:,.0f}<extra></extra>",
    ))

    # Add line thickness based on song counts
    fig.add_trace(go.Scatter(
        x=non_explicit_smoothed.index,
        y=non_explicit_smoothed[col],
        mode="lines",
        name=f"{col.replace('.', ' ')} (Non-Explicit Songs)",
        line=dict(width=(non_explicit_counts / non_explicit_counts.max()) * 5, color=colors[i % len(colors)], dash="dash"),
        hovertemplate="%{x}<br>Number of Non-Explicit Songs: %{customdata}<extra></extra>",
        customdata=non_explicit_counts.values
    ))

# Add title and labels
fig.update_layout(
    title="Streams by Platform and Explicitness (2015-2024)",
    xaxis_title="Year",
    yaxis_title="Streams and Views",
    template="plotly_dark",
    legend_title="Platforms",
    hovermode="x unified",
    xaxis=dict(range=["2015-01-01", "2024-12-31"])
)

# Show the plot
fig.show()

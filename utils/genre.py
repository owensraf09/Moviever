"""
Genre-related functions for fetching and mapping genre data from TMDB.
"""
import streamlit as st
import requests
import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load TMDB Bearer Token from environment variable
TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")
if not TMDB_BEARER_TOKEN:
    raise ValueError(
        "TMDB_BEARER_TOKEN not found in environment variables. Please create a .env file with your token."
    )

# Ensure token starts with "Bearer " prefix
if not TMDB_BEARER_TOKEN.startswith("Bearer "):
    TMDB_BEARER_TOKEN = f"Bearer {TMDB_BEARER_TOKEN}"


@st.cache_data(ttl=config.GENRE_CACHE_TTL)
def fetch_genre_map() -> dict[int, str]:
    """
    Fetch genre ID to name mapping from TMDB.
    Returns dict mapping genre_id -> genre_name.
    Unknown IDs will map to "Unknown".
    """
    headers = {
        "accept": "application/json",
        "Authorization": TMDB_BEARER_TOKEN,
    }

    try:
        response = requests.get(
            config.TMDB_GENRE_URL,
            headers=headers,
            params={"language": "en-US"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        # Build mapping: {genre_id: genre_name}
        genre_map = {genre["id"]: genre["name"] for genre in data.get("genres", [])}
        return genre_map
    except Exception as e:
        st.warning(f"Failed to fetch genre map: {e}. Using empty map.")
        return {}

"""
CSV persistence functions for saving and loading movie data.
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
from ast import literal_eval
import config
from utils.genre import fetch_genre_map


def save_data_to_csv(df: pd.DataFrame) -> bool:
    """Save prepared DataFrame to CSV file."""
    try:
        df.to_csv(config.CSV_DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save data to CSV: {e}")
        return False


def load_data_from_csv() -> pd.DataFrame | None:
    """Load prepared DataFrame from CSV file if it exists."""
    if not os.path.exists(config.CSV_DATA_FILE):
        return None

    try:
        df = pd.read_csv(config.CSV_DATA_FILE)
        # Convert release_date back to datetime
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

        # Handle genre_ids column (might be stored as string in CSV)
        if "genre_ids" in df.columns:
            # Convert string representation of list back to list if needed
            if df["genre_ids"].dtype == "object":

                def parse_genre_ids(x):
                    if pd.isna(x) or x == "":
                        return []
                    if isinstance(x, list):
                        return x
                    # Try to parse string representation
                    try:
                        return literal_eval(str(x))
                    except:
                        return []

                df["genre_ids"] = df["genre_ids"].apply(parse_genre_ids)

        # Ensure gems_score and year are present (for backward compatibility)
        if "gems_score" not in df.columns:
            df["gems_score"] = (df["vote_average"] * np.log10(df["vote_count"] + 1)) / (
                df["popularity"] + 1
            )
            df["gems_score"] = df["gems_score"].fillna(0)
        if "year" not in df.columns:
            df["year"] = df["release_date"].dt.year

        # Handle genres column (might be stored as string in CSV)
        if "genres" in df.columns:
            # Convert string representation of list back to list if needed
            if df["genres"].dtype == "object":

                def parse_genres(x):
                    if pd.isna(x) or x == "":
                        return []
                    if isinstance(x, list):
                        return x
                    # Try to parse string representation
                    try:
                        parsed = literal_eval(str(x))
                        if isinstance(parsed, list):
                            return parsed
                    except:
                        pass
                    return []

                df["genres"] = df["genres"].apply(parse_genres)

        # Regenerate genres columns if missing (for backward compatibility with old CSV files)
        if "genres" not in df.columns or "genres_str" not in df.columns:
            genre_map = fetch_genre_map()

            def map_genre_ids(genre_ids):
                if not isinstance(genre_ids, list):
                    return []
                return [genre_map.get(gid, "Unknown") for gid in genre_ids]

            df["genres"] = df["genre_ids"].apply(map_genre_ids)
            df["genres_str"] = df["genres"].apply(
                lambda x: ", ".join(x) if x else "Unknown"
            )
        elif "genres_str" not in df.columns and "genres" in df.columns:
            # Regenerate genres_str if missing
            df["genres_str"] = df["genres"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) and x else "Unknown"
            )

        return df
    except Exception as e:
        st.warning(f"Failed to load data from CSV: {e}. Will fetch from TMDB instead.")
        return None


def delete_csv_cache():
    """Delete the CSV cache file."""
    try:
        if os.path.exists(config.CSV_DATA_FILE):
            os.remove(config.CSV_DATA_FILE)
            return True
    except Exception as e:
        st.error(f"Failed to delete CSV cache: {e}")
    return False

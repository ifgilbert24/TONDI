"""
stats.py
Fungsi statistik bersama untuk semua service.
Menghindari duplikasi kode groupby/aggregate.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_reviews
import pandas as pd


def compute_location_stats(reviews_df=None, min_reviews=5):
    """
    Menghitung statistik per lokasi.
    
    Returns DataFrame: place-name, total_reviews, rating_mean,
    positif, netral, negatif, negatif_ratio, z_score, status
    """
    if reviews_df is None:
        reviews_df = load_reviews()

    if reviews_df.empty:
        return pd.DataFrame()

    grouped = reviews_df.groupby("place-name").agg(
        total_reviews=("sentiment", "count"),
        rating_mean=("reviewer-rating", "mean"),
        positif=("sentiment", lambda x: (x == "Positif").sum()),
        netral=("sentiment", lambda x: (x == "Netral").sum()),
        negatif=("sentiment", lambda x: (x == "Negatif").sum()),
    ).reset_index()

    grouped["rating_mean"] = grouped["rating_mean"].round(2)

    # Z-Score hanya untuk lokasi dengan >= min_reviews
    mask = grouped["total_reviews"] >= min_reviews
    valid = grouped[mask].copy()

    if len(valid) > 0:
        valid["negatif_ratio"] = valid["negatif"] / valid["total_reviews"]
        mean = valid["negatif_ratio"].mean()
        std = valid["negatif_ratio"].std()
        if std == 0:
            valid["z_score"] = 0.0
        else:
            valid["z_score"] = valid["negatif_ratio"].apply(
                lambda x: (x - mean) / std
            )
        valid["status"] = valid["z_score"].apply(
            lambda z: "red" if z > 2.0 else ("yellow" if z > 1.0 else "green")
        )
    else:
        valid["z_score"] = 0.0
        valid["status"] = "green"
        valid["negatif_ratio"] = 0.0

    # Gabungkan hasil
    result = grouped.merge(
        valid[["place-name", "z_score", "status", "negatif_ratio"]],
        on="place-name",
        how="left",
    )
    result["z_score"] = result["z_score"].fillna(0.0).round(2)
    result["status"] = result["status"].fillna("green")
    result["negatif_ratio"] = result["negatif_ratio"].fillna(0.0).round(4)

    return result

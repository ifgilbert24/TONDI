"""priorities.py - Priority Score."""
import sys, os, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews
from utils.stats import compute_location_stats

def _normalize(s):
    if s.max() == s.min(): return pd.Series([50]*len(s))
    return (s - s.min()) / (s.max() - s.min()) * 100

def compute_priority_score(stats_df):
    """Compute priority score from stats DataFrame. Returns same df with added 'priority_score' column."""
    df = stats_df.copy()
    df["rating_mean"] = df["rating_mean"].fillna(3.0)
    df["priority_score"] = (
        _normalize(df["z_score"]) * 0.40
        + _normalize(df["negatif_ratio"]) * 0.30
        + _normalize(df["total_reviews"]) * 0.20
        + _normalize(5 - df["rating_mean"]) * 0.10
    )
    return df

def get_priority_status(score):
    """Convert numeric priority score to status label."""
    if score >= 70: return "Merah"
    elif score >= 40: return "Kuning"
    return "Hijau"

def get_priority_status_en(score):
    """Convert numeric priority score to English status (for map markers)."""
    if score >= 70: return "red"
    elif score >= 40: return "yellow"
    return "green"

def get_priorities(limit=20):
    reviews_df = load_reviews()
    if reviews_df.empty: return []
    grouped = compute_location_stats(reviews_df, min_reviews=3)
    if grouped.empty: return []
    grouped = compute_priority_score(grouped)
    grouped = grouped.sort_values("priority_score", ascending=False).head(limit)
    return [{"name": r["place-name"], "score": round(r["priority_score"], 1), "status": get_priority_status(r["priority_score"]), "total_reviews": int(r["total_reviews"]), "rating": round(r["rating_mean"], 2), "negatif": int(r["negatif"]), "negatif_ratio": round(r["negatif_ratio"], 4)} for _, r in grouped.iterrows()]

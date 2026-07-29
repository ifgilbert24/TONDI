"""dashboard.py - Service untuk GET /api/dashboard."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews, load_metadata
from utils.stats import compute_location_stats
import pandas as pd

def get_dashboard_stats():
    reviews_df = load_reviews()
    metadata_df = load_metadata()
    if reviews_df.empty:
        return {"total_locations": 0, "red_status": 0, "weekly_trend": 0, "total_reviews": 0, "sentiment_distribution": {}, "topic_distribution": {}}
    total_locations = len(metadata_df) if not metadata_df.empty else reviews_df["place-name"].nunique()
    stats = compute_location_stats(reviews_df)
    red_status = int((stats["status"] == "red").sum()) if not stats.empty else 0
    
    # Weekly trend: bandingkan jumlah negatif 7 hari terakhir vs 7 hari sebelumnya
    weekly_trend = 0
    if "collect-date" in reviews_df.columns:
        df = reviews_df.copy()
        df["collect-date"] = pd.to_datetime(df["collect-date"], errors="coerce")
        df = df.dropna(subset=["collect-date"])
        if len(df) > 0:
            max_date = df["collect-date"].max()
            curr = df[df["collect-date"] >= (max_date - pd.Timedelta(days=7))]
            prev = df[(df["collect-date"] >= (max_date - pd.Timedelta(days=14))) & (df["collect-date"] < (max_date - pd.Timedelta(days=7)))]
            curr_neg = int((curr["sentiment"] == "Negatif").sum()) if len(curr) > 0 else 0
            prev_neg = int((prev["sentiment"] == "Negatif").sum()) if len(prev) > 0 else 0
            if prev_neg > 0:
                weekly_trend = int(((curr_neg - prev_neg) / prev_neg) * 100)
            elif curr_neg > 0:
                weekly_trend = 100
            # else: both 0 -> weekly_trend stays 0
    
    sent_dist = {str(k): int(v) for k, v in reviews_df["sentiment"].value_counts().to_dict().items()}
    top_dist = {str(k): int(v) for k, v in reviews_df["topic"].value_counts().to_dict().items()}
    return {"total_locations": int(total_locations), "red_status": red_status, "weekly_trend": weekly_trend, "total_reviews": len(reviews_df), "sentiment_distribution": sent_dist, "topic_distribution": top_dist}

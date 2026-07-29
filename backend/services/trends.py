"""trends.py - Service untuk data time-series."""
import sys, os, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews

def get_review_trends(days=7):
    reviews_df = load_reviews()
    if reviews_df.empty or "collect-date" not in reviews_df.columns: return _fallback(reviews_df)
    df = reviews_df.copy()
    df["collect-date"] = pd.to_datetime(df["collect-date"], errors="coerce")
    df = df.dropna(subset=["collect-date"])
    if df.empty: return _fallback(reviews_df)
    max_date = df["collect-date"].max(); min_date = max_date - pd.Timedelta(days=days)
    df = df[df["collect-date"] >= min_date]
    if df.empty: return _fallback(reviews_df)
    df["date"] = df["collect-date"].dt.date
    t = df.groupby("date").agg(total=("sentiment","count"), positif=("sentiment",lambda x:(x=="Positif").sum()), netral=("sentiment",lambda x:(x=="Netral").sum()), negatif=("sentiment",lambda x:(x=="Negatif").sum())).reset_index().sort_values("date")
    day_names = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    return [{"date": str(r["date"]), "day": day_names[r["date"].weekday()], "total": int(r["total"]), "positif": int(r["positif"]), "netral": int(r["netral"]), "negatif": int(r["negatif"])} for _, r in t.iterrows()]

def _fallback(reviews_df):
    if reviews_df.empty: return []
    s = reviews_df["sentiment"].value_counts()
    return [{"date":"-", "day":"Total", "total": int(s.sum()), "positif": int(s.get("Positif",0)), "netral": int(s.get("Netral",0)), "negatif": int(s.get("Negatif",0))}]

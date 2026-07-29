"""reviews.py - Service untuk review."""
import sys, os, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews

def get_reviews(location=None, sentiment=None, topic=None, limit=50):
    df = load_reviews()
    if df.empty: return []
    df = df.copy()
    if location: df = df[df["place-name"].str.contains(location, case=False, na=False)]
    if sentiment and sentiment.lower()!="semua": df = df[df["sentiment"].str.lower()==sentiment.lower()]
    if topic and topic.lower()!="semua": df = df[df["topic"].str.lower()==topic.lower()]
    df = df.dropna(subset=["review-text"]).sort_values("published-at", ascending=False).head(limit)
    return [{"id": int(r.name), "location": str(r.get("place-name","")), "author": str(r.get("name","")), "rating": float(r["reviewer-rating"]) if not pd.isna(r.get("reviewer-rating")) else None, "text": str(r.get("review-text","")), "sentiment": str(r.get("sentiment","")), "topic": str(r.get("topic","")), "date": str(r.get("published-at",""))} for _, r in df.iterrows()]

def get_filter_options():
    df = load_reviews()
    if df.empty: return {"locations":[],"sentiments":[],"topics":[]}
    return {"locations": sorted(df["place-name"].dropna().unique().tolist()), "sentiments": sorted(df["sentiment"].dropna().unique().tolist()), "topics": sorted(df["topic"].dropna().unique().tolist())}

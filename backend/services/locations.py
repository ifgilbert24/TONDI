"""locations.py - Service untuk data lokasi. (Optimized: uses cached metadata + fuzzy matching)"""
import sys, os, re, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews, load_metadata
from utils.stats import compute_location_stats
from services.priorities import compute_priority_score, get_priority_status_en

def _fuzzy_match(name, meta_dict):
    """Cari nama di metadata dengan fuzzy matching jika exact match gagal."""
    if name in meta_dict:
        return meta_dict[name]
    # Normalize both for comparison
    def norm(n):
        n = n.lower().replace('-', ' ').replace('.', '').strip()
        n = re.sub(r'[^a-z0-9 ]', '', n)
        return re.sub(r' +', ' ', n).strip()
    nn = norm(name)
    for mname, minfo in meta_dict.items():
        mn = norm(mname)
        # Check if one contains the other
        if nn in mn or mn in nn:
            return minfo
        # Check word overlap > 50%
        nwords = set(nn.split())
        mwords = set(mn.split())
        common = nwords & mwords
        if len(common) > 0 and len(common) / max(len(nwords), len(mwords)) >= 0.5:
            return minfo
    return {}

def _build_meta_dict(metadata_df):
    """Build dict dari metadata DataFrame."""
    meta_dict = {}
    if not metadata_df.empty:
        for _, r in metadata_df.iterrows():
            meta_dict[r["place_name"]] = {
                "lat": r["latitude"],
                "lng": r["longitude"],
                "category": r["category"],
                "region": r.get("region"),
            }
    return meta_dict

def get_all_locations(region=None, topic=None):
    """Daftar lokasi + koordinat + statistik. Mendukung filter region & topic."""
    reviews_df = load_reviews()
    metadata_df = load_metadata()
    stats = compute_location_stats(reviews_df)
    
    # Compute priority score FIRST for consistent status (same scores regardless of topic filter)
    stats = compute_priority_score(stats)
    
    # If topic filter, only include locations that have reviews with that topic
    if topic and topic != "Semua Isu":
        locs_with_topic = set(reviews_df[reviews_df["topic"] == topic]["place-name"].unique())
        stats = stats[stats["place-name"].isin(locs_with_topic)]
    
    meta_dict = _build_meta_dict(metadata_df)

    locations = []
    for _, r in stats.iterrows():
        name = r["place-name"]
        info = _fuzzy_match(name, meta_dict)
        loc_region = info.get("region")
        
        if region and loc_region != region:
            continue
            
        loc = {
            "name": name,
            "total_reviews": int(r["total_reviews"]),
            "rating": float(r["rating_mean"]) if not pd.isna(r["rating_mean"]) else None,
            "positif": int(r["positif"]),
            "netral": int(r["netral"]),
            "negatif": int(r["negatif"]),
            "z_score": float(r["z_score"]),
            "priority_score": round(float(r["priority_score"]), 1),
            "status": get_priority_status_en(r["priority_score"]),
            "region": loc_region,
            "latitude": info.get("lat"),
            "longitude": info.get("lng"),
        }
        locations.append(loc)
    return {"locations": locations, "total": len(locations)}


def get_location_detail(location_name):
    """Detail satu lokasi."""
    reviews_df = load_reviews()
    metadata_df = load_metadata()
    
    location_reviews = reviews_df[reviews_df["place-name"] == location_name]
    if location_reviews.empty:
        return None

    # Dapatkan metadata dari cache dengan fuzzy matching
    meta_dict = _build_meta_dict(metadata_df)
    info = _fuzzy_match(location_name, meta_dict)
    coord = {"lat": info["lat"], "lng": info["lng"]} if info.get("lat") else None
    category = info.get("category")

    stats = compute_location_stats(reviews_df)
    loc_stats = stats[stats["place-name"] == location_name]
    if loc_stats.empty:
        return None
    
    r = loc_stats.iloc[0]
    topic_dist = {str(k): int(v) for k, v in location_reviews["topic"].value_counts().to_dict().items()}
    sent_dist = {str(k): int(v) for k, v in location_reviews["sentiment"].value_counts().to_dict().items()}
    
    recent = location_reviews.sort_values("collect-date", ascending=False).head(10)
    review_list = []
    for _, x in recent.iterrows():
        review_list.append({
            "author": str(x.get("name", "")),
            "rating": float(x["reviewer-rating"]) if not pd.isna(x.get("reviewer-rating")) else None,
            "text": str(x.get("review-text", "")),
            "sentiment": x["sentiment"],
            "topic": x["topic"],
            "date": str(x.get("published-at", "")),
        })

    # Plus reviews grouped by topic for recommendation support
    by_topic = {}
    for t in location_reviews["topic"].unique():
        subset = location_reviews[location_reviews["topic"] == t].sort_values("collect-date", ascending=False).head(3)
        by_topic[str(t)] = [{
            "text": str(x.get("review-text", "")),
            "sentiment": str(x["sentiment"]),
            "rating": float(x["reviewer-rating"]) if not pd.isna(x.get("reviewer-rating")) else None,
        } for _, x in subset.iterrows()]

    return {
        "name": location_name,
        "category": category,
        "coordinate": coord,
        "total_reviews": int(r["total_reviews"]),
        "rating": float(r["rating_mean"]) if not pd.isna(r["rating_mean"]) else None,
        "positif": int(r["positif"]),
        "netral": int(r["netral"]),
        "negatif": int(r["negatif"]),
        "z_score": float(r["z_score"]),
        "status": r["status"],
        "topic_distribution": topic_dist,
        "sentiment_distribution": sent_dist,
        "recent_reviews": review_list,
        "reviews_by_topic": by_topic,
    }

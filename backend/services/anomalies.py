"""anomalies.py - Deteksi anomaly location."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews
from utils.stats import compute_location_stats

def get_anomalies(threshold=2.0):
    reviews_df = load_reviews()
    if reviews_df.empty: return []
    stats = compute_location_stats(reviews_df, min_reviews=5)
    if stats.empty: return []
    anomalies = stats[stats["z_score"] > threshold].sort_values("z_score", ascending=False)
    def get_top_topic(loc_name):
        neg = reviews_df[(reviews_df["place-name"]==loc_name)&(reviews_df["sentiment"]=="Negatif")]
        if len(neg)==0: return "-"
        topics = neg["topic"].value_counts()
        return topics.index[0] if len(topics)>0 else "-"
    results = []
    for _, r in anomalies.iterrows():
        surge = int((r["z_score"]/threshold-1)*100)
        issue = get_top_topic(r["place-name"])
        if r["z_score"] > 3.0: status, color = "Kritis", "bg-red-500"
        elif r["z_score"] > 2.5: status, color = "Tinggi", "bg-orange-500"
        else: status, color = "Menengah", "bg-amber-400"
        results.append({"location": r["place-name"], "z_score": round(r["z_score"], 2), "negative_ratio": round(r["negatif_ratio"], 4), "total_reviews": int(r["total_reviews"]), "negative_count": int(r["negatif"]), "issue": issue, "surge": f"+{surge}%", "status": status, "color": color})
    return results

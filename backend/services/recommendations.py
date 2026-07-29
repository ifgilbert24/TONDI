"""recommendations.py - Rekomendasi otomatis berdasarkan data lokasi."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_reviews
from utils.stats import compute_location_stats
import pandas as pd

# Static lookup table untuk rekomendasi per topik
_TOPIC_ACTIONS = {
    "Kebersihan": "Tingkatkan jadwal pembersihan dan penyediaan tempat sampah",
    "Pungli": "Lakukan inspeksi parkir liar dan koordinasi dengan Satgas Saber Pungli",
    "Harga": "Evaluasi kembali tarif tiket masuk dan parkir",
    "Layanan": "Adakan pelatihan service excellence untuk petugas",
    "Fasilitas": "Lakukan perbaikan fasilitas umum (toilet, mushola, gazebo)",
    "Akses": "Koordinasi dengan Dinas PU untuk perbaikan akses jalan",
    "Parkir": "Perluas area parkir dan perbaiki manajemen parkir",
    "Keamanan": "Tambahkan penerangan dan pos jaga keamanan",
}

def get_location_recommendations(location_name):
    """Hasilkan rekomendasi tindakan untuk suatu lokasi."""
    reviews_df = load_reviews()
    loc_reviews = reviews_df[reviews_df["place-name"] == location_name]
    if loc_reviews.empty:
        return []

    stats = compute_location_stats(reviews_df, min_reviews=3)
    loc_stats = stats[stats["place-name"] == location_name]
    total = len(loc_reviews)
    negatif = int((loc_reviews["sentiment"] == "Negatif").sum())
    positif = int((loc_reviews["sentiment"] == "Positif").sum())
    rating_avg = loc_reviews["reviewer-rating"].mean()
    
    neg_reviews = loc_reviews[loc_reviews["sentiment"] == "Negatif"]
    top_topics = neg_reviews["topic"].value_counts() if len(neg_reviews) > 0 else pd.Series()

    recs = []

    # 1. Berdasarkan topik dominan
    for topic, count in top_topics.head(2).items():
        if topic in _TOPIC_ACTIONS:
            pct = int(count / max(negatif, 1) * 100)
            recs.append({
                "action": _TOPIC_ACTIONS[topic],
                "reason": f"{count} dari {negatif} keluhan ({pct}%) terkait {topic.lower()}",
                "priority": "Tinggi" if pct > 40 else "Sedang",
                "topic": topic,
            })

    # 2. Anomaly
    if not loc_stats.empty:
        z = float(loc_stats.iloc[0]["z_score"])
        if z > 2.0:
            recs.append({
                "action": "Lakukan investigasi mendadak dan audit lapangan",
                "reason": f"Lokasi terdeteksi anomali (Z-Score: {z:.2f})",
                "priority": "Kritis",
            })

    # 3. Rating rendah
    if not pd.isna(rating_avg) and rating_avg < 3.0:
        recs.append({
            "action": "Survei kepuasan pengunjung untuk identifikasi akar masalah",
            "reason": f"Rating rata-rata {rating_avg:.1f}/5",
            "priority": "Tinggi",
        })

    # 4. Fallback: tidak ada masalah
    if len(recs) == 0:
        recs.append({
            "action": "Pertahankan kualitas pelayanan yang sudah baik",
            "reason": f"Tidak ada keluhan dominan. {positif} positif dari {total} review",
            "priority": "Rendah",
        })

    return recs

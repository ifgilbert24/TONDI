"""
pipeline.py
Pipeline terintegrasi TONDI.

Alur:
Raw Review + Lokasi
  -> Preprocessing (clean_review)
  -> Prediksi Sentimen + Topik (TF-IDF + Logistic Regression)
  -> Deteksi Anomali (Z-Score per lokasi)
  -> Output JSON
"""

import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "models"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "preprocessing"))

from predict import predict_review
from anomaly_detection import _group_by_location, _hitung_zscore



def _precompute_anomaly(data_path="dataset/processed/review_labeled.xlsx", threshold=2.0):
    if not os.path.exists(data_path):
        print("Warning: Dataset tidak ditemukan:", data_path)
        return {}
    df = pd.read_excel(data_path)
    grouped = _group_by_location(df)
    grouped["z_score"] = _hitung_zscore(grouped["negatif_ratio"])
    anomaly_map = {}
    for _, row in grouped.iterrows():
        loc = row["place-name"]
        anomaly_map[loc] = {
            "anomaly": bool(row["z_score"] > threshold),
            "z_score": round(row["z_score"], 2),
            "negative_ratio": round(row["negatif_ratio"], 4),
            "total_reviews": int(row["total_review"]),
            "negative_count": int(row["negatif"]),
        }
    return anomaly_map


def process_single_review(review_text, location=None, anomaly_map=None):
    pred = predict_review(review_text)
    avg_conf = (pred.get("confidence_sentiment", 0) + pred.get("confidence_topic", 0)) / 2
    result = {
        "review": review_text[:200],
        "sentiment": pred["sentiment"],
        "topic": pred["topic"],
        "confidence": round(avg_conf, 4),
        "anomaly": False,
    }
    if location and anomaly_map and location in anomaly_map:
        result["anomaly"] = anomaly_map[location]["anomaly"]
        result["anomaly_info"] = {
            "z_score": anomaly_map[location]["z_score"],
            "negative_ratio": anomaly_map[location]["negative_ratio"],
            "total_reviews": anomaly_map[location]["total_reviews"],
        }
    if location:
        result["location"] = location
    return result


def process_batch(data_path="dataset/processed/review_labeled.xlsx", limit=None):
    print("Memuat dataset...")
    df = pd.read_excel(data_path)
    if limit:
        df = df.head(limit)
    print("Total review:", len(df))
    print()
    anomaly_map = _precompute_anomaly(data_path)
    results = []
    for i, (_, row) in enumerate(df.iterrows()):
        review_text = str(row.get("review-text", ""))
        location = str(row.get("place-name", ""))
        if not review_text or review_text == "nan":
            continue
        result = process_single_review(review_text, location, anomaly_map)
        results.append(result)
        if (i + 1) % 100 == 0:
            print("  Progress:", i+1, "/", len(df))
    print()
    print("Selesai! Total output:", len(results))
    print()
    return results


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline TONDI")
    parser.add_argument("--review", type=str, help="Proses satu review")
    parser.add_argument("--location", type=str, default=None, help="Nama lokasi")
    parser.add_argument("--batch", action="store_true", help="Proses batch dataset")
    parser.add_argument("--limit", type=int, default=None, help="Batasan review")
    parser.add_argument("--data", type=str, default="dataset/processed/review_labeled.xlsx", help="Path dataset")
    args = parser.parse_args()

    if args.review:
        print("=" * 60)
        print("PIPELINE SINGLE REVIEW")
        print("=" * 60)
        print()
        anomaly_map = _precompute_anomaly(args.data)
        result = process_single_review(args.review, args.location, anomaly_map)
        print_json(result)
    elif args.batch:
        print("=" * 60)
        print("PIPELINE BATCH")
        print("=" * 60)
        print()
        results = process_batch(args.data, args.limit)
        output_path = os.path.join("dataset", "processed", "pipeline_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Output disimpan ke:", output_path)
        print()
        print("Sample output (5 review pertama):")
        for r in results[:5]:
            print_json(r)
            print()
    else:
        print("=" * 60)
        print("PIPELINE TONDI - DEMO")
        print("=" * 60)
        print()
        anomaly_map = _precompute_anomaly(args.data)
        demos = [
            ("pantainya bersih dan indah sekali, recommended!", "Parapat"),
            ("banyak sampah berserakan, baunya tidak sedap", "Parapat"),
            ("tiket masuk mahal, parkir juga mahal", "Bukit Holbung Samosir"),
            ("pelayanan ramah dan petugas membantu", "Geosite Sipinsur"),
            ("gelap tidak ada lampu, tidak aman", "Tomok"),
        ]
        for review_text, location in demos:
            result = process_single_review(review_text, location, anomaly_map)
            print_json(result)
            print()
        print("Gunakan --review untuk single, --batch untuk batch.")


if __name__ == "__main__":
    main()

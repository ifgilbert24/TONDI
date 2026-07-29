"""
anomaly_detection.py
Deteksi anomali keluhan berdasarkan data review.

Algoritma:
1. Z-Score (prioritas utama)
2. Isolation Forest (tambahan)

Input : dataset/processed/review_labeled.xlsx
Output: tabel anomali + JSON per lokasi
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def _group_by_location(df, min_review=5):
    """Helper: kelompokkan review per lokasi."""
    grouped = df.groupby("place-name").agg(
        total_review=("sentiment", "count"),
        negatif=("sentiment", lambda x: (x == "Negatif").sum())
    ).reset_index()
    grouped = grouped[grouped["total_review"] >= min_review].copy()
    grouped["negatif_ratio"] = grouped["negatif"] / grouped["total_review"]
    return grouped


def _hitung_zscore(data):
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return [0] * len(data)
    return [(x - mean) / std for x in data]


def _to_json_rows(df, method, tanggal=None):
    """Konversi DataFrame hasil deteksi ke format JSON list."""
    rows = []
    for _, row in df.iterrows():
        entry = {
            "location": row["place-name"],
            "negative_ratio": round(row["negatif_ratio"], 4),
            "status": row["status"]
        }
        if tanggal is not None:
            entry["date"] = str(row["tanggal"])
        if "z_score" in df.columns:
            entry["z_score"] = round(row["z_score"], 2)
        elif "anomaly_score" in df.columns:
            entry["anomaly_score"] = round(row["anomaly_score"], 2)
        rows.append(entry)
    return rows



def deteksi_anomali_zscore(df, threshold=2.0):
    """
    Deteksi anomali menggunakan Z-Score pada negative ratio.
    
    Returns
    -------
    DataFrame, list[dict]
        Hasil deteksi dan JSON output
    """
    print("=" * 60)
    print("DETEKSI ANOMALI - Z-SCORE")
    print("=" * 60)

    grouped = _group_by_location(df)
    grouped["z_score"] = _hitung_zscore(grouped["negatif_ratio"])
    grouped["status"] = grouped["z_score"].apply(
        lambda z: "ANOMALY" if z > threshold else "NORMAL"
    )
    grouped = grouped.sort_values("z_score", ascending=False).reset_index(drop=True)
    grouped["no"] = range(1, len(grouped) + 1)

    anomali = grouped[grouped["status"] == "ANOMALY"]
    print("Threshold Z-Score:", threshold)
    print("Total lokasi dianalisis:", len(grouped))
    print("Lokasi dengan anomali:", len(anomali))
    print()

    if len(anomali) > 0:
        print("{:>3} {:<40} {:>7} {:>6} {:>7} {:>8} {:>10}".format(
            "No", "Lokasi", "Negatif", "Total", "Ratio", "Z-Score", "Status"))
        print("-" * 85)
        for _, row in anomali.iterrows():
            print("{:>3} {:<40} {:>7} {:>6} {:.3f}  {:>+7.2f}  {:>10}".format(
                row["no"], str(row["place-name"])[:38],
                row["negatif"], row["total_review"],
                row["negatif_ratio"], row["z_score"], row["status"]))
    else:
        print("Tidak ada anomali terdeteksi.")
    print()
    
    # JSON output
    json_rows = _to_json_rows(grouped, "zscore")
    print("JSON Output:")
    print(json.dumps(json_rows, indent=2, ensure_ascii=False))
    print()

    result_cols = ["place-name", "total_review", "negatif", "negatif_ratio", "z_score", "status"]
    return grouped[result_cols], json_rows


def deteksi_anomali_isolation_forest(df, contamination=0.1):
    """
    Deteksi anomali menggunakan Isolation Forest.
    
    Returns
    -------
    DataFrame, list[dict]
        Hasil deteksi dan JSON output
    """
    print("=" * 60)
    print("DETEKSI ANOMALI - ISOLATION FOREST")
    print("=" * 60)

    grouped = _group_by_location(df)
    features = grouped[["total_review", "negatif", "negatif_ratio"]].values

    model = IsolationForest(contamination=contamination, random_state=42)
    pred = model.fit_predict(features)
    scores = model.score_samples(features)

    grouped["anomaly_score"] = scores
    grouped["status"] = pred
    grouped["status"] = grouped["status"].apply(
        lambda x: "ANOMALY" if x == -1 else "NORMAL"
    )
    grouped = grouped.sort_values("anomaly_score").reset_index(drop=True)
    grouped["no"] = range(1, len(grouped) + 1)

    anomali = grouped[grouped["status"] == "ANOMALY"]
    print("Contamination:", contamination)
    print("Total lokasi dianalisis:", len(grouped))
    print("Lokasi dengan anomali:", len(anomali))
    print()

    if len(anomali) > 0:
        print("{:>3} {:<40} {:>7} {:>6} {:>7} {:>8} {:>10}".format(
            "No", "Lokasi", "Negatif", "Total", "Ratio", "Score", "Status"))
        print("-" * 85)
        for _, row in anomali.iterrows():
            print("{:>3} {:<40} {:>7} {:>6} {:.3f}  {:>+8.2f}  {:>10}".format(
                row["no"], str(row["place-name"])[:38],
                row["negatif"], row["total_review"],
                row["negatif_ratio"], row["anomaly_score"], row["status"]))
    else:
        print("Tidak ada anomali terdeteksi.")
    print()
    
    json_rows = _to_json_rows(grouped, "isolation_forest")
    print("JSON Output:")
    print(json.dumps(json_rows, indent=2, ensure_ascii=False))
    print()

    result_cols = ["place-name", "total_review", "negatif", "negatif_ratio", "anomaly_score", "status"]
    return grouped[result_cols], json_rows


def deteksi_per_lokasi_tanggal(df, threshold=2.0):
    """
    Deteksi anomali per lokasi per tanggal menggunakan Z-Score.
    """
    print("=" * 60)
    print("DETEKSI ANOMALI PER LOKASI PER TANGGAL")
    print("=" * 60)

    if "collect-date" not in df.columns:
        print("Kolom collect-date tidak ditemukan.")
        print()
        return pd.DataFrame(), []

    df_copy = df.copy()
    df_copy["tanggal"] = pd.to_datetime(df_copy["collect-date"]).dt.date
    
    grouped = df_copy.groupby(["place-name", "tanggal"]).agg(
        total_review=("sentiment", "count"),
        negatif=("sentiment", lambda x: (x == "Negatif").sum())
    ).reset_index()
    grouped = grouped[grouped["total_review"] >= 3].copy()
    grouped["negatif_ratio"] = grouped["negatif"] / grouped["total_review"]
    grouped["z_score"] = _hitung_zscore(grouped["negatif_ratio"])
    grouped["status"] = grouped["z_score"].apply(
        lambda z: "ANOMALY" if z > threshold else "NORMAL"
    )
    grouped = grouped.sort_values("z_score", ascending=False).reset_index(drop=True)

    anomali = grouped[grouped["status"] == "ANOMALY"]
    print("Total grup (lokasi x tanggal):", len(grouped))
    print("Grup dengan anomali:", len(anomali))
    print()

    if len(anomali) > 0:
        print("{:>3} {:<35} {:<12} {:>7} {:>6} {:>8} {:>10}".format(
            "No", "Lokasi", "Tanggal", "Ratio", "Total", "Z-Score", "Status"))
        print("-" * 85)
        for i, (_, row) in enumerate(anomali.head(15).iterrows(), 1):
            print("{:>3} {:<35} {:<12} {:.3f}  {:>6} {:>+8.2f}  {:>10}".format(
                i, str(row["place-name"])[:35], str(row["tanggal"]),
                row["negatif_ratio"], row["total_review"],
                row["z_score"], row["status"]))
    else:
        print("Tidak ada anomali.")
    print()
    
    json_rows = _to_json_rows(grouped, "zscore", tanggal=True)
    print("JSON Output:")
    print(json.dumps(json_rows, indent=2, ensure_ascii=False))
    print()

    return grouped, json_rows


def main():
    data_path = os.path.join("dataset", "processed", "review_labeled.xlsx")
    print("Memuat dataset...")
    df = pd.read_excel(data_path)
    print("Total data:", len(df), "baris")
    print()

    deteksi_anomali_zscore(df, threshold=2.0)
    print()
    deteksi_anomali_isolation_forest(df, contamination=0.1)
    print()
    deteksi_per_lokasi_tanggal(df, threshold=2.0)

    print("=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()

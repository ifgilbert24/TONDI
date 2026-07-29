"""
run_labeling.py
Menjalankan pelabelan sentimen dan topik pada dataset review yang sudah dibersihkan.

Input : dataset/processed/review_clean.xlsx
Output: dataset/processed/review_labeled.xlsx
"""

import sys
import os

# Tambah path agar bisa import labeling
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from labeling import label_sentimen, label_topik


def label_dataset(input_path, output_path):
    """
    Membaca dataset, memberi label sentimen dan topik, lalu menyimpan hasil.
    """
    print("Membaca dataset:", input_path)
    df = pd.read_excel(input_path)
    print("Jumlah data:", len(df), "baris")
    
    kolom = "review_clean"
    if kolom not in df.columns:
        print("Error: Kolom", kolom, "tidak ditemukan!")
        return
    
    # Isi nilai kosong
    df[kolom] = df[kolom].fillna("")
    
    # Jalankan pelabelan
    print("Memberi label sentimen...")
    df["sentiment"] = df[kolom].apply(label_sentimen)
    
    print("Memberi label topik...")
    df["topic"] = df[kolom].apply(label_topik)
    
    # Statistik
    print()
    print("=" * 50)
    print("STATISTIK SENTIMEN")
    print("=" * 50)
    sentimen_counts = df["sentiment"].value_counts()
    for label, count in sentimen_counts.items():
        pct = count / len(df) * 100
        print(f"  {label:10}: {count:6} ({pct:.1f}%)")
    
    print()
    print("=" * 50)
    print("STATISTIK TOPIK")
    print("=" * 50)
    topik_counts = df["topic"].value_counts()
    for label, count in topik_counts.items():
        pct = count / len(df) * 100
        print(f"  {label:15}: {count:6} ({pct:.1f}%)")
    
    # Simpan hasil
    print()
    print("Menyimpan hasil ke:", output_path)
    df.to_excel(output_path, index=False)
    print("Selesai!")
    
    # Contoh hasil
    print()
    print("Contoh hasil (5 baris pertama):")
    for i in range(min(5, len(df))):
        review = str(df[kolom].iloc[i])[:60]
        sentimen = df["sentiment"].iloc[i]
        topik = df["topic"].iloc[i]
        print(f"  {i+1}. {review:60} | {sentimen:8} | {topik}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    input_path = os.path.join(project_root, "dataset", "processed", "review_clean.xlsx")
    output_path = os.path.join(project_root, "dataset", "processed", "review_labeled.xlsx")
    
    label_dataset(input_path, output_path)

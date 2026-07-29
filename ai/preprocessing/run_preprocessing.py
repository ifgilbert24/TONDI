"""
run_preprocessing.py
Menjalankan pipeline pembersihan teks pada dataset ulasan.

Input : dataset/processed/review.xlsx
Output: dataset/processed/review_clean.xlsx
"""

import sys
import os
# Tambah path agar bisa import clean_review
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from clean_review import clean_review, tokenize

def preprocess_dataset(input_path, output_path):
    print("Membaca dataset:", input_path)
    df = pd.read_excel(input_path)
    print("Jumlah data:", len(df), "baris")
    print("Kolom:", list(df.columns))
    
    kolom_review = "review-text"
    if kolom_review not in df.columns:
        print("Error: Kolom", kolom_review, "tidak ditemukan!")
        return
    
    review_kosong = df[kolom_review].isnull().sum()
    print("Review kosong:", review_kosong)
    df[kolom_review] = df[kolom_review].fillna("")
    
    print("Menjalankan preprocessing...")
    df["review_clean"] = df[kolom_review].apply(clean_review)
    df["review_tokens"] = df["review_clean"].apply(tokenize)
    
    total_char_sebelum = df[kolom_review].str.len().sum()
    total_char_sesudah = df["review_clean"].str.len().sum()
    print("Total karakter sebelum:", total_char_sebelum)
    print("Total karakter sesudah :", total_char_sesudah)
    print("Reduksi: {:.1f}%".format((1 - total_char_sesudah/total_char_sebelum)*100 if total_char_sebelum > 0 else 0))
    
    print("Menyimpan hasil ke:", output_path)
    df.to_excel(output_path, index=False)
    print("Selesai!")
    
    print("\nContoh hasil preprocessing (3 baris pertama):")
    for i in range(min(3, len(df))):
        print("\nBaris", i+1, ":")
        sebelum = str(df[kolom_review].iloc[i])[:100]
        sesudah = str(df["review_clean"].iloc[i])[:100]
        token_list = df["review_tokens"].iloc[i][:10]
        print("  Sebelum :", sebelum)
        print("  Sesudah :", sesudah)
        print("  Token   :", token_list)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    input_path = os.path.join(project_root, "dataset", "processed", "review.xlsx")
    output_path = os.path.join(project_root, "dataset", "processed", "review_clean.xlsx")
    preprocess_dataset(input_path, output_path)

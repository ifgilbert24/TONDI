"""
evaluate_model.py
Evaluasi model baseline NLP: metrik, confusion matrix, analisis error.
"""

import os
import sys
import io
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix


def main():
    # Fix UnicodeEncodeError on Windows console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    elif hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    data_path = os.path.join("dataset", "processed", "review_labeled.xlsx")
    model_dir = os.path.join("ai", "models")
    print("=" * 60)
    print("EVALUASI MODEL BASELINE NLP")
    print("=" * 60)
    print()
    print("Memuat dataset...")
    df = pd.read_excel(data_path)
    df = df.dropna(subset=["review_clean"])
    df = df[df["review_clean"].str.strip() != ""]
    print("Total data valid:", len(df))
    print()
    with open(os.path.join(model_dir, "pipeline_sentiment.pkl"), "rb") as f:
        pipeline_sent = pickle.load(f)
    with open(os.path.join(model_dir, "pipeline_topic.pkl"), "rb") as f:
        pipeline_top = pickle.load(f)
    X = df["review_clean"]
    y_sentiment = df["sentiment"]
    y_topic = df["topic"]
    X_train, X_test, y_sent_train, y_sent_test, y_top_train, y_top_test = train_test_split(
        X, y_sentiment, y_topic, test_size=0.2, random_state=42, stratify=y_sentiment
    )
    # Pipeline langsung menerima teks bersih — TF-IDF transform internal
    y_sent_pred = pipeline_sent.predict(X_test)
    y_top_pred = pipeline_top.predict(X_test)
    sent_labels = sorted(y_sentiment.unique())
    top_labels = sorted(y_topic.unique())

    # ========== SENTIMEN ==========
    print("=" * 60)
    print("EVALUASI SENTIMEN")
    print("=" * 60)
    print()
    
    sent_acc = accuracy_score(y_sent_test, y_sent_pred)
    sent_prec = precision_score(y_sent_test, y_sent_pred, average="weighted")
    sent_rec = recall_score(y_sent_test, y_sent_pred, average="weighted")
    sent_f1 = f1_score(y_sent_test, y_sent_pred, average="weighted")
    
    print("Accuracy :", round(sent_acc, 4))
    print("Precision:", round(sent_prec, 4))
    print("Recall   :", round(sent_rec, 4))
    print("F1-Score :", round(sent_f1, 4))
    print()
    print("Classification Report:")
    print(classification_report(y_sent_test, y_sent_pred, labels=sent_labels))
    print()
    
    cm_sent = confusion_matrix(y_sent_test, y_sent_pred, labels=sent_labels)
    print("Confusion Matrix:")
    header = " " * 12 + " ".join(f"{l:>10}" for l in sent_labels)
    print(header)
    for i, label in enumerate(sent_labels):
        row = f"{label:>10} " + " ".join(f"{cm_sent[i][j]:>10}" for j in range(len(sent_labels)))
        print(row)
    print()

    # ========== TOPIK ==========
    print("=" * 60)
    print("EVALUASI TOPIK")
    print("=" * 60)
    print()
    
    top_acc = accuracy_score(y_top_test, y_top_pred)
    top_prec = precision_score(y_top_test, y_top_pred, average="weighted")
    top_rec = recall_score(y_top_test, y_top_pred, average="weighted")
    top_f1 = f1_score(y_top_test, y_top_pred, average="weighted")
    
    print("Accuracy :", round(top_acc, 4))
    print("Precision:", round(top_prec, 4))
    print("Recall   :", round(top_rec, 4))
    print("F1-Score :", round(top_f1, 4))
    print()
    print("Classification Report:")
    print(classification_report(y_top_test, y_top_pred, labels=top_labels))
    print()
    
    cm_top = confusion_matrix(y_top_test, y_top_pred, labels=top_labels)
    print("Confusion Matrix:")
    header = " " * 12 + " ".join(f"{l:>12}" for l in top_labels)
    print(header)
    for i, label in enumerate(top_labels):
        row = f"{label:>10} " + " ".join(f"{cm_top[i][j]:>12}" for j in range(len(top_labels)))
        print(row)
    print()

    # ========== ANALISIS ERROR SENTIMEN ==========
    print("=" * 60)
    print("ANALISIS ERROR SENTIMEN")
    print("=" * 60)
    print()
    
    eval_df = X_test.to_frame().copy()
    eval_df["sentimen_aktual"] = y_sent_test.values
    eval_df["sentimen_prediksi"] = y_sent_pred
    eval_df["topik_aktual"] = y_top_test.values
    eval_df["topik_prediksi"] = y_top_pred
    eval_df["sentimen_benar"] = y_sent_test.values == y_sent_pred
    eval_df["topik_benar"] = y_top_test.values == y_top_pred
    
    salah_sentimen = eval_df[~eval_df["sentimen_benar"]]
    print("Total error sentimen:", len(salah_sentimen))
    print()
    
    for aktual in sent_labels:
        contoh = salah_sentimen[salah_sentimen["sentimen_aktual"] == aktual]
        if len(contoh) > 0:
            print("---", aktual, "diklasifikasikan sebagai ---")
            for pred_label in sent_labels:
                if pred_label == aktual:
                    continue
                sub = contoh[contoh["sentimen_prediksi"] == pred_label]
                if len(sub) > 0:
                    print("  Prediksi", pred_label, ":", len(sub), "data")
                    for idx, row in sub.head(3).iterrows():
                        txt = str(row["review_clean"])
                        if len(txt) > 80:
                            txt = txt[:80] + "..."
                        print(f'    - "{txt}"')
                    print()
    print()

    # ========== ANALISIS ERROR TOPIK ==========
    print("=" * 60)
    print("ANALISIS ERROR TOPIK")
    print("=" * 60)
    print()
    
    salah_topik = eval_df[~eval_df["topik_benar"]]
    print("Total error topik:", len(salah_topik))
    print()
    
    for aktual in top_labels:
        contoh = salah_topik[salah_topik["topik_aktual"] == aktual]
        if len(contoh) > 0:
            print("---", aktual, "diklasifikasikan sebagai ---")
            dist = contoh["topik_prediksi"].value_counts()
            for pred_label, count in dist.items():
                if pred_label == aktual:
                    continue
                print(" ", pred_label, ":", count, "data")
                sub = contoh[contoh["topik_prediksi"] == pred_label]
                for idx, row in sub.head(2).iterrows():
                    txt = str(row["review_clean"])
                    if len(txt) > 80:
                        txt = txt[:80] + "..."
                    print(f'    - "{txt}"')
                print()
    print()

    # ========== IRONI / SARKASME ==========
    print("=" * 60)
    print("ANALISIS REVIEW AMBIGU / IRONI / SARKASME")
    print("=" * 60)
    print()
    
    print("--- Review Negatif diprediksi Positif (kemungkinan ironi/sarkasme) ---")
    ironi = eval_df[(eval_df["sentimen_aktual"] == "Negatif") & (eval_df["sentimen_prediksi"] == "Positif")]
    if len(ironi) > 0:
        print("Jumlah:", len(ironi))
        for idx, row in ironi.head(5).iterrows():
            txt = str(row["review_clean"])
            if len(txt) > 100:
                txt = txt[:100] + "..."
            print(f'  Review  : "{txt}"')
            print("  Aktual  :", row["sentimen_aktual"], "-> Prediksi:", row["sentimen_prediksi"])
            print("  Topik   :", row["topik_aktual"], "-> Prediksi:", row["topik_prediksi"])
            print()
    else:
        print("Tidak ditemukan.")
    print()
    
    print("--- Review Positif diprediksi Negatif ---")
    kontradiksi = eval_df[(eval_df["sentimen_aktual"] == "Positif") & (eval_df["sentimen_prediksi"] == "Negatif")]
    if len(kontradiksi) > 0:
        print("Jumlah:", len(kontradiksi))
        for idx, row in kontradiksi.head(5).iterrows():
            txt = str(row["review_clean"])
            if len(txt) > 100:
                txt = txt[:100] + "..."
            print(f'  Review  : "{txt}"')
            print("  Aktual  :", row["sentimen_aktual"], "-> Prediksi:", row["sentimen_prediksi"])
            print("  Topik   :", row["topik_aktual"], "-> Prediksi:", row["topik_prediksi"])
            print()
    else:
        print("Tidak ditemukan.")
    print()

    # Confidence rendah
    print("--- Review dengan confidence rendah (< 0.6) ---")
    probs_sent = pipeline_sent.predict_proba(X_test)
    probs_top = pipeline_top.predict_proba(X_test)
    max_probs_sent = np.max(probs_sent, axis=1)
    max_probs_top = np.max(probs_top, axis=1)
    
    found = False
    for i in range(len(X_test)):
        if max_probs_sent[i] < 0.6 or max_probs_top[i] < 0.6:
            found = True
            txt = str(X_test.iloc[i])
            if len(txt) > 100:
                txt = txt[:100] + "..."
            sent_conf = round(max_probs_sent[i], 3)
            top_conf = round(max_probs_top[i], 3)
            print(f'  Review  : "{txt}"')
            print(f"  Sentimen: {y_sent_pred[i]} (conf={sent_conf}) | Topik: {y_top_pred[i]} (conf={top_conf})")
            print()
    if not found:
        print("Tidak ada review dengan confidence rendah.")
    print()

    # ========== KESIMPULAN ==========
    print("=" * 60)
    print("KESIMPULAN EVALUASI")
    print("=" * 60)
    print()
    sent_acc_pct = round(sent_acc * 100, 2)
    sent_prec_pct = round(sent_prec * 100, 2)
    sent_rec_pct = round(sent_rec * 100, 2)
    sent_f1_pct = round(sent_f1 * 100, 2)
    top_acc_pct = round(top_acc * 100, 2)
    top_prec_pct = round(top_prec * 100, 2)
    top_rec_pct = round(top_rec * 100, 2)
    top_f1_pct = round(top_f1 * 100, 2)
    err_sent = round(len(salah_sentimen) / len(eval_df) * 100, 2) if len(eval_df) > 0 else 0
    err_top = round(len(salah_topik) / len(eval_df) * 100, 2) if len(eval_df) > 0 else 0
    print("Sentimen - Accuracy:", str(sent_acc_pct) + "% | Precision:", str(sent_prec_pct) + "% | Recall:", str(sent_rec_pct) + "% | F1:", str(sent_f1_pct) + "%")
    print("Topik    - Accuracy:", str(top_acc_pct) + "% | Precision:", str(top_prec_pct) + "% | Recall:", str(top_rec_pct) + "% | F1:", str(top_f1_pct) + "%")
    print()
    print("Total error sentimen:", len(salah_sentimen), "dari", len(eval_df), "(" + str(err_sent) + "%)")
    print("Total error topik   :", len(salah_topik), "dari", len(eval_df), "(" + str(err_top) + "%)")
    if len(ironi) > 0:
        print("Review ironi/sarkasme terdeteksi:", len(ironi))
    print()


if __name__ == "__main__":
    main()

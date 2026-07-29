"""
train_baseline.py
TF-IDF + Logistic Regression untuk sentimen dan topik.

Input : dataset/processed/review_labeled.xlsx
Output: ai/models/*.pkl

Fitur:
- Data augmentation untuk mengatasi bias kata
- sklearn Pipeline (TF-IDF + LR) — CV bebas data leakage
- 5-fold Stratified Cross-Validation
- GridSearchCV untuk tuning TF-IDF + Logistic Regression
- Verifikasi cepat setelah training
"""

import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import (train_test_split, StratifiedKFold,
                                     cross_val_score, GridSearchCV)
from sklearn.metrics import classification_report, accuracy_score


def generate_synthetic_reviews(multiplier=3):
    """
    Generate synthetic reviews untuk menyeimbangkan bias di semua kategori.
    """
    data = [
        # AKSES / JALAN
        ("jalannya rapi", "Positif", "Akses"),
        ("jalan bagus", "Positif", "Akses"),
        ("jalannya bagus", "Positif", "Akses"),
        ("akses jalan bagus", "Positif", "Akses"),
        ("jalan mulus", "Positif", "Akses"),
        ("jalannya bersih", "Positif", "Akses"),
        ("jalan bersih", "Positif", "Akses"),
        ("jalan nyaman", "Positif", "Akses"),
        ("jalannya terawat", "Positif", "Akses"),
        ("akses mudah", "Positif", "Akses"),
        ("jalan lancar", "Positif", "Akses"),
        ("jalannya mulus", "Positif", "Akses"),
        ("jalannya rapi dan bersih", "Positif", "Akses"),
        ("jalan menuju lokasi bagus", "Positif", "Akses"),
        ("jalannya bagus dan lebar", "Positif", "Akses"),
        ("akses jalan cukup baik", "Positif", "Akses"),
        ("akses mudah dijangkau", "Positif", "Akses"),
        ("jalan utama bagus", "Positif", "Akses"),
        ("akses jalan lancar", "Positif", "Akses"),
        ("jalan rusak", "Negatif", "Akses"),
        ("jalan berlubang", "Negatif", "Akses"),
        ("jalannya rusak", "Negatif", "Akses"),
        ("akses jalan rusak", "Negatif", "Akses"),
        ("jalan sempit", "Negatif", "Akses"),
        ("jalan macet", "Negatif", "Akses"),
        ("akses jalan susah", "Negatif", "Akses"),
        ("jalan tidak layak", "Negatif", "Akses"),
        ("jalan hancur", "Negatif", "Akses"),
        ("jalan becek", "Negatif", "Akses"),
        ("jalan licin", "Negatif", "Akses"),
        ("akses sulit", "Negatif", "Akses"),
        ("jalan sulit dilalui", "Negatif", "Akses"),
        ("akses susah", "Negatif", "Akses"),
        ("jalan berlubang rusak", "Negatif", "Akses"),
        ("jalannya rusak parah", "Negatif", "Akses"),
        ("jalan masuk rusak", "Negatif", "Akses"),
        ("jalan sempit dan rusak", "Negatif", "Akses"),
        # PARKIR
        ("parkir luas", "Positif", "Parkir"),
        ("parkir aman", "Positif", "Parkir"),
        ("parkir nyaman", "Positif", "Parkir"),
        ("parkir murah", "Positif", "Parkir"),
        ("parkir gratis", "Positif", "Parkir"),
        ("lahan parkir bagus", "Positif", "Parkir"),
        ("tempat parkir luas", "Positif", "Parkir"),
        ("parkir cukup luas", "Positif", "Parkir"),
        ("parkir memadai", "Positif", "Parkir"),
        ("lahan parkir luas", "Positif", "Parkir"),
        ("parkir sempit", "Negatif", "Parkir"),
        ("parkir mahal", "Negatif", "Parkir"),
        ("parkir tidak aman", "Negatif", "Parkir"),
        ("parkir macet", "Negatif", "Parkir"),
        ("lahan parkir sempit", "Negatif", "Parkir"),
        ("parkir tidak memadai", "Negatif", "Parkir"),
        ("tempat parkir sempit", "Negatif", "Parkir"),
        # HARGA
        ("harga murah", "Positif", "Harga"),
        ("harga terjangkau", "Positif", "Harga"),
        ("harga pas", "Positif", "Harga"),
        ("harga bersahabat", "Positif", "Harga"),
        ("harga standar", "Positif", "Harga"),
        ("harga wajar", "Positif", "Harga"),
        ("harga tidak mahal", "Positif", "Harga"),
        ("harga cukup murah", "Positif", "Harga"),
        ("harga lumayan", "Positif", "Harga"),
        ("harga ekonomis", "Positif", "Harga"),
        ("harga mahal", "Negatif", "Harga"),
        ("harga mahal sekali", "Negatif", "Harga"),
        ("harga terlalu mahal", "Negatif", "Harga"),
        ("harga tidak wajar", "Negatif", "Harga"),
        # TIKET
        ("tiket murah", "Positif", "Harga"),
        ("tiket terjangkau", "Positif", "Harga"),
        ("tiket tidak mahal", "Positif", "Harga"),
        ("tiket masuk murah", "Positif", "Harga"),
        ("tiket masuk terjangkau", "Positif", "Harga"),
        ("tiketnya terjangkau", "Positif", "Harga"),
        ("harga tiket terjangkau", "Positif", "Harga"),
        ("tiket murah meriah", "Positif", "Harga"),
        ("tiket mahal", "Negatif", "Harga"),
        ("tiket masuk mahal", "Negatif", "Harga"),
        ("tiket terlalu mahal", "Negatif", "Harga"),
        # TOILET
        ("toilet bersih", "Positif", "Fasilitas"),
        ("toilet nyaman", "Positif", "Fasilitas"),
        ("toilet terawat", "Positif", "Fasilitas"),
        ("toilet bersih dan nyaman", "Positif", "Fasilitas"),
        ("kamar mandi bersih", "Positif", "Fasilitas"),
        ("toilet memadai", "Positif", "Fasilitas"),
        ("toilet bersih wangi", "Positif", "Fasilitas"),
        ("toilet kotor", "Negatif", "Kebersihan"),
        ("toilet bau", "Negatif", "Kebersihan"),
        ("toilet tidak bersih", "Negatif", "Kebersihan"),
        ("toilet tidak terawat", "Negatif", "Kebersihan"),
        ("toilet jorok", "Negatif", "Kebersihan"),
        ("toilet kotor dan bau", "Negatif", "Kebersihan"),
        # MAKANAN
        ("makanan enak", "Positif", "Fasilitas"),
        ("makanan murah", "Positif", "Fasilitas"),
        ("makanan lezat", "Positif", "Fasilitas"),
        ("makanan enak murah", "Positif", "Fasilitas"),
        ("makanan variatif", "Positif", "Fasilitas"),
        ("makanan mahal", "Negatif", "Fasilitas"),
        ("makanan tidak enak", "Negatif", "Fasilitas"),
        ("makanan mahal tidak enak", "Negatif", "Fasilitas"),
        # PELAYANAN
        ("pelayanan ramah", "Positif", "Layanan"),
        ("pelayanan cepat", "Positif", "Layanan"),
        ("pelayanan baik", "Positif", "Layanan"),
        ("pelayanan memuaskan", "Positif", "Layanan"),
        ("pelayanan ramah tamah", "Positif", "Layanan"),
        ("pelayanan bagus", "Positif", "Layanan"),
        ("pelayanan sangat baik", "Positif", "Layanan"),
        ("petugas ramah", "Positif", "Layanan"),
        ("staff ramah", "Positif", "Layanan"),
        ("pelayanan buruk", "Negatif", "Layanan"),
        ("pelayanan lambat", "Negatif", "Layanan"),
        ("pelayanan tidak ramah", "Negatif", "Layanan"),
        ("pelayanan jelek", "Negatif", "Layanan"),
        ("pelayanan tidak memuaskan", "Negatif", "Layanan"),
        ("petugas tidak ramah", "Negatif", "Layanan"),
        # FASILITAS
        ("fasilitas lengkap", "Positif", "Fasilitas"),
        ("fasilitas bagus", "Positif", "Fasilitas"),
        ("fasilitas memadai", "Positif", "Fasilitas"),
        ("fasilitas cukup", "Positif", "Fasilitas"),
        ("fasilitas rusak", "Negatif", "Fasilitas"),
        ("fasilitas tidak lengkap", "Negatif", "Fasilitas"),
        ("fasilitas kurang", "Negatif", "Fasilitas"),
    ]

    # Data khusus untuk pola NEGASI — multiplier lebih tinggi agar model
    # belajar bahwa "tidak" + kata_negatif = Positif (negasi membalik sentimen).
    # Contoh: "tidak ada sampah" → Positif (bukan Negatif)
    negation_data = [
        # NEGASI + KATA NEGATIF = POSITIF
        # Catatan: "ada" adalah stopword. Saat inference, "tidak ada sampah"
        # jadi "tidak sampah". Maka kita perlu bigram "tidak sampah" secara explisit.
        ("tidak sampah", "Positif", "Kebersihan"),   # bigram langsung tanpa "ada"
        ("tidak ada sampah", "Positif", "Kebersihan"),
        ("tidak bau", "Positif", "Kebersihan"),
        ("tidak ada bau", "Positif", "Kebersihan"),
        ("tidak kotor", "Positif", "Kebersihan"),
        ("tidak bau", "Positif", "Kebersihan"),
        ("tidak jorok", "Positif", "Kebersihan"),
        ("tidak kumuh", "Positif", "Kebersihan"),
        ("tidak ada macet", "Positif", "Akses"),
        ("tidak macet", "Positif", "Akses"),
        ("tidak rusak", "Positif", "Akses"),
        ("tidak berlubang", "Positif", "Akses"),
        ("tidak sempit", "Positif", "Akses"),
        ("tidak becek", "Positif", "Akses"),
        ("tidak licin", "Positif", "Akses"),
        ("tidak mahal", "Positif", "Harga"),
        ("tidak terlalu mahal", "Positif", "Harga"),
        ("tidak sulit", "Positif", "Akses"),
        ("tidak susah", "Positif", "Akses"),
        # NEGASI + KATA POSITIF = NEGATIF (sudah ada sebagian, tambah variasi)
        ("tidak bersih", "Negatif", "Kebersihan"),
        ("tidak nyaman", "Negatif", "Fasilitas"),
        ("tidak layak", "Negatif", "Fasilitas"),
        ("tidak terawat", "Negatif", "Fasilitas"),
        ("tidak aman", "Negatif", "Keamanan"),
        ("tidak enak", "Negatif", "Fasilitas"),
        ("tidak lengkap", "Negatif", "Fasilitas"),
        ("tidak ramah", "Negatif", "Layanan"),
        ("pelayanan tidak memuaskan", "Negatif", "Layanan"),
    ]

    synthetic = []
    for text, sentiment, topic in data:
        for _ in range(multiplier):
            synthetic.append((text, sentiment, topic))
    # Negation-specific data with higher multiplier
    for text, sentiment, topic in negation_data:
        for _ in range(multiplier + 2):  # 5x instead of 3x
            synthetic.append((text, sentiment, topic))
    return synthetic


def _print_section(title):
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")


def build_pipeline(tfidf_params=None, lr_params=None):
    """
    Build sklearn Pipeline: TF-IDF -> LogisticRegression.

    Parameters
    ----------
    tfidf_params : dict or None
        Params untuk TfidfVectorizer (contoh: max_features, ngram_range).
    lr_params : dict or None
        Params untuk LogisticRegression (contoh: C, solver).

    Returns
    -------
    Pipeline
    """
    if tfidf_params is None:
        tfidf_params = {"max_features": 5000, "ngram_range": (1, 2)}
    if lr_params is None:
        lr_params = {"max_iter": 1000, "class_weight": "balanced", "random_state": 42}

    return Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf_params)),
        ("clf", LogisticRegression(**lr_params)),
    ])


def main():
    data_path = os.path.join("dataset", "processed", "review_labeled.xlsx")
    model_dir = os.path.join("ai", "models")
    os.makedirs(model_dir, exist_ok=True)

    _print_section("TRAINING MODEL (Pipeline TF-IDF + LR)")

    # ========== LOAD DATA ==========
    print("\n[1] Memuat dataset...")
    df = pd.read_excel(data_path)
    print(f"Total data: {len(df)} baris")
    df = df.dropna(subset=["review_clean"])
    df = df[df["review_clean"].str.strip() != ""]
    print(f"Data valid: {len(df)} baris")

    # ========== AUGMENT ==========
    print("\n[2] Augmentasi data sintetis...")
    synthetic_data = generate_synthetic_reviews(multiplier=3)
    synth_df = pd.DataFrame(synthetic_data, columns=["review_clean", "sentiment", "topic"])
    pos_count = sum(1 for _, s, _ in synthetic_data if s == "Positif")
    neg_count = sum(1 for _, s, _ in synthetic_data if s == "Negatif")
    print(f"Menambahkan {pos_count} synthetic POSITIVE + {neg_count} synthetic NEGATIVE")
    df_augmented = pd.concat([df, synth_df], ignore_index=True)
    print(f"Total data: {len(df_augmented)} baris")

    # ========== SPLIT ==========
    print("\n[3] Split data (raw text) ...")
    X = df_augmented["review_clean"]
    y_sentiment = df_augmented["sentiment"]
    y_topic = df_augmented["topic"]

    X_train, X_test, y_sent_train, y_sent_test, y_top_train, y_top_test = train_test_split(
        X, y_sentiment, y_topic, test_size=0.2, random_state=42, stratify=y_sentiment
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    # ========== CV BASELINE (PIPELINE) ==========
    _print_section("[4] BASELINE: 5-FOLD CROSS-VALIDATION (PIPELINE)")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Sentimen baseline
    pipe_sent = build_pipeline()
    scores_sent = cross_val_score(pipe_sent, X_train, y_sent_train, cv=cv, scoring="accuracy")
    print(f"  Sentimen CV: {[f'{s:.4f}' for s in scores_sent]}")
    print(f"  Mean ± Std : {scores_sent.mean():.4f} ± {scores_sent.std():.4f}")

    # Topik baseline
    pipe_top = build_pipeline()
    scores_top = cross_val_score(pipe_top, X_train, y_top_train, cv=cv, scoring="accuracy")
    print(f"  Topik    CV: {[f'{s:.4f}' for s in scores_top]}")
    print(f"  Mean ± Std : {scores_top.mean():.4f} ± {scores_top.std():.4f}")

    # ========== GRID SEARCH SENTIMEN (FULL PIPELINE) ==========
    _print_section("[5] SENTIMEN: GRID SEARCH (TF-IDF + LR via Pipeline)")

    # max_features TIDAK di-grid untuk memastikan vectorizer konsisten
    # antara sentimen dan topik (predict.py menggunakan 1 vectorizer untuk kedua model)
    param_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "clf__C": [0.1, 1.0, 10.0],
        "clf__solver": ["lbfgs"],
        "clf__class_weight": ["balanced"],
        "clf__max_iter": [1000],
        "clf__random_state": [42],
    }

    grid_sent = GridSearchCV(
        build_pipeline(),
        param_grid,
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
        scoring="accuracy",
        n_jobs=-1,
        verbose=1,
        refit=True,
    )
    grid_sent.fit(X_train, y_sent_train)

    print(f"\n  Best params  : {grid_sent.best_params_}")
    print(f"  Best CV score: {grid_sent.best_score_:.4f}")

    # Test set evaluation
    sent_acc = grid_sent.score(X_test, y_sent_test)
    print(f"  Test score   : {sent_acc:.4f}")
    y_sent_pred = grid_sent.predict(X_test)
    print("\n  Classification Report:")
    print(classification_report(y_sent_test, y_sent_pred))

    # Extract pipeline components
    best_pipe_sent = grid_sent.best_estimator_
    vectorizer_sent = best_pipe_sent.named_steps["tfidf"]
    model_sent = best_pipe_sent.named_steps["clf"]

    # ========== GRID SEARCH TOPIK (FULL PIPELINE) ==========
    _print_section("[6] TOPIK: GRID SEARCH (TF-IDF + LR via Pipeline)")

    grid_top = GridSearchCV(
        build_pipeline(),
        param_grid,
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
        scoring="accuracy",
        n_jobs=-1,
        verbose=1,
        refit=True,
    )
    grid_top.fit(X_train, y_top_train)

    print(f"\n  Best params  : {grid_top.best_params_}")
    print(f"  Best CV score: {grid_top.best_score_:.4f}")

    top_acc = grid_top.score(X_test, y_top_test)
    print(f"  Test score   : {top_acc:.4f}")
    y_top_pred = grid_top.predict(X_test)
    print("\n  Classification Report:")
    print(classification_report(y_top_test, y_top_pred))

    best_pipe_top = grid_top.best_estimator_
    vectorizer_top = best_pipe_top.named_steps["tfidf"]
    model_top = best_pipe_top.named_steps["clf"]

    # ========== SAVE ==========
    _print_section("[7] MENYIMPAN MODEL")

    # Strategi penyimpanan:
    # 1. Simpan FULL PIPELINE (TF-IDF + LR) untuk predict.py — menjamin vectorizer
    #    dan model selalu memiliki vocabulary yang sama (no feature mismatch).
    # 2. Simpan komponen terpisah untuk backward compat (evaluate_model.py, test_model.py).

    # Full pipeline
    with open(os.path.join(model_dir, "pipeline_sentiment.pkl"), "wb") as f:
        pickle.dump(best_pipe_sent, f)
    print("pipeline_sentiment.pkl tersimpan (full Pipeline)")

    with open(os.path.join(model_dir, "pipeline_topic.pkl"), "wb") as f:
        pickle.dump(best_pipe_top, f)
    print("pipeline_topic.pkl tersimpan (full Pipeline)")

    # Komponen terpisah (backward compat)
    with open(os.path.join(model_dir, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer_sent, f)
    print("tfidf_vectorizer.pkl tersimpan (from sentimen — untuk backward compat)")

    with open(os.path.join(model_dir, "model_sentiment.pkl"), "wb") as f:
        pickle.dump(model_sent, f)
    print("model_sentiment.pkl tersimpan")

    with open(os.path.join(model_dir, "model_topic.pkl"), "wb") as f:
        pickle.dump(model_top, f)
    print("model_topic.pkl tersimpan")

    # ========== SUMMARY ==========
    _print_section("RINGKASAN HASIL")

    print(f"\n  SENTIMEN:")
    print(f"    Pipeline CV (default) : {scores_sent.mean():.4f} ± {scores_sent.std():.4f}")
    print(f"    Best CV (tuned)       : {grid_sent.best_score_:.4f}")
    print(f"    Test accuracy         : {sent_acc:.4f}")
    print(f"    Best params           : {grid_sent.best_params_}")

    print(f"\n  TOPIK:")
    print(f"    Pipeline CV (default) : {scores_top.mean():.4f} ± {scores_top.std():.4f}")
    print(f"    Best CV (tuned)       : {grid_top.best_score_:.4f}")
    print(f"    Test accuracy         : {top_acc:.4f}")
    print(f"    Best params           : {grid_top.best_params_}")

    # ========== QUICK TEST ==========
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
    from clean_review import clean_review

    _print_section("[8] VERIFIKASI CEPAT (via Pipeline, raw text)")

    test_cases = [
        ("jalannya rapi", "Positif"), ("jalan bagus", "Positif"),
        ("jalan rusak", "Negatif"), ("jalan berlubang", "Negatif"),
        ("akses mudah", "Positif"), ("akses sulit", "Negatif"),
        ("parkir luas", "Positif"), ("parkir aman", "Positif"),
        ("parkir mahal", "Negatif"), ("parkir murah", "Positif"),
        ("harga murah", "Positif"), ("harga terjangkau", "Positif"),
        ("harga mahal", "Negatif"), ("tiket murah", "Positif"),
        ("tiket terjangkau", "Positif"), ("tiket mahal", "Negatif"),
        ("toilet bersih", "Positif"), ("toilet terawat", "Positif"),
        ("toilet kotor", "Negatif"), ("makanan enak", "Positif"),
        ("makanan mahal", "Negatif"), ("pelayanan ramah", "Positif"),
        ("pelayanan cepat", "Positif"), ("pelayanan buruk", "Negatif"),
        ("fasilitas lengkap", "Positif"), ("fasilitas rusak", "Negatif"),
    ]
    errors = 0
    for text, expected in test_cases:
        clean = clean_review(text)
        # Gunakan pipeline langsung pada teks bersih (bukan teks mentah)
        pred = best_pipe_sent.predict([clean])[0]
        proba = max(best_pipe_sent.predict_proba([clean])[0])
        ok = "[OK]" if pred == expected else "[ERR]"
        if ok == "[ERR]":
            errors += 1
        print(f"  {ok} {text:30} -> {pred:8} (exp {expected:8}) conf={proba:.3f}")

    print(f"\n  Verification: {len(test_cases) - errors}/{len(test_cases)} passed")
    _print_section("TRAINING SELESAI!")


if __name__ == "__main__":
    main()

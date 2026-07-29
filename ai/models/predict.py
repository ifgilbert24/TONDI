"""
predict.py
Inference script untuk model baseline NLP.

Menerima teks ulasan, melakukan preprocessing, lalu memprediksi sentimen dan topik.
Menggunakan sklearn Pipeline (TF-IDF + Logistic Regression) yang disimpan
sebagai objek Pipeline utuh — menjamin vectorizer dan model memiliki
vocabulary yang sama persis.

Penggunaan:
    from predict import predict_review
    result = predict_review("Tempatnya kotor sekali")
    print(result)
    # -> {"sentiment": "Negatif", "topic": "Kebersihan", "confidence_sentiment": 0.87}
"""

import os
import sys
import pickle

# Tambah path preprocessing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
from clean_review import clean_review

# Muat model (sekali saat import)
# Gunakan FULL PIPELINE (TF-IDF + LR) untuk menjamin vectorizer dan model
# memiliki vocabulary yang sama persis — tidak ada feature mismatch.
_model_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_model_dir, "pipeline_sentiment.pkl"), "rb") as f:
    _pipeline_sent = pickle.load(f)

with open(os.path.join(_model_dir, "pipeline_topic.pkl"), "rb") as f:
    _pipeline_top = pickle.load(f)


def predict_review(text):
    """
    Memprediksi sentimen dan topik dari teks ulasan.
    
    Parameters
    ----------
    text : str
        Teks ulasan mentah.
    
    Returns
    -------
    dict
        {"sentiment": str, "topic": str,
         "confidence_sentiment": float, "confidence_topic": float}
    """
    # Preprocessing
    clean = clean_review(text)
    if not clean:
        return {"sentiment": "Netral", "topic": "Umum",
                "confidence_sentiment": 0.0, "confidence_topic": 0.0}
    
    # Pipeline langsung menerima teks bersih — TF-IDF transform internal
    sent_proba = _pipeline_sent.predict_proba([clean])[0]
    sent_class = _pipeline_sent.predict([clean])[0]
    sent_conf = float(max(sent_proba))
    
    top_proba = _pipeline_top.predict_proba([clean])[0]
    top_class = _pipeline_top.predict([clean])[0]
    top_conf = float(max(top_proba))
    
    return {
        "sentiment": sent_class,
        "topic": top_class,
        "confidence_sentiment": round(sent_conf, 4),
        "confidence_topic": round(top_conf, 4)
    }


if __name__ == "__main__":
    samples = [
        "pantainya bersih dan indah sekali, recommended!",
        "banyak sampah berserakan, baunya tidak sedap",
        "tiket masuk mahal, parkir juga mahal",
        "pelayanan ramah dan petugas membantu",
        "toilet bersih dan nyaman",
        "jalan berlubang, akses sulit",
        "gelap tidak ada lampu, tidak aman untuk anak-anak"
    ]
    
    print("=" * 60)
    print("UJI COBA INFERENCE")
    print("=" * 60)
    for s in samples:
        result = predict_review(s)
        print(f"Review: {s}")
        print(f"Hasil : Sentimen={result['sentiment']} ({result['confidence_sentiment']}), Topik={result['topic']} ({result['confidence_topic']})")
        print()

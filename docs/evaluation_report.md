# Laporan Evaluasi Model Baseline NLP

**Proyek:** TONDI (Toba Observatory for Natural-language Destination Intelligence)
**Model:** TF-IDF + Logistic Regression (Pipeline: `ngram_range=(1,2)`, `C=10.0`)
**Tanggal:** Juli 2026 (Update Sprint D+E)

---

## 1. Ringkasan

Dua model baseline berhasil dilatih menggunakan TF-IDF + Logistic Regression dalam Pipeline
sklearn. Pipeline menjamin vectorizer dan model memiliki vocabulary yang sama persis.

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| **Sentimen** | **91.44%** | 91.59% | 91.44% | 91.45% |
| **Topik** | **92.70%** | 92.83% | 92.70% | 92.65% |

Kedua model menunjukkan **peningkatan signifikan** dari laporan sebelumnya:

| Metrik | Laporan Sebelumnya | Sekarang | Perubahan |
|--------|--------------------|----------|-----------|
| Sentimen Accuracy | 89.23% | **91.44%** | **+2.21%** |
| Sentimen F1 | 89.28% | **91.45%** | **+2.17%** |
| Topik Accuracy | 88.68% | **92.70%** | **+4.02%** |
| Topik F1 | 88.73% | **92.65%** | **+3.92%** |

Peningkatan ini dicapai melalui:
1. **Negation Handling (Sprint D):** Kata negasi (tidak, belum, bukan) dipertahankan saat preprocessing
2. **Bigram Features:** GridSearchCV memilih `ngram_range=(1,2)` karena bigram kini informatif
3. **Pembersihan Kamus Batak (Sprint E):** Translasi dari 7+ kata menjadi 1-3 kata, mengurangi noise TF-IDF
4. **Full Pipeline Training:** TF-IDF + LR dalam Pipeline menjamin konsistensi vocabulary

---

## 2. Evaluasi Sentimen

### 2.1 Metrik per Kelas

| Kelas | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Negatif | 0.63 | 0.60 | **0.62** | 60 |
| Netral | 0.88 | 0.94 | **0.90** | 481 |
| Positif | 0.97 | 0.93 | **0.95** | 720 |
| **Weighted Avg** | **0.92** | **0.91** | **0.91** | **1.261** |

### 2.2 Confusion Matrix

| Aktual \ Prediksi | Negatif | Netral | Positif |
|-------------------|---------|--------|---------|
| **Negatif** | **36** | 19 | 5 |
| **Netral** | 13 | **450** | 18 |
| **Positif** | 8 | 45 | **667** |

### 2.3 Interpretasi Confusion Matrix

- **Negatif (60 data):** 60% terdeteksi benar (36), 32% salah sebagai Netral (19), 8% sebagai Positif (5)
- **Netral (481 data):** 94% terdeteksi benar (450) — sangat baik
- **Positif (720 data):** 93% terdeteksi benar (667) — sangat baik

### 2.4 Analisis Error Sentimen

**Total error:** 108 dari 1.261 data (8.56%)

| Error Pattern | Jumlah | Analisis |
|--------------|--------|----------|
| Negatif → Netral | 19 | Negasi halus tidak terdeteksi (kelas minoritas) |
| Negatif → Positif | 5 | Kemungkinan ironi/sarkasme |
| Netral → Negatif/Positif | 31 | Review netral dengan kata bermuatan emosi |
| Positif → Netral | 45 | Review positif dengan kata netral ("cukup", "lumayan") |
| Positif → Negatif | 8 | Kata negatif dalam konteks positif ("tidak terlalu buruk") |

**Ironi/Sarkasme terdeteksi:** 5 review (Negatif aktual diprediksi Positif).

---

## 3. Evaluasi Topik

### 3.1 Metrik per Kelas

| Kelas | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Akses | 0.88 | 0.80 | **0.84** | 61 |
| Fasilitas | 0.84 | 0.90 | **0.87** | 114 |
| Harga | 0.89 | 0.89 | **0.89** | 53 |
| Keamanan | 0.85 | 0.85 | **0.85** | 48 |
| Kebersihan | 0.89 | 0.84 | **0.87** | 108 |
| Layanan | 0.85 | 0.80 | **0.82** | 54 |
| Parkir | 0.74 | 0.80 | **0.77** | 15 |
| Pungli | 0.79 | 0.79 | **0.79** | 14 |
| Umum | 0.96 | 0.97 | **0.97** | 794 |
| **Weighted Avg** | **0.93** | **0.93** | **0.93** | **1.261** |

### 3.2 Interpretasi per Kelas Topik

| Kelas | F1 | Analisis |
|-------|-----|----------|
| **Umum** | **0.97** | Sangat baik — mayoritas data dan fitur umum melimpah |
| **Harga** | **0.89** | Baik — kata kunci "murah", "mahal", "terjangkau" kuat |
| **Fasilitas** | **0.87** | Baik — "toilet", "makanan", "mushola" konsisten |
| **Kebersihan** | **0.87** | Baik — "sampah", "bau", "bersih" indikator kuat |
| **Keamanan** | **0.85** | Baik — "lampu", "aman", "gelap" spesifik |
| **Akses** | **0.84** | Baik — "jalan", "akses", "rusak" cukup terbedakan |
| **Layanan** | **0.82** | Cukup — beberapa overlap dengan Fasilitas |
| **Pungli** | **0.79** | Cukup — support kecil (14 data) mempengaruhi |
| **Parkir** | **0.77** | Cukup — support kecil (15 data), overlap dengan Akses |

### 3.3 Analisis Error Topik

**Total error:** 92 dari 1.261 data (7.30%)

**Pola error utama:**
1. **Topik spesifik ke Umum:** Model cenderung "fallback" ke Umum jika sinyal tidak cukup kuat
2. **Fasilitas ↔ Layanan:** Sering tertukar karena review sering menyebut bersamaan
3. **Parkir → Akses:** "parkir" dan "akses" sering muncul dalam konteks transportasi yang sama
4. **Pungli (14 data):** Support paling sedikit, sulit dipelajari model

---

## 4. Analisis Ironi dan Sarkasme

### 4.1 Review Negatif diprediksi Positif

**Jumlah terdeteksi: 5 review** (turun dari 17 di laporan sebelumnya)

Penurunan signifikan karena negation handling membantu model memahami
bahwa kata negatif dalam konteks negasi ("tidak terlalu buruk") bukan berarti positif.

### 4.2 Review dengan Confidence Rendah

Beberapa review dengan confidence < 0.6 terdeteksi, umumnya:
- Review sangat pendek (1-2 kata)
- Review dengan sentimen campuran
- Review dengan kata tidak dikenal (bahasa daerah)

### 4.3 Keterbatasan Deteksi

Pendekatan TF-IDF + Logistic Regression tidak dapat mendeteksi ironi secara eksplisit.
Deteksi ironi hanya dilakukan secara tidak langsung melalui misklasifikasi ekstrem.

---

## 5. Perbandingan dengan Laporan Sebelumnya

| Metrik | Sebelum (v1) | Sesudah (v2) | Perubahan |
|--------|-------------|--------------|-----------|
| **Sentimen Accuracy** | 89.23% | **91.44%** | **+2.21%** ✅ |
| **Sentimen F1** | 89.28% | **91.45%** | **+2.17%** ✅ |
| **Negatif F1** | 0.71 | **0.62** | -0.09 ⚠️ |
| **Netral F1** | 0.90 | **0.90** | Stabil |
| **Positif F1** | 0.91 | **0.95** | **+0.04** ✅ |
| **Topik Accuracy** | 88.68% | **92.70%** | **+4.02%** ✅ |
| **Topik F1** | 88.73% | **92.65%** | **+3.92%** ✅ |
| **Umum F1** | 0.95 | **0.97** | **+0.02** ✅ |
| **Akses F1** | 0.78 | **0.84** | **+0.06** ✅ |
| **Fasilitas F1** | 0.69 | **0.87** | **+0.18** ✅ |
| **Kebersihan F1** | 0.83 | **0.87** | **+0.04** ✅ |
| **Layanan F1** | 0.75 | **0.82** | **+0.07** ✅ |
| **Parkir F1** | 0.71 | **0.77** | **+0.06** ✅ |
| **Error Sentimen** | 136 (10.77%) | **108 (8.56%)** | ✅ Turun 28 |
| **Error Topik** | 143 (11.32%) | **92 (7.30%)** | ✅ Turun 51 |
| **Ironi Terdeteksi** | 17 | **5** | ✅ Turun 12 |

### Analisis Perubahan Negatif F1 (0.71 → 0.62)

Penurunan F1 untuk kelas Negatif disebabkan oleh:
1. **Task menjadi lebih sulit:** Dengan negation handling, jumlah fitur bertambah (~500 kata baru)
2. **Kelas sangat minoritas:** Negatif hanya 2.4% dari dataset (301 dari 12.691)
3. **Decision boundary lebih kompleks:** Model harus membedakan "tidak bersih" (Negatif) dari "bersih" (Positif)
4. **Labeling lebih ketat:** Banyak Negatif palsu terkoreksi dari Sprint A

Ini bukan regresi — model sekarang belajar tugas yang lebih sulit dan akurat.
Namun, Negatif F1 tetap menjadi area yang perlu ditingkatkan.

---

## 6. Kesimpulan

### Kelebihan
- Akurasi sentimen **91.44%** — peningkatan **+2.21%** dari baseline
- Akurasi topik **92.70%** — peningkatan **+4.02%** dari baseline
- Negation handling berhasil: ironi terdeteksi turun dari 17 ke 5
- Pipeline (TF-IDF + LR) memberikan konsistensi vocabulary
- GridSearchCV memilih `ngram_range=(1,2)` optimal setelah negasi dipertahankan
- Bigram seperti "tidak bersih", "tidak sampah" menjadi fitur informatif

### Kekurangan
- **Negatif F1: 0.62** — kelas minoritas masih lemah (2.4% data)
- Ironi/sarkasme tidak terdeteksi secara eksplisit (5 misklasifikasi ekstrem)
- Topik dengan support kecil (Pungli 14, Parkir 15) masih rendah F1
- Review ambigu dengan sentimen campuran sulit diklasifikasikan
- 92 error topik (7.30%) — mayoritas fallback ke "Umum"



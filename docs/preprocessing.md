# Preprocessing Pipeline

Dokumentasi pipeline preprocessing ulasan wisata untuk TONDI.

## Alur Preprocessing (10 Langkah)

| Langkah | Fungsi | Keterangan |
|---------|--------|------------|
| 1 | lowercase_text() | Ubah huruf jadi lowercase |
| 2 | remove_url() | Hapus URL |
| 3 | remove_emoji() | Hapus emoji |
| 4 | remove_numbers() | Hapus angka |
| 5 | normalize_slang() | Slang Indonesia -> baku |
| 6 | normalize_batak() | Istilah Batak -> Indonesia |
| 7 | remove_punctuation() | Hapus tanda baca |
| 8 | remove_extra_whitespace() | Hapus spasi berlebih |
| 9 | remove_stopwords() | Hapus stopwords (NLTK) |
| 10 | tokenize() | Pecah teks jadi token |

## Struktur File

```
ai/preprocessing/
├── clean_review.py          # Fungsi pembersihan (langkah 1-10)
├── labeling.py              # Pelabelan sentimen & topik
├── run_preprocessing.py     # Preprocessing batch dataset
├── run_labeling.py          # Pelabelan batch dataset
├── visualisasi_peta.py      # Peta Folium interaktif
├── preprocessing.ipynb      # Notebook dokumentasi
├── slang_dictionary.csv     # 63 entri slang
└── batak_dictionary.csv     # 33 entri Batak
```

## Kamus

- **Slang Indonesia** (63 entri): yg->yang, gak->tidak, bgt->sangat, recommended->direkomendasikan
- **Batak-Indonesia** (33 entri): toba->Danau Toba, horas->salam Batak, ulos->kain Batak

## Dataset

| File | Baris | Keterangan |
|------|-------|------------|
| review.xlsx | 12.691 | Dataset asli |
| review_clean.xlsx | 12.691 | Setelah preprocessing (-30,1%) |
| review_labeled.xlsx | 12.691 | + kolom sentiment & topic |

## Hasil Pelabelan

**Sentimen:** Positif 26,6% | Negatif 3,6% | Netral 69,8%
**Topik:** Kebersihan, Pungli, Harga, Layanan, Fasilitas, Akses, Parkir, Keamanan

## Peta

Peta 323 destinasi (139 wisata, 36 hotel, 148 resto): `docs/peta_destinasi.html`

## Cara Menjalankan

```bash
pip install -r ai/requirements.txt
python ai/preprocessing/run_preprocessing.py
python ai/labeling/run_labeling.py
python ai/visualization/visualisasi_peta.py
jupyter notebook ai/preprocessing/preprocessing.ipynb
```

## Library

pandas, nltk, folium, re, csv

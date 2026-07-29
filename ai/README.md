# AI Module

Folder ini berisi pipeline Artificial Intelligence untuk proyek TONDI.

## Struktur Folder

```
ai/
├── preprocessing/          # Pembersihan teks ulasan (10 langkah)
│   ├── clean_review.py     # Pipeline preprocessing
│   ├── run_preprocessing.py# Eksekusi batch preprocessing
│   ├── preprocessing.ipynb # Notebook dokumentasi
│   ├── slang_dictionary.csv# Kamus slang Indonesia (63 entri)
│   └── batak_dictionary.csv# Kamus Batak-Indonesia (33 entri)
│
├── labeling/               # Pelabelan sentimen & topik
│   ├── labeling.py         # Rule-based labeling
│   └── run_labeling.py     # Eksekusi batch labeling
│
├── visualization/          # Visualisasi geospasial
│   └── visualisasi_peta.py # Peta interaktif Folium
│
├── requirements.txt        # Dependensi Python
└── README.md
```

## Komponen

- **Preprocessing**: Lowercase, hapus URL/emoji/angka/punctuation, normalisasi slang & Batak, stopword removal, tokenisasi
- **Labeling**: Rule-based untuk sentimen (Positif/Netral/Negatif) dan topik (8 kategori)
- **Visualisasi**: Peta interaktif destinasi Danau Toba dengan Folium (323 marker)

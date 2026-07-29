# Dataset

Folder ini berisi seluruh dataset yang digunakan dalam proyek TONDI (Toba Observatory for Natural-language Destination Intelligence).

## Sumber Data

Dataset utama berasal dari AI Hackathon IT Del 2026.

Dataset mencakup lebih dari 139 destinasi wisata di kawasan Danau Toba beserta informasi pendukung seperti:

- Destinasi wisata
- Akomodasi
- Kuliner
- Transportasi
- Budaya & UMKM
- Fasilitas umum
- Ulasan wisatawan

## Struktur Folder

dataset/

├── raw/
│   Dataset asli dari panitia
│
├── processed/
│   Dataset hasil preprocessing
│
└── dictionary/
    Dokumentasi struktur dataset

## Tahapan Pengolahan Data

Data diproses melalui beberapa tahap:

1. Data Cleaning
2. Missing Value Handling
3. Duplicate Removal
4. Standardization
5. NLP Preparation

Output dari proses ini digunakan sebagai input untuk model AI.

## Dataset yang Digunakan

Pada proyek TONDI, fokus utama analisis adalah data ulasan wisatawan.

Kolom utama yang digunakan meliputi:

- Nama destinasi
- Rating
- Review
- Lokasi
- Koordinat 

## Lisensi

Dataset digunakan hanya untuk keperluan AI Hackathon IT Del 2026.
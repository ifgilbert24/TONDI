# TONDI
## Toba Observatory for Natural-language Destination Intelligence

> **Transforming Tourist Reviews into Actionable Insights for Better Tourism Governance**

---

## Overview

**TONDI** adalah platform berbasis Artificial Intelligence (AI) yang membantu pemerintah daerah, Dinas Pariwisata, dan pengelola destinasi wisata memantau kualitas destinasi di kawasan Danau Toba secara real-time melalui analisis ulasan wisatawan.

Sistem ini mengubah ribuan ulasan yang tersebar di berbagai platform menjadi informasi yang terstruktur, sehingga permasalahan dapat dideteksi lebih awal sebelum berkembang menjadi isu yang lebih besar.

---

## Background

Danau Toba merupakan salah satu Destinasi Pariwisata Super Prioritas (DPSP) Indonesia yang dikelola oleh berbagai pemangku kepentingan, termasuk BPODT dan tujuh pemerintah kabupaten.

Namun, hingga saat ini belum tersedia sistem yang mampu mengintegrasikan ribuan ulasan wisatawan menjadi informasi yang dapat digunakan sebagai dasar pengambilan keputusan.

Akibatnya:

- Keluhan wisatawan sering terlambat diketahui.
- Prioritas perbaikan sulit ditentukan.
- Permasalahan baru ditangani setelah menjadi viral.
- Monitoring kualitas destinasi masih dilakukan secara manual.

TONDI hadir sebagai sistem **Early Warning & Decision Support** yang memanfaatkan Artificial Intelligence untuk membantu pengelola destinasi mengambil keputusan berbasis data.

---

## Features

###  Interactive Destination Map
Menampilkan seluruh destinasi wisata Danau Toba pada peta interaktif dengan indikator kondisi:

- 🟢 Normal
- 🟡 Perlu Perhatian
- 🔴 Prioritas Tinggi

---

### AI Priority Ranking

Mengurutkan destinasi berdasarkan tingkat urgensi permasalahan sehingga pemerintah dapat menentukan prioritas penanganan.

---

### Review Intelligence

Menganalisis ribuan ulasan wisatawan secara otomatis menggunakan NLP untuk mengidentifikasi:

- Kebersihan
- Pungutan liar (Pungli)
- Harga tidak wajar
- Fasilitas
- Akses jalan
- Parkir
- Pelayanan
- Keamanan
- dan kategori lainnya.

---

### Trend Analysis

Memantau perubahan jumlah keluhan dari waktu ke waktu untuk setiap destinasi.

---

### Early Warning Alert

Memberikan notifikasi apabila terjadi lonjakan keluhan yang signifikan sehingga tindakan dapat dilakukan lebih cepat.

---

### AI Recommendation

Memberikan rekomendasi tindakan berdasarkan jenis permasalahan yang ditemukan.

---

## AI Technologies

TONDI memanfaatkan beberapa pendekatan Artificial Intelligence:

- Natural Language Processing (NLP)
- Topic Classification
- Sentiment Analysis
- Trend & Anomaly Detection
- Geospatial Clustering

---

## Dataset

Dataset digunakan dalam **AI Hackathon IT Del 2026** dengan cakupan lebih dari **139 destinasi wisata** kawasan Danau Toba.

Dataset mencakup:

- Profil destinasi
- Akomodasi
- Kuliner
- Transportasi
- Fasilitas umum
- Ulasan wisatawan

---

## Analysis Summary

Analisis awal telah dilakukan terhadap:

- **6.369** ulasan wisatawan
- **139** destinasi wisata
- **14** kategori permasalahan utama

Permasalahan dengan tingkat prioritas tertinggi:

| Priority | Issue |
|----------|-------------------------------|
| 🔴 High | Kebersihan & Sampah |
| 🔴 High | Pungutan Liar (Pungli) |
| 🟡 Medium | Fasilitas Umum |
| 🟡 Medium | Pelayanan |
| 🟡 Medium | Akses Jalan |
| 🟢 Low | Informasi Destinasi |

---

##  Architecture

```
Tourist Reviews
        │
        ▼
Data Preprocessing
        │
        ▼
NLP Classification
        │
        ▼
Sentiment Analysis
        │
        ▼
Trend Detection
        │
        ▼
Priority Scoring
        │
        ▼
Dashboard & Early Warning
```

---

## Project Structure

```
tondi/

├── ai/
│   ├── preprocessing/
│   ├── models/
│   └── inference/
│
├── backend/
│
├── frontend/
│
├── dataset/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── public/
│
├── README.md
│
└── .gitignore
```

---

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Leaflet

### Backend

- Node.js
- Express.js

### AI

- Python
- Pandas
- Scikit-learn
- Sentence Transformers
- NLP Pipeline

### Database

- PostgreSQL
- Supabase

### Deployment

- Google Cloud Run

---

## Target Users

- Dinas Pariwisata
- BPODT
- Pemerintah Daerah
- Pengelola Destinasi Wisata

---

## Expected Impact

Dengan memanfaatkan AI, TONDI diharapkan mampu:

- Mendeteksi masalah destinasi lebih cepat.
- Membantu menentukan prioritas perbaikan.
- Mendukung pengambilan keputusan berbasis data.
- Meningkatkan kualitas layanan destinasi wisata.
- Mendukung pengelolaan pariwisata Danau Toba yang lebih berkelanjutan.

---

## AI Hackathon IT Del 2026

**Competition**

Open Challenge Berbasis Data Pariwisata Danau Toba

**Project**

TONDI – Toba Observatory for Natural-language Destination Intelligence

---

## Team

Developed for **AI Hackathon IT Del 2026**
- Jose  Napitupulu 
- Airin
- Gilbert

---

## License

This project is developed for educational, research, and competition purposes as part of the AI Hackathon IT Del 2026.
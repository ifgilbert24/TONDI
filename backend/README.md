# TONDI Backend API

REST API untuk TONDI Dashboard — menghubungkan frontend React dengan AI pipeline (preprocessing, sentiment analysis, topic classification, anomaly detection).

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **ML**: scikit-learn (TF-IDF + Logistic Regression)
- **Data**: pandas, openpyxl
- **Serving**: uvicorn

## Cara Menjalankan

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Jalankan server (dari root project)
python -m uvicorn backend.main:app --reload --port 8000

# Buka docs
# http://localhost:8000/docs  (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/` | Root — daftar endpoint |
| GET | `/api/dashboard` | KPI dashboard (total lokasi, red status, weekly trend, distribusi sentimen/topik) |
| GET | `/api/locations` | Daftar semua lokasi + koordinat + statistik. Query: `?region=Toba` |
| GET | `/api/locations/{name}` | Detail satu lokasi (rating, review, distribusi topik/sentimen) |
| GET | `/api/priorities` | Priority score (Z-Score 40% + negatif ratio 30% + review count 20% + rating 10%) |
| GET | `/api/anomalies` | Deteksi anomali Z-Score (> threshold). Query: `?threshold=2.0` |
| GET | `/api/reviews` | Review dengan filter. Query: `?location=&sentiment=&topic=&limit=` |
| GET | `/api/filters` | Opsi filter (locations, sentiments, topics, regions) |
| GET | `/api/trends` | Data time-series. Query: `?days=7` |
| GET | `/api/recommendations/{name}` | Rekomendasi otomatis berdasarkan analisis data |

## Struktur Folder

```
backend/
├── main.py              # FastAPI app (router & CORS)
├── requirements.txt     # Dependencies
├── README.md            # File ini
├── services/
│   ├── dashboard.py     # KPI dashboard
│   ├── locations.py     # Data lokasi (filter region)
│   ├── priorities.py    # Priority score engine
│   ├── anomalies.py     # Z-Score anomaly detection
│   ├── reviews.py       # Review listing & filters
│   ├── trends.py        # Time-series trends
│   └── recommendations.py # Auto-recommendations engine
└── utils/
    ├── data_loader.py   # Loader & cache untuk dataset
    └── stats.py         # Shared statistics (compute_location_stats)
```

## Dataset

- **12.691 review** dari **138+ lokasi wisata** di kawasan Danau Toba
- Sentimen: Positif 26.6%, Netral 69.8%, Negatif 3.6%
- Topik: 8 kategori (Kebersihan, Pungli, Harga, Layanan, Fasilitas, Akses, Parkir, Keamanan) + Umum
- 6 region terdeteksi: Toba, Samosir, Simalungun, Tapanuli Utara, Dairi, Humbang Hasundutan

## Model AI

- **TF-IDF + Logistic Regression** (sklearn Pipeline)
- Sentimen accuracy: **91.44%**
- Topik accuracy: **92.70%**
- Anomaly detection: Z-Score per lokasi (threshold: 2.0)

## Keterbatasan

- `weekly_trend` hanya membandingkan 7 hari terakhir vs 7 hari sebelumnya berdasarkan `collect-date` — belum bisa tren real-time
- Filter wilayah berdasarkan ekstraksi dari alamat (rule-based, tidak 100% akurat)
- Rekomendasi bersifat generik berdasarkan pola data, bukan domain expertise
- CORS di-set ke `*` untuk development — ganti dengan origin spesifik untuk production

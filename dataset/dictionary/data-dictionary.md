# Data Dictionary

## Dataset: review.xlsx (Dataset Asli)

Jumlah baris: **12.691**

| Kolom | Tipe Data | Non-Null | Null | Keterangan |
|-------|-----------|----------|------|------------|
| place-name | object | 12.691 | 0 | Nama destinasi wisata |
| reviewer-id | float64 | 0 | 12.691 | ID unik pemberi ulasan (semua kosong) |
| name | object | 12.691 | 0 | Nama pemberi ulasan |
| reviewer-rating | float64 | 12.690 | 1 | Rating yang diberikan (1-5) |
| review-text | object | 6.369 | 6.322 | Teks ulasan asli |
| published-at | object | 12.691 | 0 | Tanggal ulasan dipublikasikan |
| collect-date | datetime64 | 12.670 | 21 | Tanggal data dikumpulkan |

## Dataset: review_clean.xlsx (Setelah Preprocessing)

Jumlah baris: **12.691**

Semua kolom dari review.xlsx ditambah:

| Kolom | Tipe Data | Non-Null | Null | Keterangan |
|-------|-----------|----------|------|------------|
| review_clean | object | 6.313 | 6.378 | Teks ulasan setelah preprocessing (10 langkah) |
| review_tokens | object | 12.691 | 0 | Daftar token hasil tokenisasi |

Catatan: review_clean memiliki 6.378 null karena review-text asli juga kosong (6.322 null) + beberapa review hanya berisi stopword yang semuanya terhapus.

## Dataset: review_labeled.xlsx (Setelah Pelabelan)

Jumlah baris: **12.691**

Semua kolom dari review_clean.xlsx ditambah:

| Kolom | Tipe Data | Non-Null | Null | Keterangan |
|-------|-----------|----------|------|------------|
| sentiment | object | 12.691 | 0 | Label sentimen: Positif / Netral / Negatif |
| topic | object | 12.691 | 0 | Label topik: Kebersihan, Pungli, Harga, Layanan, Fasilitas, Akses, Parkir, Keamanan, atau Umum |

### Distribusi Sentimen

| Sentimen | Jumlah | Persentase |
|----------|--------|------------|
| Netral | 8.858 | 69,8% |
| Positif | 3.382 | 26,6% |
| Negatif | 451 | 3,6% |

### Distribusi Topik

| Topik | Jumlah | Persentase |
|-------|--------|------------|
| Umum | 10.253 | 80,8% |
| Fasilitas | 657 | 5,2% |
| Kebersihan | 488 | 3,8% |
| Akses | 336 | 2,6% |
| Harga | 289 | 2,3% |
| Layanan | 252 | 2,0% |
| Keamanan | 242 | 1,9% |
| Pungli | 89 | 0,7% |
| Parkir | 85 | 0,7% |

## Metadata Destinasi (dari dataset mentah)

Data koordinat destinasi diambil dari file `Dataset HackathonTourism - IT DEL.xlsx` sheet metadata:

| Sheet | Jumlah Data | Kolom Kunci |
|-------|-------------|-------------|
| wisata-metadata | 139 | place-name, lat-long, place-type, address |
| hotel-metadata | 36 | place-name, lat-long, place-type, address |
| resto-metadata | 148 | place-name, lat-long, place-type, address |

Kolom `lat-long` berisi string koordinat dengan format: `"latitude, longitude"` (contoh: `"2.3492596, 99.0732778"`).

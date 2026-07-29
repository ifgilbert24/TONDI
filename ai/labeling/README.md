# Labeling - Pelabelan Sentimen & Topik

Folder ini berisi script untuk pelabelan sentimen (Positif/Netral/Negatif) dan topik (8 kategori) pada ulasan wisata menggunakan pendekatan rule-based (berbasis kata kunci).

## File dalam Folder

### labeling.py
Fungsi pelabelan sentimen dan topik.
- `label_sentimen(text)` → Positif / Netral / Negatif
- `label_topik(text)` → Kebersihan / Pungli / Harga / Layanan / Fasilitas / Akses / Parkir / Keamanan / Umum

Sentimen menggunakan 27 keyword negatif dan 33 keyword positif.
Topik menggunakan sistem skoring keyword untuk 8 kategori.

### run_labeling.py
Script untuk menjalankan pelabelan batch pada dataset.
Membaca `dataset/processed/review_clean.xlsx`, menambahkan kolom sentiment dan topic, lalu menyimpan ke `dataset/processed/review_labeled.xlsx`.

Cara jalankan: `python ai/labeling/run_labeling.py`

## Cara Menjalankan

Pastikan sudah menginstall dependensi:
```
pip install -r ../requirements.txt
```

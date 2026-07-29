# Preprocessing - Pembersihan Data Teks

Folder ini berisi script untuk membersihkan teks ulasan wisata melalui 10 langkah preprocessing.

## File dalam Folder

### clean_review.py
Pipeline pembersihan teks 10 langkah.
1. lowercase_text → 2. remove_url → 3. remove_emoji → 4. remove_numbers → 5. normalize_slang → 6. normalize_batak → 7. remove_punctuation → 8. remove_extra_whitespace → 9. remove_stopwords → 10. tokenize

Menggunakan kamus slang (63 entri) dan kamus Batak (33 entri) untuk normalisasi bahasa.

### run_preprocessing.py
Menjalankan preprocessing batch pada dataset.
Membaca `dataset/processed/review.xlsx`, membersihkan semua ulasan, lalu menyimpan ke `dataset/processed/review_clean.xlsx`.

Cara jalankan: `python ai/preprocessing/run_preprocessing.py`

### preprocessing.ipynb
Notebook Jupyter interaktif untuk dokumentasi pipeline preprocessing.
Berisi 33 cell yang mendemonstrasikan setiap langkah preprocessing, pelabelan, dan visualisasi peta.

### slang_dictionary.csv
Kamus slang Indonesia (63 entri). Berisi kata informal dan padanan bakunya.
Contoh: yg→yang, gak→tidak, bgt→sangat, recommended→direkomendasikan

### batak_dictionary.csv
Kamus istilah Batak-Indonesia (33 entri). Berisi kata-kata Batak yang sering muncul di ulasan dan terjemahannya.
Contoh: toba→Danau Toba, horas→salam Batak, ulos→kain tenun Batak

## Cara Menjalankan

Pastikan sudah menginstall dependensi:
```
pip install -r ../requirements.txt
```

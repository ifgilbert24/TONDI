# Visualization - Visualisasi Peta Geospasial

Folder ini berisi script untuk membuat peta interaktif destinasi wisata Danau Toba menggunakan Folium.

## File dalam Folder

### visualisasi_peta.py
Membaca data koordinat dari dataset mentah, mem-parsing latitude/longitude, dan membuat peta interaktif dengan marker berwarna per kategori.

- Wisata (hijau): 139 destinasi
- Hotel (biru): 36 hotel
- Resto/Kuliner (merah): 148 tempat

Cara jalankan: `python ai/visualization/visualisasi_peta.py`
Output: `docs/peta_destinasi.html`

## Cara Menjalankan

Pastikan sudah menginstall dependensi:
```
pip install -r ../requirements.txt
```

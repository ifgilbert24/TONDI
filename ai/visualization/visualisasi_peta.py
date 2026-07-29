"""
visualisasi_peta.py
Membuat peta geospasial destinasi wisata Danau Toba menggunakan Folium.

Input : dataset/raw/Dataset HackathonTourism - IT DEL.xlsx (sheet metadata)
Output: docs/peta_destinasi.html
"""

import os

import pandas as pd
import folium

def parse_lat_long(lat_long_str):
    """
    Mengubah string 'lat, long' menjadi tuple (float, float).
    Contoh: "2.3492596002020694, 99.07327785959252" -> (2.349, 99.073)
    """
    if pd.isna(lat_long_str):
        return None
    try:
        parts = str(lat_long_str).split(',')
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            return (lat, lng)
    except (ValueError, TypeError):
        pass
    return None


def muat_data_destinasi(path):
    """
    Membaca data destinasi dari sheet metadata di file Excel mentah.
    Returns DataFrame dengan kolom: place_name, category, latitude, longitude
    """
    sheets = {
        'wisata-metadata': 'Wisata',
        'hotel-metadata': 'Hotel',
        'resto-metadata': 'Resto / Kuliner'
    }
    
    semua_data = []
    
    for sheet, kategori in sheets.items():
        df = pd.read_excel(path, sheet_name=sheet)
        
        for _, row in df.iterrows():
            nama = row.get('place-name', '')
            if pd.isna(nama):
                continue
            
            koordinat = parse_lat_long(row.get('lat-long'))
            if koordinat is None:
                continue
            
            semua_data.append({
                'place_name': str(nama).strip(),
                'category': kategori,
                'latitude': koordinat[0],
                'longitude': koordinat[1]
            })
    
    result = pd.DataFrame(semua_data)
    return result


def buat_peta(df, output_path):
    """
    Membuat peta interaktif dengan Folium.
    """
    # Pusat peta di Danau Toba
    peta = folium.Map(
        location=[2.5, 98.9],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Warna marker berdasarkan kategori
    warna_kategori = {
        'Wisata': 'green',
        'Hotel': 'blue',
        'Resto / Kuliner': 'red'
    }
    
    # Tambahkan marker untuk setiap destinasi
    for _, row in df.iterrows():
        warna = warna_kategori.get(row['category'], 'gray')
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(
                "<b>" + row['place_name'] + "</b><br>" + row['category'],
                max_width=250
            ),
            tooltip=row['place_name'],
            icon=folium.Icon(color=warna, icon='info-sign')
        ).add_to(peta)
    
    # Tambahkan layer control
    folium.LayerControl().add_to(peta)
    
    # Simpan ke file HTML
    peta.save(output_path)
    
    print("Peta disimpan:", output_path)
    print("Total marker:", len(df))
    print("- Wisata:", len(df[df['category']=='Wisata']))
    print("- Hotel:", len(df[df['category']=='Hotel']))
    print("- Resto/Kuliner:", len(df[df['category']=='Resto / Kuliner']))


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    
    raw_path = os.path.join(project_root, 'dataset', 'raw', 'Dataset HackathonTourism - IT DEL.xlsx')
    output_path = os.path.join(project_root, 'docs', 'peta_destinasi.html')
    
    print("Memuat data destinasi...")
    df = muat_data_destinasi(raw_path)
    print("Data dimuat:", len(df), "destinasi dengan koordinat valid")
    print()
    
    buat_peta(df, output_path)
    print()
    print("Selesai! Buka docs/peta_destinasi.html di browser.")

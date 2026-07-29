"""
data_loader.py
Memuat semua data yang dibutuhkan backend dari dataset.
"""

import os
import re
import pandas as pd

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DATA_PROCESSED = os.path.join(_PROJECT_ROOT, "dataset", "processed")
_DATA_RAW = os.path.join(_PROJECT_ROOT, "dataset", "raw")
_cache = {}

# Region keywords untuk ekstraksi dari alamat
_REGION_KEYWORDS = {
    "Toba": ["Kec. Balige", "Toba", "Kab. Toba"],
    "Samosir": ["Samosir", "Kec. Pangururan", "Kec. Simanindo"],
    "Simalungun": ["Simalungun", "Kec. Girsang", "Parapat"],
    "Tapanuli Utara": ["Tapanuli Utara", "Taput", "Kec. Siborongborong"],
    "Dairi": ["Dairi", "Kec. Sidikalang"],
    "Karo": ["Karo", "Kec. Kabanjahe", "Kec. Berastagi"],
    "Humbang Hasundutan": ["Humbang", "Kec. Dolok Sanggul"],
    "Pakpak Bharat": ["Pakpak", "Kec. Salak"],
}


def extract_region_from_address(address):
    """Ekstrak kabupaten/kota dari string alamat."""
    if pd.isna(address):
        return None
    addr = str(address)
    for region, keywords in _REGION_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in addr.lower():
                return region
    match = re.search(r"(?:Kabupaten|Kab\.)\s*(\w+)", addr, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    return None


def load_reviews():
    """Memuat dataset review yang sudah dilabeli."""
    if "reviews" in _cache:
        return _cache["reviews"]
    path = os.path.join(_DATA_PROCESSED, "review_labeled.xlsx")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_excel(path)
    _cache["reviews"] = df
    return df


def load_metadata():
    """
    Memuat metadata destinasi (wisata, hotel, resto) + koordinat + region.
    Returns DataFrame: place_name, category, latitude, longitude, region
    """
    if "metadata_with_region" in _cache:
        return _cache["metadata_with_region"]

    raw_path = os.path.join(_DATA_RAW, "Dataset HackathonTourism - IT DEL.xlsx")
    if not os.path.exists(raw_path):
        return pd.DataFrame()

    sheets = {
        "wisata-metadata": "Wisata",
        "hotel-metadata": "Hotel",
        "resto-metadata": "Resto / Kuliner",
    }

    all_data = []
    for sheet, category in sheets.items():
        df = pd.read_excel(raw_path, sheet_name=sheet)
        for _, row in df.iterrows():
            name = row.get("place-name", "")
            if pd.isna(name):
                continue
            lat_long = row.get("lat-long", "")
            if pd.isna(lat_long):
                continue
            try:
                parts = str(lat_long).split(",")
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    addr = row.get("address", "") if "address" in df.columns else ""
                    region = extract_region_from_address(addr)
                    all_data.append({
                        "place_name": str(name).strip(),
                        "category": category,
                        "latitude": lat,
                        "longitude": lng,
                        "region": region,
                    })
            except (ValueError, TypeError):
                continue

    result = pd.DataFrame(all_data)
    _cache["metadata_with_region"] = result
    return result


def get_location_coordinates():
    """Mengembalikan dictionary {place_name: {lat, lng, region}}."""
    meta = load_metadata()
    if meta.empty:
        return {}
    result = {}
    for _, row in meta.iterrows():
        result[row["place_name"]] = {
            "lat": row["latitude"],
            "lng": row["longitude"],
            "region": row.get("region"),
        }
    return result


def get_regions():
    """Mengembalikan daftar region unik."""
    meta = load_metadata()
    if meta.empty:
        return []
    regions = meta["region"].dropna().unique().tolist()
    return sorted(regions)


def clear_cache():
    _cache.clear()

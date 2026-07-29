"""
clean_review.py
Fungsi pembersihan teks dasar untuk preprocessing ulasan wisata.

Langkah-langkah:
1. lowercase
2. hapus URL
3. hapus emoji
4. hapus angka
5. normalisasi slang Indonesia
6. normalisasi kata Batak
7. hapus tanda baca
8. hapus spasi berlebih
9. stopword removal Bahasa Indonesia
10. tokenisasi

Penggunaan:
    from clean_review import clean_review, tokenize
    
    teks_bersih = clean_review("Contoh review dengan URL https://example.com ")
    tokens = tokenize(teks_bersih)
"""

import re
import string
import csv
import os

from nltk.corpus import stopwords


# --- Muat kamus (dijalankan sekali saat import) ---

_script_dir = os.path.dirname(os.path.abspath(__file__))

def _muat_kamus_slang(path):
    """Muat kamus slang dari file CSV."""
    kamus = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slang = row["slang_word"].strip().lower()
            baku = row["standard_indonesian"].strip().lower()
            kamus[slang] = baku
    return kamus

def _muat_kamus_batak(path):
    """Muat kamus Batak dari file CSV."""
    kamus = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batak = row["batak_term"].strip().lower()
            indo = row["indonesian_translation"].strip().lower()
            kamus[batak] = indo
    return kamus

# Kamus global (dimuat sekali saat import)
_KAMUS_SLANG = _muat_kamus_slang(os.path.join(_script_dir, "slang_dictionary.csv"))
_KAMUS_BATAK = _muat_kamus_batak(os.path.join(_script_dir, "batak_dictionary.csv"))

# Stopwords Bahasa Indonesia dari NLTK (dimuat sekali)
_STOPWORDS = set(stopwords.words("indonesian"))

# Kata negasi yang WAJIB dipertahankan — jangan dihapus saat stopword removal.
# Tanpa ini, "tidak ada sampah" jadi "sampah" dan model kehilangan konteks negasi.
_NEGATION_WORDS = {"tidak", "belum", "bukan", "jangan", "tanpa", "tak"}


# --- Fungsi pembersihan ---

def lowercase_text(text):
    """Ubah semua huruf menjadi lowercase."""
    return text.lower()


def remove_url(text):
    """Hapus URL dari teks."""
    url_pattern = r"https?://\S+|www\.\S+"
    return re.sub(url_pattern, "", text)


def remove_emoji(text):
    """Hapus emoji dari teks menggunakan rentang Unicode."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticon
        "\U0001F300-\U0001F5FF"  # Simbol & piktograf
        "\U0001F680-\U0001F6FF"  # Transportasi & simbol
        "\U0001F1E0-\U0001F1FF"  # Bendera
        "\u2702-\u27B0"          # Dingbats
        "\u24C2-\U0001F251"      # Lainnya
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text)


def remove_numbers(text):
    """Hapus angka dari teks."""
    return re.sub(r"\d+", "", text)


def remove_punctuation(text):
    """Hapus tanda baca dari teks."""
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)


def remove_extra_whitespace(text):
    """Hapus spasi berlebih (ganti spasi ganda jadi satu, hapus spasi awal/akhir)."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_slang(text):
    """Ganti kata slang Indonesia dengan kata baku menggunakan word boundary."""
    for slang, baku in _KAMUS_SLANG.items():
        pattern = "\\b" + re.escape(slang) + "\\b"
        text = re.sub(pattern, baku, text)
    return text


def normalize_batak(text):
    """Ganti kata Batak dengan padanan Bahasa Indonesia menggunakan word boundary."""
    for batak, indo in _KAMUS_BATAK.items():
        pattern = "\\b" + re.escape(batak) + "\\b"
        text = re.sub(pattern, indo, text)
    return text


def remove_stopwords(text):
    """
    Hapus stopwords Bahasa Indonesia dari teks.
    
    Kata negasi (tidak, belum, bukan, dll) TETAP dipertahankan karena
    sangat penting untuk klasifikasi sentimen.
    
    Stopwords adalah kata umum yang tidak memiliki makna penting
    (misal: dan, di, ke, yang, dll).
    """
    if not text:
        return text
    words = text.split()
    # Pertahankan negation words meskipun ada di stopword list
    words_filtered = [w for w in words if w not in _STOPWORDS or w in _NEGATION_WORDS]
    return " ".join(words_filtered)


def tokenize(text):
    """
    Tokenisasi: memecah teks menjadi daftar kata (token).
    
    Parameters
    ----------
    text : str
        Teks yang sudah dibersihkan.
    
    Returns
    -------
    list of str
        Daftar token kata.
    """
    if not text:
        return []
    return text.split()


def clean_review(text):
    """
    Fungsi utama: menjalankan semua langkah pembersihan secara berurutan.
    
    Parameters
    ----------
    text : str
        Teks ulasan mentah.
    
    Returns
    -------
    str
        Teks ulasan yang sudah dibersihkan (tanpa stopword).
    """
    if not isinstance(text, str):
        return ""
    
    text = lowercase_text(text)
    text = remove_url(text)
    text = remove_emoji(text)
    text = remove_numbers(text)
    text = normalize_slang(text)
    text = normalize_batak(text)
    text = remove_punctuation(text)
    text = remove_extra_whitespace(text)
    text = remove_stopwords(text)
    
    return text


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    
    print("=" * 60)
    print("CONTOH 1: Pembersihan Dasar")
    print("=" * 60)
    sample1 = "Tempatnya KEREN banget! Kunjungi https://example.com untuk info \U0001F60D\U0001F44D 2 kali liburan disini"
    result1 = clean_review(sample1)
    tokens1 = tokenize(result1)
    print(f"Sebelum : {sample1}")
    print(f"Sesudah : {result1}")
    print(f"Token   : {tokens1}")
    print()
    
    print("=" * 60)
    print("CONTOH 2: Normalisasi Slang")
    print("=" * 60)
    sample2 = "Tp tempatnya bener2 keren bgt, gak ada sampah. recommended!"
    result2 = clean_review(sample2)
    tokens2 = tokenize(result2)
    print(f"Sebelum : {sample2}")
    print(f"Sesudah : {result2}")
    print(f"Token   : {tokens2}")
    print()
    
    print("=" * 60)
    print("CONTOH 3: Normalisasi Batak")
    print("=" * 60)
    sample3 = "Horas! Danau toba di samosir sangat indah, banyak ulos dan sigale-gale."
    result3 = clean_review(sample3)
    tokens3 = tokenize(result3)
    print(f"Sebelum : {sample3}")
    print(f"Sesudah : {result3}")
    print(f"Token   : {tokens3}")

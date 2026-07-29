"""
labeling.py
Pelabelan sentimen dan topik pada ulasan wisata menggunakan aturan rule-based.

Label sentimen: Positif, Netral, Negatif
Label topik: Kebersihan, Pungli, Harga, Layanan, Fasilitas, Akses, Parkir, Keamanan
"""# ============================================================
# KONFIGURASI NEGATION HANDLING
# ============================================================
# Kata negasi Bahasa Indonesia.
# Jika kata negasi muncul dalam `window` kata SEBELUM sebuah keyword,
# maka keyword tersebut dianggap dinegasikan.
#
# Contoh:
#   "tidak ada sampah"  -> "sampah" dinegasikan oleh "tidak"
#   "sampah tidak ada"  -> "sampah" TIDAK dinegasikan (negasi setelah keyword)
# ============================================================

NEGATION_WORDS = ["tidak", "bukan", "jangan", "tanpa", "belum"]


def _is_negated(text, keyword, window=3):
    """
    Memeriksa apakah suatu keyword dinegasikan oleh kata negasi.

    Parameters
    ----------
    text : str
        Teks lengkap yang sudah di-lowercase.
    keyword : str
        Keyword yang diperiksa.
    window : int
        Jumlah kata maksimal sebelum keyword yang dicek.

    Returns
    -------
    bool
        True jika keyword dinegasikan (ada kata negasi dalam window).
    """
    idx = text.find(keyword)
    if idx < 0:
        return False
    # Ambil teks sebelum keyword
    before = text[:idx].strip()
    if not before:
        return False
    # Ambil N kata terakhir sebelum keyword
    words = before.split()
    check_words = words[-window:] if len(words) >= window else words
    for neg in NEGATION_WORDS:
        if neg in check_words:
            return True
    return False


# ============================================================
# KEYWORD SENTIMEN
# ============================================================

KEYWORD_NEGATIF = [
    "buruk", "jelek", "kotor", "jorok", "kumuh", "bau",
    "sampah", "banyak sampah", "mahal", "pungli", "liar", "preman",
    "macet", "rusak", "lubang", "sempit", "gelap",
    "mengecewakan", "kecewa", "sedih", "kasihan",
    "kotor sekali", "sampah berserakan", "bau sampah",
    "mahal sekali", "parkir mahal", "tiket mahal",
    "lambat", "jahat", "kasar",
    "licin", "banjir", "banyak nyamuk", "tidak ada lampu",
    "tidak ada tempat sampah"
]

KEYWORD_POSITIF = [
    "bagus", "indah", "bersih", "nyaman", "recommended",
    "rekomendasi", "direkomendasikan", "mantap", "keren",
    "terbaik", "ramah", "murah", "enak",
    "sejuk", "adem", "asri", "hijau",
    "menarik", "seru", "menyenangkan", "memuaskan",
    "lengkap", "tersedia", "tertata", "rapi",
    "cocok", "pas", "luar biasa", "amazing",
    "pemandangan indah", "pemandangan bagus",
    "view bagus", "pelayanan baik", "fasilitas lengkap",
    "tempat nyaman", "tempat bagus", "tempat bersih",
    "layak", "aman", "terawat"
]


def label_sentimen(text):
    """
    Menentukan label sentimen menggunakan scoring berbasis keyword
    dengan negation handling.

    Logika:
    - Keyword NEGATIF yang TIDAK dinegasikan -> skor negatif +1
    - Keyword NEGATIF yang dinegasikan     -> skor positif +1
      (contoh: "tidak ada sampah" -> "sampah" dinegasikan)
    - Keyword POSITIF yang TIDAK dinegasikan -> skor positif +1
    - Keyword POSITIF yang dinegasikan      -> skor negatif +1
      (contoh: "tidak bersih" -> "bersih" dinegasikan)
    - Jika skor negatif > positif -> "Negatif"
    - Jika skor positif > negatif -> "Positif"
    - Jika imbang atau 0           -> "Netral"

    Returns
    -------
    str
        "Positif", "Netral", atau "Negatif"
    """
    if not isinstance(text, str) or not text.strip():
        return "Netral"

    text = text.lower().strip()

    positive_score = 0
    negative_score = 0

    # Proses keyword NEGATIF
    for kw in KEYWORD_NEGATIF:
        if kw in text:
            if _is_negated(text, kw):
                # "tidak ada sampah" -> sebenarnya positif
                positive_score += 1
            else:
                negative_score += 1

    # Proses keyword POSITIF
    for kw in KEYWORD_POSITIF:
        if kw in text:
            if _is_negated(text, kw):
                # "tidak bersih" -> sebenarnya negatif
                negative_score += 1
            else:
                positive_score += 1

    if negative_score > positive_score:
        return "Negatif"
    elif positive_score > negative_score:
        return "Positif"
    else:
        return "Netral"



# ============================================================
# KEYWORD TOPIK
# ============================================================

KEYWORD_TOPIK = {
    "Kebersihan": [
        "sampah", "kotor", "jorok", "kumuh", "bau",
        "bersih", "tidak bersih", "sampah berserakan",
        "bau sampah", "tempat sampah", "kebersihan",
        "tidak terawat", "kotor sekali"
    ],
    "Pungli": [
        "pungli", "pungutan liar", "preman", "liar",
        "memungut", "dipungut", "biaya masuk",
        "parkir liar", "tiket liar"
    ],
    "Harga": [
        "mahal", "murah", "tiket mahal", "parkir mahal",
        "mahal sekali", "harga", "tarif", "biaya",
        "terjangkau", "ekonomis", "murah meriah",
        "tidak mahal", "harga terjangkau"
    ],
    "Layanan": [
        "pelayanan", "layanan", "ramah", "tidak ramah",
        "petugas", "staff", "pegawai",
        "guide", "pemandu", "sapa",
        "informasi", "customer service"
    ],
    "Fasilitas": [
        "toilet", "kamar mandi", "wc", "mushola",
        "gazebo", "bangku", "tempat duduk",
        "parkiran", "lahan parkir",
        "fasilitas", "lengkap", "tersedia",
        "wifi", "listrik", "air", "tempat sampah",
        "tidak ada fasilitas"
    ],
    "Akses": [
        "jalan", "akses", "lubang", "rusak",
        "macet", "sempit",
        "jalan rusak", "akses jalan",
        "jembatan", "aspal", "berlubang",
        "susah diakses", "mudah diakses"
    ],
    "Parkir": [
        "parkir", "parkiran", "lahan parkir",
        "parkir motor", "parkir mobil",
        "tempat parkir", "luas parkir"
    ],
    "Keamanan": [
        "aman", "tidak aman", "keamanan",
        "lampu", "tidak ada lampu", "gelap",
        "satpam", "pos jaga", "pengawasan",
        "nyamuk", "licin", "banjir",
        "kecelakaan", "resiko"
    ]
}


def label_topik(text):
    """
    Menentukan topik ulasan berdasarkan keyword.
    Menghitung jumlah keyword yang cocok untuk setiap topik,
    lalu pilih topik dengan skor tertinggi.
    """
    if not isinstance(text, str) or not text.strip():
        return "Umum"
    text = text.lower().strip()
    skor = {}
    for topik, keywords in KEYWORD_TOPIK.items():
        jumlah = 0
        for kw in keywords:
            if kw in text:
                jumlah += 1
        if jumlah > 0:
            skor[topik] = jumlah
    if not skor:
        return "Umum"
    return max(skor, key=skor.get)

if __name__ == "__main__":
    print("=" * 60)
    print("UJI COBA SENTIMEN")
    print("=" * 60)
    sample_sentimen = [
        "pantainya bersih indah recommended",
        "banyak sampah kotor sekali",
        "parkir mahal tidak ramah",
        "lumayan bagus tempatnya",
        "danau toba samosir indah",
        "pungli merajalela"
    ]
    for s in sample_sentimen:
        print(f"{s:45} -> {label_sentimen(s)}")
    print()
    print("=" * 60)
    print("UJI COBA TOPIK")
    print("=" * 60)
    sample_topik = [
        "sampah berserakan bau tidak sedap",
        "pungli parkir meresahkan",
        "tiket masuk mahal sekali",
        "pelayanan ramah dan petugas membantu",
        "toilet bersih dan mushola nyaman",
        "jalan berlubang akses sulit",
        "lahan parkir sempit",
        "gelap tidak ada lampu tidak aman"
    ]
    for s in sample_topik:
        sentimen = label_sentimen(s)
        topik = label_topik(s)
        print(f"{s:45} -> {topik:12} | {sentimen}")
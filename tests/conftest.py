"""Shared fixtures and test data for TONDI test suite."""

import sys
import os
import pytest

# Add source paths
_LABELING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "labeling"))
_PREPROC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "preprocessing"))
_MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "models"))
for p in [_LABELING_DIR, _PREPROC_DIR, _MODEL_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def sample_reviews():
    """Sample reviews for comprehensive testing."""
    return {
        # Positive
        "positive_clean": "pantainya bersih indah recommended",
        "positive_service": "pelayanan ramah dan memuaskan",
        "positive_facility": "toilet bersih dan nyaman",
        "positive_road": "jalannya rapi dan bagus",
        "positive_price": "harga murah terjangkau",
        "positive_negated_trash": "tidak ada sampah di sini",

        # Negative
        "negative_trash": "banyak sampah kotor sekali",
        "negative_price": "parkir mahal",
        "negative_road": "jalan rusak berlubang",
        "negative_dark": "gelap tidak ada lampu",
        "negative_service_negated": "tidak ramah",
        "negative_unclean": "tidak bersih",

        # Neutral
        "neutral_plain": "biasa saja",
        "neutral_so_so": "lumayan",
        "neutral_empty": "",
        "neutral_whitespace": "   ",

        # Mixed
        "mixed_indah_tapi_macet": "pemandangan indah tapi jalan macet",
        "mixed_bersih_tapi_mahal": "bersih tapi parkir mahal",
    }


@pytest.fixture
def sample_dirty_texts():
    """Dirty texts for preprocessing test."""
    return [
        (
            "Tempatnya KEREN banget! Kunjungi https://example.com untuk info 😍👍 2 kali",
            "tempatnya keren banget kunjungi info kali"  # expected clean (no URL, emoji, numbers)
        ),
        (
            "Tp tempatnya bener2 keren bgt, gak ada sampah. recommended!",
            "tp tempatnya bener2 keren bgt gak ada sampah recommended"
        ),
    ]


@pytest.fixture
def sample_topic_texts():
    """Sample texts for topic classification testing."""
    return [
        ("sampah berserakan bau tidak sedap", "Kebersihan"),
        ("pungli parkir meresahkan", "Pungli"),
        ("tiket masuk mahal sekali", "Harga"),
        ("pelayanan ramah dan petugas membantu", "Layanan"),
        ("toilet bersih dan mushola nyaman", "Fasilitas"),
        ("jalan berlubang akses sulit", "Akses"),
        ("lahan parkir sempit", "Parkir"),
        ("gelap tidak ada lampu tidak aman", "Keamanan"),
    ]


@pytest.fixture
def expected_model_output_keys():
    """Expected keys in predict_review output."""
    return {"sentiment", "topic", "confidence_sentiment", "confidence_topic"}

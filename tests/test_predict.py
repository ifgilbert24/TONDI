"""Tests for ai/models/predict.py - inference engine."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "models")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "preprocessing")))

import pytest
from predict import predict_review


class TestPredictReview:
    """Test predict_review() function."""

    def test_output_keys(self):
        result = predict_review("pantainya bersih indah sekali")
        expected_keys = {"sentiment", "topic", "confidence_sentiment", "confidence_topic"}
        assert set(result.keys()) == expected_keys

    def test_sentiment_positive(self):
        result = predict_review("pantainya bersih dan indah, recommended!")
        assert result["sentiment"] == "Positif"

    def test_sentiment_negative(self):
        result = predict_review("banyak sampah berserakan, baunya tidak sedap")
        assert result["sentiment"] == "Negatif"

    def test_sentiment_neutral(self):
        result = predict_review("biasa aja")
        assert result["sentiment"] == "Netral"

    def test_confidence_range(self):
        result = predict_review("tempatnya bagus")
        assert 0.0 <= result["confidence_sentiment"] <= 1.0
        assert 0.0 <= result["confidence_topic"] <= 1.0

    def test_empty_input(self):
        result = predict_review("")
        assert result["sentiment"] == "Netral"
        assert result["topic"] == "Umum"
        assert result["confidence_sentiment"] == 0.0

    def test_topic_detection(self):
        result = predict_review("sampah berserakan bau tidak sedap")
        assert result["topic"] == "Kebersihan"

    def test_topic_generic(self):
        result = predict_review("tempatnya bagus")
        assert result["topic"] == "Umum"

    def test_negation_handling(self):
        """
        Negation words (tidak, belum, bukan) sekarang dipertahankan
        saat preprocessing, sehingga model bisa belajar pola negasi.
        'tidak ada sampah' jadi 'tidak sampah' (bukan 'sampah' saja).
        """
        result = predict_review("tidak ada sampah, bersih sekali")
        # Dengan negation preservation, 'tidak' menjadi feature
        # yang bisa dipelajari model sebagai indikator negasi
        assert result["sentiment"] in ("Positif", "Netral"), \
            f"Expected Positif or Netral, got {result['sentiment']}"

    def test_road_positive_prediction(self):
        result = predict_review("jalannya rapi dan bagus")
        assert result["sentiment"] == "Positif"

    def test_road_negative_prediction(self):
        result = predict_review("jalan rusak berlubang")
        assert result["sentiment"] == "Negatif"

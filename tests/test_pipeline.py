"""Tests for ai/pipeline.py - integrated pipeline."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "models")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "preprocessing")))

import pytest
from pipeline import process_single_review, _precompute_anomaly
from anomaly_detection import _group_by_location, _hitung_zscore, _to_json_rows


class TestProcessSingleReview:
    def test_output_structure(self):
        result = process_single_review("pantainya bersih indah")
        assert "review" in result
        assert "sentiment" in result
        assert "topic" in result
        assert "confidence" in result
        assert "anomaly" in result

    def test_sentiment_positive(self):
        result = process_single_review("pantainya bersih indah")
        assert result["sentiment"] == "Positif"

    def test_sentiment_negative(self):
        result = process_single_review("banyak sampah kotor")
        assert result["sentiment"] == "Negatif"

    def test_with_location(self):
        result = process_single_review("bagus", location="Parapat")
        assert result["location"] == "Parapat"

    def test_without_location(self):
        result = process_single_review("bagus")
        assert "location" not in result

    def test_review_truncation(self):
        long_text = "x" * 500
        result = process_single_review(long_text)
        assert len(result["review"]) <= 200


class TestHitungZscore:
    def test_basic(self):
        data = [1, 2, 3, 4, 5]
        scores = _hitung_zscore(data)
        assert len(scores) == 5
        assert abs(scores[2]) < 0.01  # mean (3) should have zscore near 0

    def test_constant_data(self):
        data = [5, 5, 5, 5]
        scores = _hitung_zscore(data)
        assert all(s == 0 for s in scores)

    def test_empty_data(self):
        scores = _hitung_zscore([])
        assert scores == []


class TestGroupByLocation:
    def test_basic_grouping(self):
        import pandas as pd
        df = pd.DataFrame({
            "place-name": ["A", "A", "B"],
            "sentiment": ["Positif", "Negatif", "Positif"],
        })
        result = _group_by_location(df, min_review=1)
        assert len(result) == 2
        a_row = result[result["place-name"] == "A"].iloc[0]
        assert a_row["total_review"] == 2
        assert a_row["negatif"] == 1

    def test_min_review_filter(self):
        import pandas as pd
        df = pd.DataFrame({
            "place-name": ["A", "B", "B"],
            "sentiment": ["Positif", "Negatif", "Positif"],
        })
        result = _group_by_location(df, min_review=2)
        assert len(result) == 1
        assert result.iloc[0]["place-name"] == "B"


class TestToJsonRows:
    def test_basic(self):
        import pandas as pd
        df = pd.DataFrame({
            "place-name": ["A"],
            "negatif_ratio": [0.5],
            "status": ["ANOMALY"],
            "z_score": [2.5],
        })
        rows = _to_json_rows(df, "zscore")
        assert len(rows) == 1
        assert rows[0]["location"] == "A"
        assert rows[0]["negative_ratio"] == 0.5
        assert rows[0]["z_score"] == 2.5

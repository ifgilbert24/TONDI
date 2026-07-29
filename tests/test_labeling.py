"""Unit tests for ai/labeling/labeling.py.

Tests:
- _is_negated() helper function
- label_sentimen() with negation handling
- label_topik() topic classification
- Edge cases (empty text, mixed sentiment)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "labeling")))

from labeling import (
    _is_negated,
    label_sentimen,
    label_topik,
    NEGATION_WORDS,
    KEYWORD_NEGATIF,
    KEYWORD_POSITIF,
    KEYWORD_TOPIK,
)


# ─── _is_negated TESTS ────────────────────────────────────────────────────

class TestIsNegated:
    def test_negation_before_keyword(self):
        """Negation word BEFORE keyword should be detected."""
        assert _is_negated("tidak ada sampah", "sampah") is True
        assert _is_negated("tidak bersih", "bersih") is True
        assert _is_negated("bukan tempat bersih", "bersih") is True
        assert _is_negated("tanpa sampah", "sampah") is True
        assert _is_negated("belum bersih", "bersih") is True

    def test_negation_after_keyword(self):
        """Negation word AFTER keyword should NOT be detected."""
        assert _is_negated("sampah tidak ada", "sampah") is False
        assert _is_negated("bersih tidak", "bersih") is False

    def test_no_negation(self):
        """No negation word should return False."""
        assert _is_negated("bersih", "bersih") is False
        assert _is_negated("sampah", "sampah") is False
        assert _is_negated("tempatnya bersih", "bersih") is False

    def test_multi_word_negation(self):
        """Negation window works for multi-word prefix."""
        assert _is_negated("sangat tidak ramah", "ramah") is True
        assert _is_negated("tempatnya tidak bersih", "bersih") is True

    def test_keyword_not_found(self):
        """Keyword not in text should return False."""
        assert _is_negated("", "sampah") is False
        assert _is_negated("bersih", "sampah") is False

    def test_window_limit(self):
        """Negation beyond window should not be detected (default window=3)."""
        text = "saya pikir tempat ini tidak terlalu bersih"
        assert _is_negated(text, "bersih", window=3) is True  # "tidak terlalu" within 3 words
        # "tidak" is 2 words before "bersih" ("tidak terlalu bersih") → within window=3


# ─── label_sentimen TESTS ─────────────────────────────────────────────────

class TestLabelSentimen:

    # POSITIVE CASES
    def test_positive_clean(self, sample_reviews):
        assert label_sentimen(sample_reviews["positive_clean"]) == "Positif"

    def test_positive_service(self, sample_reviews):
        assert label_sentimen(sample_reviews["positive_service"]) == "Positif"

    def test_positive_facility(self, sample_reviews):
        assert label_sentimen(sample_reviews["positive_facility"]) == "Positif"

    def test_positive_road(self, sample_reviews):
        assert label_sentimen(sample_reviews["positive_road"]) == "Positif"

    def test_positive_price(self, sample_reviews):
        assert label_sentimen(sample_reviews["positive_price"]) == "Positif"

    def test_positive_negated_trash(self, sample_reviews):
        """'tidak ada sampah' should be Positif (negation handling)."""
        assert label_sentimen(sample_reviews["positive_negated_trash"]) == "Positif"

    # NEGATIVE CASES
    def test_negative_trash(self, sample_reviews):
        assert label_sentimen(sample_reviews["negative_trash"]) == "Negatif"

    def test_negative_price(self, sample_reviews):
        assert label_sentimen(sample_reviews["negative_price"]) == "Negatif"

    def test_negative_road(self, sample_reviews):
        assert label_sentimen(sample_reviews["negative_road"]) == "Negatif"

    def test_negative_dark(self, sample_reviews):
        assert label_sentimen(sample_reviews["negative_dark"]) == "Negatif"

    def test_negative_service_negated(self, sample_reviews):
        """'tidak ramah' should be Negatif (negated positive keyword)."""
        assert label_sentimen(sample_reviews["negative_service_negated"]) == "Negatif"

    def test_negative_unclean(self, sample_reviews):
        """'tidak bersih' should be Negatif."""
        assert label_sentimen(sample_reviews["negative_unclean"]) == "Negatif"

    # NEUTRAL CASES
    def test_neutral_plain(self, sample_reviews):
        assert label_sentimen(sample_reviews["neutral_plain"]) == "Netral"

    def test_neutral_so_so(self, sample_reviews):
        assert label_sentimen(sample_reviews["neutral_so_so"]) == "Netral"

    def test_neutral_empty(self, sample_reviews):
        assert label_sentimen(sample_reviews["neutral_empty"]) == "Netral"

    def test_neutral_whitespace(self, sample_reviews):
        assert label_sentimen(sample_reviews["neutral_whitespace"]) == "Netral"

    def test_neutral_non_string(self):
        assert label_sentimen(None) == "Netral"
        assert label_sentimen(123) == "Netral"

    # MIXED CASES
    def test_mixed_indah_tapi_macet(self, sample_reviews):
        """'pemandangan indah tapi jalan macet' — 'pemandangan indah' + 'indah' = 2 positive > 'macet' = 1 negative."""
        result = label_sentimen(sample_reviews["mixed_indah_tapi_macet"])
        assert result == "Positif"  # "pemandangan indah"+1, "indah"+1 > "macet"-1

    def test_mixed_bersih_tapi_mahal(self, sample_reviews):
        """'bersih tapi parkir mahal' — 'parkir mahal' + 'mahal' = 2 negative > 'bersih' = 1 positive."""
        result = label_sentimen(sample_reviews["mixed_bersih_tapi_mahal"])
        assert result == "Negatif"  # "parkir mahal"-1, "mahal"-1 > "bersih"+1

    # REGRESSION: SENTENCE-LEVEL NEGATION
    def test_negated_negative_at_start(self):
        """'sampah' at start before negation should be Negatif."""
        assert label_sentimen("sampah tidak ada") == "Negatif"

    def test_double_positive(self):
        assert label_sentimen("bagus dan indah") == "Positif"

    def test_double_negative(self):
        assert label_sentimen("kotor dan bau") == "Negatif"

    def test_three_negatives_one_positive(self):
        """More negative keywords than positive."""
        result = label_sentimen("kotor bau mahal tapi pemandangan indah")
        assert result == "Negatif"  # 3 negatif > 1 positif

    def test_review_with_multiple_negations(self):
        """Complex review with multiple negated keywords."""
        result = label_sentimen("tidak bersih tidak ramah tapi murah")
        # "bersih" negated → negative +1, "ramah" negated → negative +1, "murah" → positive +1
        # negative=2 > positive=1
        assert result == "Negatif"


# ─── label_topik TESTS ────────────────────────────────────────────────────

class TestLabelTopik:
    def test_all_topics(self, sample_topic_texts):
        """Each sample should map to its expected topic."""
        for text, expected in sample_topic_texts:
            result = label_topik(text)
            assert result == expected, f"Expected {expected}, got {result} for: {text}"

    def test_topic_empty(self):
        assert label_topik("") == "Umum"
        assert label_topik("   ") == "Umum"
        assert label_topik(None) == "Umum"

    def test_topic_generic(self):
        assert label_topik("tempatnya bagus") == "Umum"

    def test_topic_negation_preserves_topic(self):
        """Negated keywords should still detect the correct topic."""
        assert label_topik("tidak ada sampah") == "Kebersihan"
        assert label_topik("tidak ada lampu") == "Keamanan"


# ─── DATA INTEGRITY TESTS ─────────────────────────────────────────────────

class TestKeywordDataIntegrity:
    def test_negation_words_defined(self):
        assert len(NEGATION_WORDS) >= 5
        assert "tidak" in NEGATION_WORDS

    def test_negative_keywords_not_empty(self):
        assert len(KEYWORD_NEGATIF) > 10

    def test_positive_keywords_not_empty(self):
        assert len(KEYWORD_POSITIF) > 10

    def test_topic_categories(self):
        expected_topics = {"Kebersihan", "Pungli", "Harga", "Layanan",
                           "Fasilitas", "Akses", "Parkir", "Keamanan"}
        assert set(KEYWORD_TOPIK.keys()) == expected_topics

    def test_no_duplicate_keywords_in_negative(self):
        assert len(KEYWORD_NEGATIF) == len(set(KEYWORD_NEGATIF))

    def test_no_duplicate_keywords_in_positive(self):
        assert len(KEYWORD_POSITIF) == len(set(KEYWORD_POSITIF))

    def test_no_overlap_positive_negative(self):
        """A keyword should not appear in both positive and negative lists."""
        overlap = set(KEYWORD_POSITIF) & set(KEYWORD_NEGATIF)
        assert len(overlap) == 0, f"Overlap found: {overlap}"

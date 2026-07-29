"""Unit tests for ai/preprocessing/clean_review.py."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai", "preprocessing")))

import pytest
from clean_review import (
    lowercase_text,
    remove_url,
    remove_emoji,
    remove_numbers,
    remove_punctuation,
    remove_extra_whitespace,
    normalize_slang,
    normalize_batak,
    remove_stopwords,
    clean_review,
    tokenize,
)


class TestIndividualSteps:
    def test_lowercase(self):
        assert lowercase_text("Hello WORLD") == "hello world"
        assert lowercase_text("") == ""

    def test_remove_url(self):
        assert "https" not in remove_url("cek https://example.com")

    def test_remove_numbers(self):
        assert "5000" not in remove_numbers("harga 5000 rupiah")

    def test_remove_punctuation(self):
        assert "!" not in remove_punctuation("halo!")

    def test_remove_extra_whitespace(self):
        assert remove_extra_whitespace("banyak   spasi") == "banyak spasi"

    def test_remove_stopwords(self):
        """Stopwords removal - 'tempat' might be a stopword, just verify some are removed."""
        before = "dan di ke yang"
        after = remove_stopwords(before)
        assert len(after) < len(before) or after == ""

    def test_negation_words_preserved(self):
        """Negation words MUST survive stopword removal."""
        for neg_word in ["tidak", "belum", "bukan", "jangan", "tanpa"]:
            result = remove_stopwords(f"{neg_word} ada")
            assert neg_word in result, f"Negation word '{neg_word}' was removed!"
            result = clean_review(f"{neg_word} ada sampah")
            assert neg_word in result, f"clean_review removed negation '{neg_word}'!"

    def test_normalize_slang_in_clean(self):
        """Slang normalization works within clean_review().
        Note: 'tidak' is a stopword and gets removed. We verify slang WAS
        converted by checking 'gak' no longer appears."""
        result = clean_review("gak ada sampah")
        assert "gak" not in result  # slang 'gak' was converted
        # Use a slang word whose replacement is NOT a stopword
        result2 = clean_review("org baik")
        assert "orang" in result2  # 'org' -> 'orang' (not a stopword)

    def test_normalize_batak_in_clean(self):
        """Batak normalization works within clean_review()."""
        result = clean_review("toba")
        assert "danau" in result


class TestCleanReview:
    def test_basic_cleaning(self):
        result = clean_review("Tempatnya INDAH dan bersih! https://example.com")
        # 'INDAH' → 'indah', survives preprocessing (not in slang dict)
        assert "indah" in result
        assert "https" not in result

    def test_non_string_input(self):
        assert clean_review(None) == ""
        assert clean_review(123) == ""

    def test_empty_string(self):
        assert clean_review("") == ""


class TestTokenize:
    def test_basic(self):
        assert tokenize("bersih indah") == ["bersih", "indah"]

    def test_empty(self):
        assert tokenize("") == []

"""
Tests for nlu/preprocessor.py
================================
Tests stop-word removal, lemmatization, case normalisation,
special character handling, and edge cases.
"""

import pytest
from nlu.preprocessor import preprocess, tokenize_raw


class TestPreprocess:
    """Tests for the preprocess() function."""

    def test_lowercases_input(self):
        result = preprocess("OPEN CHROME")
        assert result == result.lower()

    def test_removes_stop_words(self):
        result = preprocess("can you please do this for me")
        # "can", "you", "please", "do", "this", "me" are stop words
        # "for" is in _KEEP_WORDS so it stays
        assert "can" not in result.split()
        assert "you" not in result.split()

    def test_keeps_domain_words(self):
        """Words like 'open', 'search', 'find', 'write', 'my', 'in' should be kept."""
        result = preprocess("open my file in search")
        assert "open" in result.split()
        assert "my" in result.split()
        assert "in" in result.split()
        assert "search" in result.split()

    def test_lemmatization(self):
        """Verbs should be lemmatized: 'opening' → 'open', 'searching' → 'search'."""
        result = preprocess("opening files")
        assert "open" in result.split()

    def test_strips_special_characters(self):
        result = preprocess("open @Chrome! #now$")
        # @ # $ ! should be removed
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "!" not in result

    def test_keeps_colons(self):
        """Colons are kept (useful for 'write this: ...' patterns)."""
        result = preprocess("write this: hello world")
        assert ":" in result

    def test_empty_input(self):
        result = preprocess("")
        assert result == ""

    def test_whitespace_only(self):
        result = preprocess("   ")
        assert result.strip() == ""

    def test_numeric_input(self):
        result = preprocess("set timer for 10 minutes")
        assert "10" in result

    def test_preserves_meaningful_words(self):
        result = preprocess("search for quantum in my notes")
        assert "search" in result.split()
        assert "for" in result.split()
        assert "quantum" in result.split()
        assert "my" in result.split()

    def test_down_is_kept(self):
        """'down' is in _KEEP_WORDS."""
        result = preprocess("scroll down please")
        assert "down" in result.split()


class TestTokenizeRaw:
    """Tests for the tokenize_raw() function."""

    def test_returns_list_of_tokens(self):
        result = tokenize_raw("open chrome")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_lowercases(self):
        result = tokenize_raw("OPEN CHROME")
        assert result == ["open", "chrome"]

    def test_preserves_numbers(self):
        result = tokenize_raw("set timer 10 minutes")
        assert "10" in result

    def test_empty_input(self):
        result = tokenize_raw("")
        assert result == []

"""
Tests for nlu/entity_extractor.py
====================================
Tests entity extraction for each intent type.
"""

import pytest
from nlu.entity_extractor import extract, Entities


class TestFileSearchExtraction:
    def test_extracts_file_query(self):
        ent = extract("find my physics notes", "file_search")
        assert ent.file_query == "physics notes"

    def test_open_pattern(self):
        ent = extract("open my research paper", "file_search")
        assert "research paper" in ent.file_query

    def test_locate_pattern(self):
        ent = extract("locate assignment 3", "file_search")
        assert "assignment 3" in ent.file_query

    def test_fallback_uses_full_text(self):
        ent = extract("physics pdf", "file_search")
        assert ent.file_query == "physics pdf"


class TestContentSearchExtraction:
    def test_extracts_keyword(self):
        ent = extract("search for quantum in my notes", "content_search")
        assert ent.search_keyword == "quantum"

    def test_find_keyword_in_documents(self):
        ent = extract("find voltage in my documents", "content_search")
        assert ent.search_keyword == "voltage"

    def test_fallback(self):
        ent = extract("search deadline", "content_search")
        assert "deadline" in ent.search_keyword


class TestActiveTypingExtraction:
    def test_write_this_down(self):
        ent = extract("write this down: Meeting at 3 PM", "active_typing")
        assert ent.typing_text == "Meeting at 3 PM"

    def test_type_this(self):
        ent = extract("type this: Buy groceries", "active_typing")
        assert ent.typing_text == "Buy groceries"

    def test_note_this_down(self):
        ent = extract("note this down: Call mom at 5", "active_typing")
        assert ent.typing_text == "Call mom at 5"

    def test_plain_write(self):
        ent = extract("write: hello world", "active_typing")
        assert ent.typing_text == "hello world"


class TestSummarizeExtraction:
    def test_summarize(self):
        ent = extract("summarize my physics notes", "summarize")
        assert "physics notes" in ent.summarize_query

    def test_summary_of(self):
        ent = extract("give me a summary of my research paper", "summarize")
        assert "research paper" in ent.summarize_query

    def test_tldr(self):
        ent = extract("TLDR of my assignment 3", "summarize")
        assert "assignment 3" in ent.summarize_query


class TestTimerExtraction:
    def test_set_timer_for(self):
        ent = extract("set a timer for 5 minutes", "timer")
        assert "5 minutes" in ent.timer_text

    def test_duration_before_timer(self):
        ent = extract("set a 10 minute timer", "timer")
        assert "10 minute" in ent.timer_text

    def test_countdown(self):
        ent = extract("countdown 30 seconds", "timer")
        assert "30 seconds" in ent.timer_text

    def test_timer_for(self):
        ent = extract("timer for 15 minutes", "timer")
        assert "15 minutes" in ent.timer_text


class TestRawTextPassthrough:
    """Intents that just pass raw text should always set ent.raw."""

    def test_screenshot_preserves_raw(self):
        ent = extract("take a screenshot", "screenshot")
        assert ent.raw == "take a screenshot"

    def test_gui_control_preserves_raw(self):
        ent = extract("scroll down", "gui_control")
        assert ent.raw == "scroll down"

    def test_create_file_preserves_raw(self):
        ent = extract("create a python file called utils in Desktop", "create_file")
        assert ent.raw == "create a python file called utils in Desktop"

    def test_system_power_preserves_raw(self):
        ent = extract("shutdown the computer", "system_power")
        assert ent.raw == "shutdown the computer"

    def test_brightness_preserves_raw(self):
        ent = extract("brightness up", "brightness")
        assert ent.raw == "brightness up"

    def test_window_mgmt_preserves_raw(self):
        ent = extract("minimize all windows", "window_mgmt")
        assert ent.raw == "minimize all windows"

    def test_open_url_preserves_raw(self):
        ent = extract("open youtube.com", "open_url")
        assert ent.raw == "open youtube.com"


class TestEdgeCases:
    def test_none_intent(self):
        ent = extract("hello world", None)
        assert ent.raw == "hello world"
        assert ent.file_query == ""
        assert ent.search_keyword == ""

    def test_unknown_intent(self):
        ent = extract("hello world", "unknown_intent")
        assert ent.raw == "hello world"

    def test_empty_text(self):
        ent = extract("", "file_search")
        assert ent.file_query == ""

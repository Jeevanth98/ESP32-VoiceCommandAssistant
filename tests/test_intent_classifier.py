"""
Tests for nlu/intent_classifier.py
=====================================
Tests model loading, classification of known intents,
confidence thresholding, and garbage rejection.

NOTE: These tests require a trained model at models/intent_model.joblib.
Run `python generate_data.py && python -m nlu.intent_classifier train` first.
"""

import pytest
import os

# Skip all tests if no trained model exists
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "intent_model.joblib")
pytestmark = pytest.mark.skipif(
    not os.path.isfile(MODEL_PATH),
    reason="Trained model not found — run training first",
)

from nlu.intent_classifier import classify_intent
from nlu.preprocessor import preprocess


class TestClassifyIntent:
    """Tests for the classify_intent() function."""

    # ── Known intents should classify correctly ──────────────────────────

    def test_open_app(self):
        intent, conf = classify_intent(preprocess("open chrome"))
        assert intent == "open_app"
        assert conf > 0.3

    def test_close_app(self):
        intent, conf = classify_intent(preprocess("close notepad"))
        assert intent == "close_app"
        assert conf > 0.3

    def test_file_search(self):
        intent, conf = classify_intent(preprocess("find my physics notes"))
        assert intent == "file_search"
        assert conf > 0.3

    def test_content_search(self):
        intent, conf = classify_intent(preprocess("search for quantum in my notes"))
        assert intent == "content_search"
        assert conf > 0.3

    def test_summarize(self):
        intent, conf = classify_intent(preprocess("summarize my research paper"))
        assert intent == "summarize"
        assert conf > 0.3

    def test_web_search(self):
        intent, conf = classify_intent(preprocess("what is photosynthesis"))
        assert intent == "web_search"
        assert conf > 0.3

    def test_screenshot(self):
        intent, conf = classify_intent(preprocess("take a screenshot"))
        assert intent == "screenshot"
        assert conf > 0.3

    def test_timer(self):
        intent, conf = classify_intent(preprocess("set a timer for 5 minutes"))
        assert intent == "timer"
        assert conf > 0.3

    def test_active_typing(self):
        intent, conf = classify_intent(preprocess("write this down meeting at 3"))
        assert intent == "active_typing"
        assert conf > 0.3

    def test_system_info(self):
        intent, conf = classify_intent(preprocess("what is my cpu usage"))
        assert intent == "system_info"
        assert conf > 0.3

    def test_gui_control(self):
        intent, conf = classify_intent(preprocess("scroll down"))
        assert intent == "gui_control"
        assert conf > 0.3

    # ── New intents ──────────────────────────────────────────────────────

    def test_create_file(self):
        intent, conf = classify_intent(preprocess("create a python file called utils in desktop"))
        assert intent == "create_file"
        assert conf > 0.3

    def test_system_power(self):
        intent, conf = classify_intent(preprocess("lock the screen"))
        assert intent == "system_power"
        assert conf > 0.3

    def test_brightness(self):
        intent, conf = classify_intent(preprocess("increase brightness"))
        assert intent == "brightness"
        assert conf > 0.3

    def test_window_mgmt(self):
        intent, conf = classify_intent(preprocess("minimize all windows"))
        assert intent == "window_mgmt"
        assert conf > 0.3

    def test_open_url(self):
        intent, conf = classify_intent(preprocess("go to youtube.com"))
        assert intent == "open_url"
        assert conf > 0.3

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_empty_string_returns_none(self):
        intent, conf = classify_intent("")
        assert intent is None
        assert conf == 0.0

    def test_whitespace_returns_none(self):
        intent, conf = classify_intent("   ")
        assert intent is None
        assert conf == 0.0

    def test_returns_tuple(self):
        result = classify_intent(preprocess("hello"))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_confidence_is_float(self):
        _, conf = classify_intent(preprocess("open chrome"))
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

# Testing & Evaluation Guide

This guide explains how to test and evaluate the ESP32 Voice Command Assistant's NLU (Natural Language Understanding) pipeline.

## Quick Start

### Run All Tests & Evaluations

```bash
python run_tests.py
```

This comprehensive script will:
1. ✅ Check all dependencies
2. ✅ Verify NLTK data is downloaded
3. ✅ Confirm training artifacts exist
4. ✅ Run unit tests (pytest)
5. ✅ Evaluate model performance
6. ✅ Provide summary and recommendations

## Individual Scripts

### 1. Model Performance Evaluation

```bash
python evaluate_model.py
```

**What it does:**
- Cross-validation accuracy (5-fold)
- Per-intent precision, recall, F1-score
- Overall classification accuracy
- Training data distribution analysis
- Misclassification analysis
- Confidence score distribution
- Actionable recommendations

**Expected Output:**
- 99%+ accuracy indicates excellent performance
- 95-99% accuracy indicates good performance
- <95% accuracy needs improvement

### 2. Improvement Suggestions

```bash
python suggest_improvements.py
```

**What it does:**
- Analyzes training data quality
- Checks class balance
- Examines vocabulary richness
- Identifies intent overlap/confusion risks
- Suggests hyperparameter tuning
- Recommends data augmentation strategies
- Proposes advanced techniques

**Use this when:**
- Accuracy is below desired threshold
- You want to optimize the model further
- Planning to add new intents

### 3. Unit Tests Only

```bash
pytest -v
```

**What it tests:**
- Preprocessor (stop-word removal, lemmatization)
- Entity extractor (regex patterns)
- Intent classifier (classification accuracy)
- Command handlers (individual tests)

**Options:**
```bash
# Run specific test file
pytest tests/test_intent_classifier.py -v

# Run with coverage
pytest --cov=nlu --cov=commands --cov-report=html

# Run in quiet mode
pytest -q
```

## Understanding Results

### Accuracy Metrics

- **Precision**: Of all predictions for an intent, how many were correct?
  - High precision = few false positives
  
- **Recall**: Of all actual samples for an intent, how many were correctly identified?
  - High recall = few false negatives
  
- **F1-Score**: Harmonic mean of precision and recall
  - Balanced metric (0 to 1, higher is better)

### Confidence Threshold

The system uses `INTENT_CONFIDENCE_THRESHOLD = 0.30` (from `config.py`).

- Predictions below this threshold return "I'm not confident enough"
- Adjust this based on your preference:
  - **Lower (0.20)**: More responsive, but more errors
  - **Higher (0.50)**: Fewer errors, but more rejections

### Common Issues & Solutions

#### Issue: Low accuracy on specific intents

**Solution:**
1. Check training data distribution (`evaluate_model.py`)
2. Add more diverse examples for that intent
3. Re-run `python generate_data.py` with updated templates
4. Retrain: `python -m nlu.intent_classifier train`

#### Issue: Intent confusion (e.g., "open_app" vs "open_url")

**Solution:**
1. Run `suggest_improvements.py` to identify overlapping keywords
2. Add more distinguishing examples
3. Consider adding keyword overrides in `main.py`

#### Issue: Low confidence predictions

**Solution:**
1. Check confidence distribution in `evaluate_model.py`
2. If many predictions are <50%, review training data quality
3. Add more training samples
4. Consider lowering `INTENT_CONFIDENCE_THRESHOLD` in `config.py`

## Retraining the Model

After making changes to training data:

```bash
# 1. Regenerate training data (if you modified generate_data.py)
python generate_data.py

# 2. Retrain the model
python -m nlu.intent_classifier train

# 3. Evaluate new performance
python evaluate_model.py

# 4. Run full test suite
python run_tests.py
```

## Adding New Intents

1. **Update `generate_data.py`:**
   - Add templates for the new intent
   - Add to `INTENTS` list

2. **Create command handler:**
   - Add `commands/new_intent.py`
   - Implement `execute()` function

3. **Update `main.py`:**
   - Add to `COMMAND_MAP`
   - Optionally add keyword override

4. **Update entity extractor:**
   - Add extraction logic in `nlu/entity_extractor.py`

5. **Retrain and test:**
   ```bash
   python generate_data.py
   python -m nlu.intent_classifier train
   python run_tests.py
   ```

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Overall Accuracy | >95% | 99.59% ✅ |
| Per-intent F1 | >0.90 | Check with `evaluate_model.py` |
| Confidence (mean) | >70% | Check with `evaluate_model.py` |
| Test Coverage | >80% | Run `pytest --cov` |

## Continuous Improvement

1. **Collect real-world usage data**
   - Log commands users type
   - Identify common misclassifications

2. **Iterative refinement**
   - Add misclassified examples to training data
   - Retrain periodically

3. **Monitor metrics**
   - Run `evaluate_model.py` after each retraining
   - Track accuracy trends over time

## Troubleshooting

### Tests fail with "Model not found"
```bash
python generate_data.py
python -m nlu.intent_classifier train
```

### Tests fail with "NLTK data not found"
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### ImportError for packages
```bash
pip install -r requirements.txt
```

### Pytest not found
```bash
pip install pytest pytest-cov
```

## Next Steps

After successful testing:

1. ✅ **Run the assistant**: `python main.py`
2. ✅ **Test with natural commands**: Try various phrasings
3. ✅ **Monitor real-world accuracy**: Note any misclassifications
4. ✅ **Iterate**: Add examples, retrain, evaluate
5. ✅ **Consider Phase 3**: ESP32 integration with Whisper STT

---

For more information, see the main [README.md](README.md).

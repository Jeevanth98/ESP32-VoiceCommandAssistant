"""
Test Web Search Improvements
=============================
Tests the improved web search recognition for short queries like "search vit".

Run: python test_web_search_fix.py
"""

from nlu.preprocessor import preprocess
from nlu.intent_classifier import classify_intent
from main import _keyword_override, COMMAND_MAP
from nlu.entity_extractor import extract

def test_web_search_cases():
    """Test various web search query formats."""
    
    print("="*70)
    print("Testing Web Search Recognition")
    print("="*70)
    print()
    
    test_cases = [
        # Short queries (the problem case)
        "search vit",
        "search python",
        "google java",
        "search docker",
        
        # Medium queries
        "search machine learning",
        "google quantum physics",
        "look up data structures",
        
        # Long queries (already working)
        "search what is vit",
        "search how to learn python",
        "google who invented java",
        "what is machine learning",
        "how to use docker",
        
        # Edge cases
        "search",  # No query
        "vit",     # Just the query word
    ]
    
    results = []
    
    for raw_text in test_cases:
        print(f"Testing: \"{raw_text}\"")
        print("-" * 60)
        
        # Step 1: Check keyword override
        override = _keyword_override(raw_text)
        if override:
            print(f"  ✅ Keyword override: {override}")
            intent = override
            confidence = 1.0  # Keyword overrides have 100% confidence
        else:
            # Step 2: Try NLU classifier
            cleaned = preprocess(raw_text)
            intent, confidence = classify_intent(cleaned)
            print(f"  🧠 NLU classifier: {intent} (confidence: {confidence:.2%})")
        
        # Step 3: Extract entities
        entities = extract(raw_text, intent)
        
        # Step 4: Test command execution (dry run)
        if intent == "web_search":
            from commands.web_search import extract_query
            query = extract_query(raw_text)
            print(f"  📝 Extracted query: \"{query}\"")
            results.append(("✅ PASS", raw_text, intent, query))
        elif intent is None:
            print(f"  ⚠️  Low confidence - would reject")
            results.append(("⚠️  WARN", raw_text, "rejected", "N/A"))
        else:
            print(f"  ❌ Misclassified as: {intent}")
            results.append(("❌ FAIL", raw_text, intent, "N/A"))
        
        print()
    
    # Summary
    print("="*70)
    print("Summary")
    print("="*70)
    print()
    
    passed = sum(1 for r in results if r[0] == "✅ PASS")
    warned = sum(1 for r in results if r[0] == "⚠️  WARN")
    failed = sum(1 for r in results if r[0] == "❌ FAIL")
    
    print(f"Results: {passed} passed, {warned} warnings, {failed} failed")
    print()
    
    if failed > 0:
        print("Failed cases:")
        for status, text, intent, query in results:
            if status == "❌ FAIL":
                print(f"  • \"{text}\" → misclassified as {intent}")
        print()
    
    if warned > 0:
        print("Warning cases (low confidence):")
        for status, text, intent, query in results:
            if status == "⚠️  WARN":
                print(f"  • \"{text}\" → {intent}")
        print()
    
    if passed == len(test_cases):
        print("🎉 All tests passed!")
    elif passed >= len(test_cases) - warned:
        print("✅ All valid tests passed (some low confidence warnings expected)")
    else:
        print("⚠️  Some tests failed. Review output above.")
    
    print()
    
    # Recommendations
    print("="*70)
    print("Recommendations")
    print("="*70)
    print()
    
    if failed > 0 or warned > 3:
        print("If you see failures or many warnings:")
        print("  1. Regenerate training data with updated examples:")
        print("     python generate_data.py")
        print()
        print("  2. Retrain the model:")
        print("     python -m nlu.intent_classifier train")
        print()
        print("  3. Re-run this test:")
        print("     python test_web_search_fix.py")
    else:
        print("✅ Web search recognition is working well!")
        print("   The keyword override catches most cases instantly.")
        print("   The NLU model provides backup for edge cases.")
    
    print()


if __name__ == "__main__":
    try:
        print()
        print("Web Search Recognition Test")
        print("This tests if short queries like 'search vit' are recognized correctly.")
        print()
        
        test_web_search_cases()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

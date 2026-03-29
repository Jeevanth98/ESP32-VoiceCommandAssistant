"""
Complete Test and Evaluation Runner
====================================
Runs all tests and evaluations for the ESP32 Voice Command Assistant.

This script:
1. Checks dependencies
2. Runs pytest test suite
3. Runs model evaluation
4. Provides summary and recommendations

Usage:
    python run_tests.py
"""

import sys
import os
import subprocess

def print_banner(text):
    """Print a formatted banner."""
    width = 70
    print()
    print("="*width)
    print(text.center(width))
    print("="*width)
    print()

def check_dependencies():
    """Check if required packages are installed."""
    print_banner("Checking Dependencies")
    
    required = [
        "nltk", "sklearn", "joblib", "pandas", "pytest",
        "transformers", "torch", "thefuzz", "PyPDF2",
        "pyautogui", "psutil"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT FOUND")
            missing.append(package)
    
    if missing:
        print()
        print("⚠️  Missing packages detected!")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print()
    print("✅ All dependencies installed")
    return True

def check_nltk_data():
    """Ensure NLTK data is downloaded."""
    print_banner("Checking NLTK Data")
    
    try:
        import nltk
        required_data = ['punkt', 'stopwords', 'wordnet']
        
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}' if data == 'punkt' else f'corpora/{data}')
                print(f"✅ {data}")
            except LookupError:
                print(f"⬇️  Downloading {data}...")
                nltk.download(data, quiet=True)
                print(f"✅ {data} downloaded")
        
        print()
        print("✅ NLTK data ready")
        return True
    except Exception as e:
        print(f"❌ Error checking NLTK data: {e}")
        return False

def check_training_artifacts():
    """Check if training data and model exist."""
    print_banner("Checking Training Artifacts")
    
    data_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")
    model_path = os.path.join(os.path.dirname(__file__), "models", "intent_model.joblib")
    
    data_exists = os.path.isfile(data_path)
    model_exists = os.path.isfile(model_path)
    
    print(f"Training data: {'✅ Found' if data_exists else '❌ Missing'}")
    print(f"Trained model: {'✅ Found' if model_exists else '❌ Missing'}")
    
    if not data_exists or not model_exists:
        print()
        print("⚠️  Training artifacts missing!")
        if not data_exists:
            print("   Generate data: python generate_data.py")
        if not model_exists:
            print("   Train model: python -m nlu.intent_classifier train")
        return False
    
    print()
    print("✅ Training artifacts present")
    return True

def run_pytest():
    """Run the pytest test suite."""
    print_banner("Running Pytest Test Suite")
    
    try:
        # Run pytest with verbose output
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            cwd=os.path.dirname(__file__) or ".",
            capture_output=False,
            text=True,
        )
        
        print()
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("⚠️  Some tests failed. Review output above.")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def run_model_evaluation():
    """Run the model evaluation script."""
    print_banner("Running Model Evaluation")
    
    try:
        # Import and run evaluation
        from evaluate_model import evaluate_model
        evaluate_model()
        return True
    except Exception as e:
        print(f"❌ Error during model evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_summary(results):
    """Show final summary of all checks and tests."""
    print_banner("Summary")
    
    all_passed = all(results.values())
    
    for step, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {step}")
    
    print()
    if all_passed:
        print("🎉 All checks and tests completed successfully!")
        print()
        print("Next steps:")
        print("  • Run the assistant: python main.py")
        print("  • Test with natural language commands")
        print("  • Monitor accuracy in real-world usage")
    else:
        print("⚠️  Some checks or tests failed.")
        print("   Review the output above for details and recommendations.")
    
    print()
    return all_passed

def main():
    """Main execution flow."""
    print_banner("ESP32 Voice Command Assistant - Test Suite")
    
    results = {}
    
    # Step 1: Check dependencies
    results["Dependencies"] = check_dependencies()
    if not results["Dependencies"]:
        print("\n❌ Cannot proceed without required packages.")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    # Step 2: Check NLTK data
    results["NLTK Data"] = check_nltk_data()
    if not results["NLTK Data"]:
        print("\n❌ NLTK data check failed.")
        return False
    
    # Step 3: Check training artifacts
    results["Training Artifacts"] = check_training_artifacts()
    if not results["Training Artifacts"]:
        print("\n❌ Cannot run tests without training data and model.")
        return False
    
    # Step 4: Run pytest
    results["Unit Tests"] = run_pytest()
    
    # Step 5: Run model evaluation
    results["Model Evaluation"] = run_model_evaluation()
    
    # Show summary
    return show_summary(results)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

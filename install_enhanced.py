#!/usr/bin/env python3
"""
Installation helper for enhanced product extractor
Installs required and optional dependencies
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed: {description}")
        return False

def main():
    print("Enhanced Product Extractor - Installation Helper")
    print("="*60)
    
    # Core dependencies
    print("\n📦 Installing core dependencies...")
    core_deps = [
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.20.0",  # For faster fuzzy matching
        "numpy>=1.24.0",
        "python-dateutil>=2.8.0"
    ]
    
    cmd = f"{sys.executable} -m pip install " + " ".join(f'"{dep}"' for dep in core_deps)
    run_command(cmd, "Installing core dependencies")
    
    # Optional dependencies
    print("\n📦 Installing optional dependencies...")
    
    # NLP support
    if input("\n🤔 Install spaCy for NLP support? (recommended) [y/N]: ").lower() == 'y':
        run_command(f"{sys.executable} -m pip install spacy>=3.5.0", "Installing spaCy")
        run_command(f"{sys.executable} -m spacy download en_core_web_sm", "Downloading spaCy English model")
    
    # JavaScript rendering
    print("\n🌐 JavaScript rendering options:")
    print("1. Playwright (recommended)")
    print("2. Selenium")
    print("3. Both")
    print("4. Skip")
    
    js_choice = input("Choose option [1-4]: ").strip()
    
    if js_choice in ['1', '3']:
        if run_command(f"{sys.executable} -m pip install playwright>=1.30.0", "Installing Playwright"):
            run_command("playwright install chromium", "Installing Chromium browser")
            run_command("playwright install-deps", "Installing browser dependencies")
    
    if js_choice in ['2', '3']:
        run_command(f"{sys.executable} -m pip install selenium>=4.8.0", "Installing Selenium")
        print("\n⚠️  Note: You'll need to download ChromeDriver separately")
        print("   Visit: https://chromedriver.chromium.org/")
    
    # Embeddings for classification
    if input("\n🤔 Install sentence-transformers for better classification? [y/N]: ").lower() == 'y':
        run_command(f"{sys.executable} -m pip install sentence-transformers>=2.2.0", "Installing sentence-transformers")
    
    # Create cache directory
    cache_dir = ".cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        print(f"\n✅ Created cache directory: {cache_dir}")
    
    # Test imports
    print("\n🧪 Testing imports...")
    test_passed = True
    
    try:
        import requests
        import bs4
        import fuzzywuzzy
        print("✅ Core dependencies OK")
    except ImportError as e:
        print(f"❌ Core dependency error: {e}")
        test_passed = False
    
    try:
        import spacy
        print("✅ spaCy OK")
    except ImportError:
        print("⚠️  spaCy not installed (optional)")
    
    try:
        import playwright
        print("✅ Playwright OK")
    except ImportError:
        print("⚠️  Playwright not installed (optional)")
    
    try:
        import selenium
        print("✅ Selenium OK")
    except ImportError:
        print("⚠️  Selenium not installed (optional)")
    
    try:
        import sentence_transformers
        print("✅ Sentence transformers OK")
    except ImportError:
        print("⚠️  Sentence transformers not installed (optional)")
    
    print("\n" + "="*60)
    if test_passed:
        print("✅ Installation complete! You can now run:")
        print("   python extract_products_enhanced.py companies.json")
    else:
        print("❌ Some core dependencies failed. Please check the errors above.")
    
    print("\n💡 Quick start:")
    print("   python extract_products_enhanced.py companies.json --js auto --limit 10")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Sample test script for the Healthcare URL Validator
This script tests a small subset of URLs so you can quickly verify the system works.
"""

import asyncio
import url_validator

# Test URLs - just a few to start
SAMPLE_URLS = [
    "https://www.acalta.de",
    "https://www.actimi.com", 
    "https://www.emmora.de",
    "https://www.alfa-ai.com",
    "https://www.apheris.com"
]

def main():
    """Run a quick test with a few sample URLs."""
    print("Healthcare URL Validator - Sample Test")
    print("=" * 45)
    print(f"Testing {len(SAMPLE_URLS)} sample URLs...")
    print()
    
    # Validate the sample URLs
    results = url_validator.clean_and_validate_urls(SAMPLE_URLS)
    
    # Print results
    print("\n" + "="*60)
    print("SAMPLE TEST RESULTS")
    print("="*60)
    
    live_count = sum(1 for r in results if r['is_live'])
    healthcare_count = sum(1 for r in results if r.get('is_live') and r.get('is_healthcare'))
    
    print(f"Total URLs tested: {len(results)}")
    print(f"Live URLs: {live_count}")
    print(f"Healthcare-related URLs: {healthcare_count}")
    print()
    
    print("Detailed results:")
    for result in results:
        status = "✅ LIVE" if result['is_live'] else "❌ DOWN"
        healthcare = "🏥 HEALTHCARE" if result.get('is_healthcare') else "🏢 OTHER"
        print(f"  {status} {healthcare} - {result['url']}")
        if result.get('title'):
            print(f"    Title: {result['title'][:60]}...")
        if result.get('error'):
            print(f"    Error: {result['error']}")
        print()
    
    print("✨ Sample test completed successfully!")
    print("To run the full validation with all URLs and discovery, use: python main.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("\n⚠️  Event loop conflict detected.")
            print("Please run this script in a regular Python environment:")
            print("  python test_sample.py")
        else:
            print(f"❌ Error: {e}")
            print("Please check your setup and try again.")
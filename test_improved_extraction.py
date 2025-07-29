#!/usr/bin/env python3
"""
Test script to demonstrate improved product extraction
"""

import json
from extract_product_names import ProductExtractor

# Test URLs that were problematic
test_urls = [
    {
        "company_name": "Nutrio",
        "url": "https://shop.getnutrio.com/",
        "expected": ["Nutrio App", "aurora nutrio"]
    },
    {
        "company_name": "VisionCheckout",
        "url": "https://visioncheckout.com/",
        "expected": ["auvisus"]
    }
]

def test_extraction():
    extractor = ProductExtractor()
    
    print("Testing Improved Product Extraction")
    print("=" * 60)
    
    for test_case in test_urls:
        print(f"\nTesting: {test_case['company_name']} ({test_case['url']})")
        print("-" * 40)
        
        # Extract products
        results = extractor.extract_products_from_page(test_case['url'])
        
        print(f"Found products: {results['found_products']}")
        print(f"Product types: {results['product_types']}")
        print(f"Extraction methods: {results['extraction_methods']}")
        print(f"Expected: {test_case['expected']}")
        
        # Check if we found the expected products
        found_expected = [p for p in test_case['expected'] if any(
            p.lower() in found.lower() or found.lower() in p.lower() 
            for found in results['found_products']
        )]
        
        print(f"Success rate: {len(found_expected)}/{len(test_case['expected'])}")
        
        # Show what would be excluded
        print("\nFiltering demonstration:")
        
        # Simulate some junk that would be filtered out
        test_strings = [
            "Der autonome Self-Checkoutfür Ihre Kantine",
            "Unser einzigartiges Servicekonzept", 
            "Prozessoptimierung",
            "Nutrio App",  # This should pass
            "Contact Us",
            "Mehr erfahren",
            "auvisus Platform"  # This should pass
        ]
        
        for test_str in test_strings:
            is_valid = extractor._is_valid_product_name(test_str)
            print(f"  '{test_str}' -> {'✓ VALID' if is_valid else '✗ FILTERED'}")

if __name__ == "__main__":
    test_extraction()
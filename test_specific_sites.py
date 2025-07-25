#!/usr/bin/env python3
"""
Test specific sites to debug product extraction issues
"""

import json
from extract_products_enhanced_v4 import EnhancedProductExtractorV4

# Problematic sites to test
TEST_SITES = [
    {"url": "https://www.apheris.com", "company_name": "apheris AI GmbH", "expected": ["apheris", "Apheris Platform"]},
    {"url": "https://www.alfa-ai.com", "company_name": "ALFA AI GmbH", "expected": ["ALFA AI"]},
    {"url": "https://www.emmora.de", "company_name": "Ahorn AG", "expected": ["Emmora"]},
]

def test_site(site_data, extractor):
    """Test a single site and show detailed extraction results"""
    print(f"\n{'='*80}")
    print(f"Testing: {site_data['company_name']} - {site_data['url']}")
    print(f"Expected products: {site_data['expected']}")
    print(f"{'='*80}")
    
    # Extract products
    result = extractor.extract_all_products(site_data['url'], site_data['company_name'])
    
    # Show results
    print(f"\nExtracted {len(result['products'])} products:")
    for i, product in enumerate(result['products'], 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Type: {product['type']}")
        print(f"   Confidence: {product['confidence']:.2f}")
        print(f"   Method: {product['method']}")
        print(f"   Ground Truth: {product.get('is_ground_truth', False)}")
    
    # Check against expected
    found_names = [p['name'] for p in result['products']]
    print(f"\nExpected vs Found:")
    for expected in site_data['expected']:
        if any(expected.lower() in found.lower() or found.lower() in expected.lower() for found in found_names):
            print(f"  ✅ {expected}")
        else:
            print(f"  ❌ {expected} (MISSING)")
    
    # Show extraction methods used
    print(f"\nExtraction methods: {', '.join(result['methods'])}")
    print(f"Pages scraped: {result['pages_scraped']}")
    
    return result

def main():
    print("Testing Product Extractor V4 on Problematic Sites")
    print("Debug mode enabled to see filtering decisions")
    
    # Create extractor with debug mode
    extractor = EnhancedProductExtractorV4(
        timeout=30,
        use_js='auto',
        debug=True
    )
    
    # Test each site
    all_results = []
    for site in TEST_SITES:
        result = test_site(site, extractor)
        all_results.append({
            'site': site,
            'result': result
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    total_expected = sum(len(site['expected']) for site in TEST_SITES)
    total_found = sum(len(r['result']['products']) for r in all_results)
    
    print(f"Total expected products: {total_expected}")
    print(f"Total found products: {total_found}")
    print(f"Success rate: {total_found/total_expected*100:.1f}%")
    
    # Save detailed results
    with open('test_results_debug.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\nDetailed results saved to test_results_debug.json")

if __name__ == "__main__":
    main()
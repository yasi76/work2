#!/usr/bin/env python3
"""
Compare outputs from different product extractor versions
"""

import json
import sys
from collections import defaultdict

def load_results(filename):
    """Load extraction results from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'results' in data:
        return data['results']
    else:
        # Assume it's a list of results directly
        return data

def compare_by_url(results1, results2):
    """Compare two sets of results by URL"""
    # Create URL-indexed dicts
    r1_by_url = {r['url']: r for r in results1 if 'url' in r}
    r2_by_url = {r['url']: r for r in results2 if 'url' in r}
    
    all_urls = sorted(set(r1_by_url.keys()) | set(r2_by_url.keys()))
    
    print(f"\n{'='*100}")
    print(f"PRODUCT EXTRACTION COMPARISON")
    print(f"{'='*100}")
    print(f"File 1: {len(results1)} companies")
    print(f"File 2: {len(results2)} companies")
    print(f"{'='*100}\n")
    
    improvements = 0
    regressions = 0
    
    for url in all_urls:
        r1 = r1_by_url.get(url, {})
        r2 = r2_by_url.get(url, {})
        
        company = r1.get('company_name') or r2.get('company_name', 'Unknown')
        
        # Get product counts
        count1 = r1.get('products_found', 0)
        count2 = r2.get('products_found', 0)
        
        # Get product names
        names1 = r1.get('product_names', [])
        names2 = r2.get('product_names', [])
        
        # Check for GT match
        gt1 = r1.get('has_ground_truth', False)
        gt2 = r2.get('has_ground_truth', False)
        
        # Determine if improved/regressed
        status = ""
        if count2 > count1:
            status = "✅ IMPROVED"
            improvements += 1
        elif count2 < count1:
            status = "⚠️  REGRESSED"
            regressions += 1
        elif gt2 and not gt1:
            status = "✅ GT MATCH"
            improvements += 1
        else:
            status = "➖ SAME"
        
        print(f"{status} {company}")
        print(f"  URL: {url}")
        print(f"  V1: {count1} products - {', '.join(names1[:3])}")
        print(f"  V2: {count2} products - {', '.join(names2[:3])}")
        
        if gt2:
            print(f"  ✓ Ground truth matched")
        
        # Show new products found
        new_products = [n for n in names2 if n not in names1]
        if new_products:
            print(f"  + New: {', '.join(new_products[:3])}")
        
        # Show lost products
        lost_products = [n for n in names1 if n not in names2]
        if lost_products:
            print(f"  - Lost: {', '.join(lost_products[:3])}")
        
        print()
    
    print(f"\n{'='*100}")
    print(f"SUMMARY:")
    print(f"  Improvements: {improvements}")
    print(f"  Regressions: {regressions}")
    print(f"  Unchanged: {len(all_urls) - improvements - regressions}")
    print(f"{'='*100}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_extractors.py <results1.json> <results2.json>")
        print("Example: python compare_extractors.py old_results.json v3_results.json")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    print(f"Loading {file1}...")
    results1 = load_results(file1)
    
    print(f"Loading {file2}...")
    results2 = load_results(file2)
    
    compare_by_url(results1, results2)

if __name__ == "__main__":
    main()
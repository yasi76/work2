#!/usr/bin/env python3
"""
Test script for the extraction pipeline
Tests both company name and product extraction
"""

import json
import os
import sys

def create_test_data():
    """Create a small test dataset"""
    test_data = [
        {
            "url": "https://fyzo.de",
            "is_live": True,
            "is_health_related": True,
            "page_title": "fyzo - Digital Health Solutions"
        },
        {
            "url": "https://www.gesund.de",
            "is_live": True,
            "is_health_related": True,
            "page_title": "gesund.de - Your Health Platform"
        },
        {
            "url": "https://www.actimi.com",
            "is_live": True,
            "is_health_related": True,
            "page_title": "Actimi - Remote Patient Monitoring"
        }
    ]
    
    with open('test_startups.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("✅ Created test_startups.json")
    return 'test_startups.json'

def test_company_extraction(input_file):
    """Test company name extraction"""
    print("\n🔍 Testing Company Name Extraction...")
    
    # Run company extraction
    cmd = f"python extract_company_names.py {input_file} --output-prefix test"
    print(f"Running: {cmd}")
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Company extraction completed successfully")
        
        # Check output files
        if os.path.exists('test_with_names.json'):
            with open('test_with_names.json', 'r') as f:
                data = json.load(f)
            print(f"✅ Found {len(data)} companies with names")
            
            # Show sample results
            print("\nSample results:")
            for item in data[:3]:
                print(f"  - {item.get('company_name', 'Unknown')} ({item.get('url')})")
            
            return 'test_with_names.json'
    else:
        print("❌ Company extraction failed")
        return None

def test_product_extraction(input_file):
    """Test product extraction"""
    print("\n🔍 Testing Product Extraction...")
    
    # Run product extraction with limit
    cmd = f"python extract_products.py {input_file} --output-prefix test --limit 3"
    print(f"Running: {cmd}")
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Product extraction completed successfully")
        
        # Check output files
        if os.path.exists('test_products.json'):
            with open('test_products.json', 'r') as f:
                data = json.load(f)
            
            print(f"✅ Processed {len(data)} companies")
            
            # Show sample results
            print("\nSample results:")
            for company in data:
                products = company.get('product_names', [])
                print(f"  - {company.get('company_name')}: {len(products)} products")
                for product in products[:3]:
                    product_type = company.get('product_types', {}).get(product, 'unknown')
                    print(f"    • {product} ({product_type})")
        
        # Check statistics
        if os.path.exists('test_product_stats.json'):
            with open('test_product_stats.json', 'r') as f:
                stats = json.load(f)
            print("\n📊 Extraction Statistics:")
            print(f"  - Total products: {stats.get('total_products', 0)}")
            print(f"  - Companies with products: {stats.get('companies_with_products', 0)}")
            if 'ground_truth_validation' in stats:
                gt = stats['ground_truth_validation']
                print(f"  - Ground truth accuracy: {gt.get('accuracy', 'N/A')}")
    else:
        print("❌ Product extraction failed")

def cleanup_test_files():
    """Remove test files"""
    print("\n🧹 Cleaning up test files...")
    test_files = [
        'test_startups.json',
        'test_with_names.json',
        'test_with_names.csv',
        'test_company_names.txt',
        'test_extraction_stats.json',
        'test_products.json',
        'test_products.csv',
        'test_product_stats.json'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removed {file}")

def main():
    print("🚀 Digital Health Extraction Pipeline Test")
    print("="*50)
    
    try:
        # Create test data
        test_file = create_test_data()
        
        # Test company extraction
        companies_file = test_company_extraction(test_file)
        
        if companies_file:
            # Test product extraction
            test_product_extraction(companies_file)
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        sys.exit(1)
    
    finally:
        # Ask user if they want to keep test files
        response = input("\nKeep test files for inspection? (y/n): ").lower()
        if response != 'y':
            cleanup_test_files()

if __name__ == "__main__":
    main()
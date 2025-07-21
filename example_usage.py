#!/usr/bin/env python3
"""
Example usage of the Company Name Extractor
"""

from extract_company_name import CompanyNameExtractor
from extract_company_name_advanced import AdvancedCompanyNameExtractor
import json


def basic_example():
    """Basic extraction example"""
    print("="*60)
    print("BASIC COMPANY NAME EXTRACTION")
    print("="*60)
    
    # Your URLs
    urls = [
        "https://floy.health",
        "https://www.actimi.com",
        "https://getnutrio.shop",
        # Add your URLs here
    ]
    
    # Create extractor
    extractor = CompanyNameExtractor()
    
    # Extract company names
    for url in urls:
        result = extractor.extract_company_name(url)
        print(f"\n{url}")
        print(f"  Company Name: {result['final_result'] or 'Not found'}")
        
        # Show which method was used
        for method in ['og_site_name', 'application_name', 'cleaned_title', 'h1', 'logo_alt', 'domain_based']:
            if result[method]:
                print(f"  Extracted via: {method}")
                break


def advanced_example():
    """Advanced extraction with confidence scores"""
    print("\n\n" + "="*60)
    print("ADVANCED EXTRACTION WITH CONFIDENCE SCORES")
    print("="*60)
    
    urls = [
        "https://stripe.com",
        "https://github.com",
        "https://www.shopify.com",
        # Add more URLs
    ]
    
    # Create advanced extractor
    extractor = AdvancedCompanyNameExtractor()
    
    # Process all URLs in parallel
    results = extractor.process_urls_parallel(urls, max_workers=3)
    
    # Display results
    for url, data in results.items():
        if 'error' not in data:
            print(f"\n{url}")
            print(f"  Company: {data['final_result']}")
            print(f"  Confidence: {data['confidence_score']:.0%}")
            print(f"  Method: {data['extraction_method']}")
    
    # Export to CSV
    extractor.export_results(results, 'my_company_names.csv')
    print("\n✓ Results saved to my_company_names.csv")


def batch_processing_example():
    """Process URLs from a file"""
    print("\n\n" + "="*60)
    print("BATCH PROCESSING FROM FILE")
    print("="*60)
    
    # Example: Read URLs from a file
    urls_file = "urls.txt"
    
    # Create the file with some example URLs
    with open(urls_file, 'w') as f:
        f.write("https://www.tesla.com\n")
        f.write("https://openai.com\n")
        f.write("https://www.microsoft.com\n")
        f.write("getnutrio.shop\n")  # Works without https://
    
    # Read URLs
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Processing {len(urls)} URLs from {urls_file}...")
    
    # Process
    extractor = AdvancedCompanyNameExtractor()
    results = extractor.process_urls_parallel(urls)
    
    # Save results as JSON
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✓ Results saved to results.json")
    
    # Quick summary
    print("\nSummary:")
    for url, data in results.items():
        if data.get('final_result'):
            print(f"  {data['final_result']} ({url})")


def custom_processing_example():
    """Example with custom processing"""
    print("\n\n" + "="*60)
    print("CUSTOM PROCESSING EXAMPLE")
    print("="*60)
    
    extractor = CompanyNameExtractor()
    
    # Process a single URL with detailed output
    url = "https://www.apple.com"
    result = extractor.extract_company_name(url)
    
    print(f"Analyzing: {url}")
    print("-" * 40)
    
    # Show all extraction attempts
    extraction_methods = [
        ('Open Graph', result['og_site_name']),
        ('Application Name', result['application_name']),
        ('Page Title', result['title']),
        ('Cleaned Title', result['cleaned_title']),
        ('H1 Tag', result['h1']),
        ('Logo Alt Text', result['logo_alt']),
        ('Domain Based', result['domain_based']),
    ]
    
    for method, value in extraction_methods:
        if value:
            print(f"✓ {method}: {value}")
        else:
            print(f"✗ {method}: Not found")
    
    print("-" * 40)
    print(f"Final Result: {result['final_result']}")


def filtering_example():
    """Example showing how to filter results by confidence"""
    print("\n\n" + "="*60)
    print("FILTERING BY CONFIDENCE SCORE")
    print("="*60)
    
    urls = [
        "https://www.amazon.com",
        "https://www.netflix.com",
        "https://random-startup-12345.com",  # May fail
        "https://example.com",
    ]
    
    extractor = AdvancedCompanyNameExtractor()
    results = extractor.process_urls_parallel(urls)
    
    # Filter high confidence results (>70%)
    high_confidence = {
        url: data for url, data in results.items()
        if data.get('confidence_score', 0) > 0.7
    }
    
    print("High Confidence Results (>70%):")
    for url, data in high_confidence.items():
        print(f"  {data['final_result']} - {url} ({data['confidence_score']:.0%})")
    
    # Filter low confidence results
    low_confidence = {
        url: data for url, data in results.items()
        if 0 < data.get('confidence_score', 0) <= 0.5
    }
    
    if low_confidence:
        print("\nLow Confidence Results (≤50%) - May need manual review:")
        for url, data in low_confidence.items():
            print(f"  {data['final_result']} - {url} ({data['confidence_score']:.0%})")


if __name__ == "__main__":
    # Run all examples
    basic_example()
    advanced_example()
    batch_processing_example()
    custom_processing_example()
    filtering_example()
    
    print("\n\n✨ All examples completed!")
    print("Check the generated files:")
    print("  - my_company_names.csv")
    print("  - results.json")
    print("  - urls.txt")
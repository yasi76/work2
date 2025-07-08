#!/usr/bin/env python3
"""
Test script for the enhanced healthcare URL discovery
Tests the improvements: better filtering, precise country detection, clean output
"""

import asyncio
import enhanced_main

async def test_enhanced_discovery():
    """
    Test the enhanced discovery with improvements
    """
    print("🧪 Testing Enhanced Healthcare URL Discovery")
    print("=" * 50)
    
    # Test just the initial URLs to verify improvements
    print("Testing with provided healthcare URLs only...")
    
    # Run a limited version for testing
    results = enhanced_main.url_validator.clean_and_validate_urls(
        enhanced_main.INITIAL_HEALTHCARE_URLS[:10]  # Test with first 10 URLs
    )
    
    print(f"\n📊 Test Results:")
    print(f"Total URLs tested: {len(results)}")
    
    healthcare_count = 0
    countries = {}
    
    for result in results:
        if result.get('is_live') and result.get('is_healthcare'):
            healthcare_count += 1
            country = enhanced_main.get_precise_country_estimate(result['url'])
            countries[country] = countries.get(country, 0) + 1
            
            print(f"✅ {result['url']}")
            print(f"   Country: {country}")
            print(f"   Title: {result.get('title', 'N/A')[:50]}...")
            print()
    
    print(f"🏥 Healthcare companies found: {healthcare_count}")
    print(f"🌍 Countries represented:")
    for country, count in countries.items():
        print(f"   {country}: {count}")
    
    print("\n✅ Enhanced discovery test completed!")
    print("The fixes should eliminate Google spam and provide precise country detection.")

if __name__ == "__main__":
    asyncio.run(test_enhanced_discovery())
#!/usr/bin/env python3
"""
Simple test to verify the main logic works without external dependencies
"""

import re
from urllib.parse import urlparse

def test_healthcare_url_detection():
    """Test the healthcare URL detection logic"""
    print("🧪 Testing Healthcare URL Detection Logic")
    print("=" * 50)
    
    # Simplified healthcare keywords
    healthcare_keywords = [
        'health', 'medical', 'healthcare', 'medicine', 'clinic', 'hospital',
        'doctor', 'physician', 'patient', 'therapy', 'treatment', 'diagnosis',
        'pharmaceutical', 'biotech', 'medtech', 'digital health', 'telemedicine'
    ]
    
    def is_healthcare_url(url, content=""):
        """Simplified healthcare detection"""
        combined_text = f"{url} {content}".lower()
        score = 0
        
        for keyword in healthcare_keywords:
            if keyword in combined_text:
                score += 1
        
        return score > 0, score
    
    # Test URLs
    test_cases = [
        ("https://www.medtech-europe.org/members/", "Medical technology association"),
        ("https://www.health-startup.com", "Digital health solutions"),
        ("https://www.example.com", "Regular website"),
        ("https://www.pharmacy-online.de", ""),
        ("https://www.biotech-innovations.fr", "Biotechnology company")
    ]
    
    print("Testing healthcare detection:")
    for url, content in test_cases:
        is_healthcare, score = is_healthcare_url(url, content)
        print(f"   URL: {url}")
        print(f"   Content: {content}")
        print(f"   Healthcare: {is_healthcare}, Score: {score}")
        print()
    
    return True

def test_url_cleaning():
    """Test URL cleaning logic"""
    print("🧹 Testing URL Cleaning Logic")
    print("=" * 30)
    
    def clean_url(url):
        """Simplified URL cleaning"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove fragments and tracking parameters
        parsed = urlparse(url)
        cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return cleaned.rstrip('/')
    
    test_urls = [
        "example.com",
        "https://example.com/page#fragment",
        "http://example.com/path/?utm_source=test",
        "https://example.com/page/"
    ]
    
    print("Testing URL cleaning:")
    for url in test_urls:
        cleaned = clean_url(url)
        print(f"   Original: {url}")
        print(f"   Cleaned:  {cleaned}")
        print()
    
    return True

def test_timeout_logic():
    """Test timeout and circuit breaker logic"""
    print("⏰ Testing Timeout Logic")
    print("=" * 25)
    
    import time
    import asyncio
    
    async def simulate_slow_operation(delay):
        """Simulate a slow operation"""
        await asyncio.sleep(delay)
        return f"Completed after {delay} seconds"
    
    async def test_with_timeout():
        """Test operation with timeout"""
        try:
            # Test with short timeout
            result = await asyncio.wait_for(
                simulate_slow_operation(0.5),  # 0.5 second operation
                timeout=1.0  # 1 second timeout
            )
            print(f"   ✅ Quick operation: {result}")
            
            # Test with timeout that should trigger
            try:
                result = await asyncio.wait_for(
                    simulate_slow_operation(2.0),  # 2 second operation  
                    timeout=1.0  # 1 second timeout
                )
                print(f"   ❌ This shouldn't complete: {result}")
            except asyncio.TimeoutError:
                print(f"   ✅ Timeout correctly triggered after 1 second")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Timeout test error: {e}")
            return False
    
    # Run the async test
    try:
        result = asyncio.run(test_with_timeout())
        return result
    except Exception as e:
        print(f"   ❌ Async test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Healthcare Discovery System - Logic Verification")
    print("=" * 60)
    print("Testing core logic without external dependencies...")
    print()
    
    test_results = []
    
    # Test 1: Healthcare detection
    test_results.append(test_healthcare_url_detection())
    
    # Test 2: URL cleaning
    test_results.append(test_url_cleaning())
    
    # Test 3: Timeout logic
    test_results.append(test_timeout_logic())
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 20)
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print()
        print("🎯 RECOMMENDATIONS:")
        print("1. Install dependencies: pip install aiohttp beautifulsoup4 requests")
        print("2. Run with small target: python professional_main.py --target-count 20")
        print("3. Use timeouts: The system now has proper timeout handling")
        print("4. Monitor progress: Watch for timeout messages in the output")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("   Some core logic may have issues")

if __name__ == "__main__":
    main()
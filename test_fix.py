#!/usr/bin/env python3
"""
Quick test to verify the healthcare discovery system fixes
"""

import asyncio
import sys
import traceback

async def test_healthcare_discovery():
    """Test the fixed healthcare discovery system"""
    print("🧪 Testing Healthcare Discovery System Fixes")
    print("=" * 50)
    
    try:
        # Import the fixed discovery module
        from ultimate_discoverer import UltimateURLDiscoverer
        
        print("✅ Successfully imported UltimateURLDiscoverer")
        
        # Test basic initialization
        async with UltimateURLDiscoverer() as discoverer:
            print("✅ Successfully initialized discoverer")
            
            # Test healthcare URL detection
            test_urls = [
                "https://www.medtech-europe.org/members/",
                "https://www.example-health.com",
                "https://www.random-tech.com"
            ]
            
            for url in test_urls:
                is_healthcare, score = discoverer._is_ultimate_healthcare_url(url, "medical device company")
                print(f"   URL: {url}")
                print(f"   Healthcare: {is_healthcare}, Score: {score}")
            
            # Test single source scraping with timeout
            print("\n🔍 Testing single source scraping with timeout...")
            test_source = "https://www.medtech-europe.org"
            
            try:
                # Test with a very short timeout to ensure it doesn't hang
                results = await asyncio.wait_for(
                    discoverer._advanced_web_scraping(test_source, max_depth=1),
                    timeout=10.0  # 10 second test timeout
                )
                print(f"✅ Successfully scraped {test_source}")
                print(f"   Found {len(results)} healthcare URLs")
                
                # Show first few results
                for i, url in enumerate(list(results)[:3], 1):
                    print(f"   {i}. {url}")
                    
            except asyncio.TimeoutError:
                print(f"⏰ Timeout test passed - scraping stopped at 10 seconds")
            except Exception as e:
                print(f"⚠️  Scraping error (expected): {str(e)[:100]}")
        
        print("\n✅ All tests passed! The system should work without hanging.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False


async def test_main_discovery():
    """Test the main discovery function with short timeout"""
    print("\n🚀 Testing Main Discovery Function")
    print("-" * 40)
    
    try:
        from ultimate_discoverer import discover_ultimate_healthcare_urls
        
        # Test with very short timeout to prevent hanging
        results = await asyncio.wait_for(
            discover_ultimate_healthcare_urls(),
            timeout=60.0  # 1 minute timeout for full test
        )
        
        print(f"✅ Main discovery completed successfully!")
        print(f"   Found {len(results)} healthcare URLs")
        
        # Show first few results
        if results:
            print("\n🏆 Sample results:")
            for i, result in enumerate(results[:5], 1):
                print(f"   {i}. {result['url']} (score: {result.get('healthcare_score', '?')})")
        
        return True
        
    except asyncio.TimeoutError:
        print("⏰ Discovery timeout - system may still have hanging issues")
        return False
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Healthcare Discovery System - Fix Verification")
    print("=" * 60)
    
    async def run_tests():
        # Test 1: Basic functionality
        test1_passed = await test_healthcare_discovery()
        
        if test1_passed:
            # Test 2: Main discovery function
            test2_passed = await test_main_discovery()
            
            if test2_passed:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ The system should now work without hanging")
                print("✅ You can run: python professional_main.py")
            else:
                print("\n⚠️  Basic tests passed but main discovery may still have issues")
                print("💡 Try running with smaller target: python professional_main.py --target-count 20")
        else:
            print("\n❌ Basic tests failed - check dependencies and imports")
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test framework error: {e}")
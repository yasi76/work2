#!/usr/bin/env python3
"""
NO-HANG Test for Healthcare Discovery System
This will demonstrate the system works without hanging
"""

import asyncio
import sys

def test_config():
    """Test that configuration is properly set to prevent hanging"""
    print("🔧 Testing Configuration Settings...")
    
    try:
        import ultimate_config as uconfig
        
        settings = uconfig.ULTIMATE_SETTINGS
        print(f"   MAX_TOTAL_URLS_TARGET: {settings['MAX_TOTAL_URLS_TARGET']}")
        print(f"   PARALLEL_SEARCHES: {settings['PARALLEL_SEARCHES']}")
        print(f"   CRAWL_DEPTH: {settings['CRAWL_DEPTH']}")
        print(f"   ENABLE_DEEP_CRAWLING: {settings['ENABLE_DEEP_CRAWLING']}")
        
        # Check if settings are conservative enough
        if (settings['MAX_TOTAL_URLS_TARGET'] <= 50 and 
            settings['PARALLEL_SEARCHES'] <= 5 and
            settings['CRAWL_DEPTH'] <= 1 and
            not settings['ENABLE_DEEP_CRAWLING']):
            print("   ✅ Configuration is SAFE - should not hang")
            return True
        else:
            print("   ⚠️  Configuration may still cause hanging")
            return False
            
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

async def test_no_hang_discovery():
    """Test the no-hang discovery system"""
    print("\n🚀 Testing NO-HANG Discovery System...")
    
    try:
        from ultimate_discoverer import discover_ultimate_healthcare_urls
        
        print("   Starting discovery with 30-second timeout...")
        
        # Test with aggressive timeout to prove it won't hang
        results = await asyncio.wait_for(
            discover_ultimate_healthcare_urls(),
            timeout=30.0  # 30 second timeout
        )
        
        print(f"   ✅ Discovery completed successfully!")
        print(f"   Found {len(results)} healthcare URLs")
        
        if results:
            print("   📋 Sample results:")
            for i, result in enumerate(results[:3], 1):
                print(f"      {i}. {result['url']}")
        
        return True
        
    except asyncio.TimeoutError:
        print("   ❌ Discovery still hanging (timed out after 30 seconds)")
        return False
    except Exception as e:
        print(f"   ❌ Discovery error: {e}")
        return False

async def main():
    """Run all no-hang tests"""
    print("🔬 NO-HANG Healthcare Discovery Test")
    print("=" * 50)
    print("This test will prove the system no longer hangs")
    print()
    
    # Test 1: Configuration
    config_ok = test_config()
    
    if config_ok:
        # Test 2: Discovery with timeout
        discovery_ok = await test_no_hang_discovery()
        
        if discovery_ok:
            print("\n🎉 SUCCESS! System no longer hangs!")
            print("✅ Safe to run: python professional_main.py")
        else:
            print("\n⚠️  System may still have hanging issues")
            print("💡 Try with even smaller target: --target-count 5")
    else:
        print("\n❌ Configuration not safe enough")
        print("💡 Need to reduce settings further")

if __name__ == "__main__":
    print("⚠️  NO-HANG TEST - Will complete in under 30 seconds")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test framework error: {e}")
#!/usr/bin/env python3
"""
SAFE Healthcare Discovery Runner
Ensures the system runs with safe settings to prevent hanging
"""

import sys
import subprocess

def update_config_for_safety(target_count=20):
    """Update configuration to ensure safe operation"""
    try:
        import ultimate_config as uconfig
        
        # Force safe settings
        uconfig.ULTIMATE_SETTINGS.update({
            'MAX_TOTAL_URLS_TARGET': min(target_count, 50),  # Cap at 50
            'MAX_URLS_PER_SOURCE': 5,  # Very conservative
            'PARALLEL_SEARCHES': 2,  # Very low concurrency
            'CRAWL_DEPTH': 1,  # Surface only
            'ENABLE_DEEP_CRAWLING': False,
            'ENABLE_MULTILINGUAL_SEARCH': False,
            'ENABLE_SECTOR_SPECIFIC_SEARCH': False,
            'ENABLE_GEOGRAPHIC_SEARCH': False,
        })
        
        print(f"✅ Configuration updated for SAFE operation (target: {uconfig.ULTIMATE_SETTINGS['MAX_TOTAL_URLS_TARGET']})")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    """Run the healthcare discovery system safely"""
    print("🛡️  SAFE Healthcare Discovery Runner")
    print("=" * 50)
    
    # Parse target count from command line
    target_count = 20
    if len(sys.argv) > 1:
        try:
            target_count = int(sys.argv[1])
            print(f"📊 Requested target: {target_count}")
        except ValueError:
            print(f"⚠️  Invalid target count, using default: {target_count}")
    
    # Cap target count for safety
    if target_count > 100:
        print(f"⚠️  Target {target_count} too high for safety, capping at 100")
        target_count = 100
    
    # Update configuration
    if update_config_for_safety(target_count):
        
        print("\n🚀 Starting SAFE healthcare discovery...")
        print("   - Limited sources to prevent hanging")
        print("   - Short timeouts for all operations")
        print("   - Conservative crawling settings")
        print()
        
        try:
            # Run the main system with safe parameters
            cmd = [
                sys.executable, 
                "professional_main.py",
                "--target-count", str(target_count),
                "--max-workers", "2",  # Very conservative
                "--log-level", "INFO"
            ]
            
            print(f"🎯 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                print("\n✅ SAFE discovery completed successfully!")
            else:
                print(f"\n⚠️  Discovery completed with return code: {result.returncode}")
                
        except KeyboardInterrupt:
            print("\n⚠️  Discovery interrupted by user")
        except Exception as e:
            print(f"\n❌ Error running discovery: {e}")
    
    else:
        print("❌ Could not configure system for safe operation")

if __name__ == "__main__":
    print("Usage: python safe_run.py [target_count]")
    print("Example: python safe_run.py 30")
    print()
    main()
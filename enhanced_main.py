"""
ENHANCED Healthcare URL Validator and Discoverer
Designed to find 500-2000+ healthcare companies across Europe instead of just 57

This enhanced version uses:
- 50+ comprehensive search queries (multi-language)
- Geographic searches across 50+ European cities
- Sector-specific searches (13 healthcare sectors)
- Multiple startup databases and industry sources
- Deep crawling and better extraction methods

Usage:
    python enhanced_main.py
"""

import asyncio
import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict
import url_validator
import enhanced_discoverer
import enhanced_config as econfig
import utils


# The provided list of healthcare URLs to validate and clean
INITIAL_HEALTHCARE_URLS = [
    "https://www.acalta.de",
    "https://www.actimi.com",
    "https://www.emmora.de", 
    "https://www.alfa-ai.com",
    "https://www.apheris.com",
    "https://www.aporize.com/",
    "https://www.arztlena.com/",
    "https://shop.getnutrio.com/",
    "https://www.auta.health/",
    "https://visioncheckout.com/",
    "https://www.avayl.tech/",
    "https://www.avimedical.com/avi-impact",
    "https://de.becureglobal.com/",
    "https://bellehealth.co/de/",
    "https://www.biotx.ai/",
    "https://www.brainjo.de/",
    "https://brea.app/",
    "https://breathment.com/",
    "https://de.caona.eu/",
    "https://www.careanimations.de/",
    "https://sfs-healthcare.com",
    "https://www.climedo.de/",
    "https://www.cliniserve.de/",
    "https://cogthera.de/#erfahren",
    "https://www.comuny.de/",
    "https://curecurve.de/elina-app/",
    "https://www.cynteract.com/de/rehabilitation",
    "https://www.healthmeapp.de/de/",
    "https://deepeye.ai/",
    "https://www.deepmentation.ai/",
    "https://denton-systems.de/",
    "https://www.derma2go.com/",
    "https://www.dianovi.com/",
    "http://dopavision.com/",
    "https://www.dpv-analytics.com/",
    "http://www.ecovery.de/",
    "https://elixionmedical.com/",
    "https://www.empident.de/",
    "https://eye2you.ai/",
    "https://www.fitwhit.de",
    "https://www.floy.com/",
    "https://fyzo.de/assistant/",
    "https://www.gesund.de/app",
    "https://www.glaice.de/",
    "https://gleea.de/",
    "https://www.guidecare.de/",
    "https://www.apodienste.com/",
    "https://www.help-app.de/",
    "https://www.heynanny.com/",
    "https://incontalert.de/",
    "https://home.informme.info/",
    "https://www.kranushealth.com/de/therapien/haeufiger-harndrang",
    "https://www.kranushealth.com/de/therapien/inkontinenz"
]


def print_enhanced_statistics(all_results: List[Dict]):
    """
    Print comprehensive statistics about the enhanced URL processing results.
    """
    print("\n" + "="*80)
    print("ENHANCED DISCOVERY FINAL STATISTICS")
    print("="*80)
    
    # Overall statistics
    total_urls = len(all_results)
    live_urls = [r for r in all_results if r['is_live']]
    healthcare_urls = [r for r in live_urls if r['is_healthcare']]
    
    print(f"🎯 TARGET: 500-2000+ healthcare companies across Europe")
    print(f"📊 RESULTS:")
    print(f"   Total URLs discovered & validated: {total_urls}")
    print(f"   Live URLs: {len(live_urls)} ({len(live_urls)/total_urls*100:.1f}%)")
    print(f"   Healthcare-related URLs: {len(healthcare_urls)} ({len(healthcare_urls)/total_urls*100:.1f}%)")
    
    # Success metrics
    if len(healthcare_urls) >= 200:
        print(f"✅ SUCCESS: Found {len(healthcare_urls)} healthcare companies!")
    elif len(healthcare_urls) >= 100:
        print(f"🟡 GOOD: Found {len(healthcare_urls)} healthcare companies (target: 200+)")
    else:
        print(f"🔴 NEEDS IMPROVEMENT: Only found {len(healthcare_urls)} healthcare companies")
    
    # Geographic distribution
    print(f"\n🌍 GEOGRAPHIC DISTRIBUTION:")
    countries = {}
    for result in healthcare_urls:
        url = result['url']
        if '.de' in url or 'german' in url.lower() or 'deutschland' in url.lower():
            countries['Germany'] = countries.get('Germany', 0) + 1
        elif '.fr' in url or 'france' in url.lower():
            countries['France'] = countries.get('France', 0) + 1
        elif '.nl' in url or 'netherlands' in url.lower():
            countries['Netherlands'] = countries.get('Netherlands', 0) + 1
        elif '.uk' in url or '.co.uk' in url:
            countries['UK'] = countries.get('UK', 0) + 1
        elif '.ch' in url or 'switzerland' in url.lower():
            countries['Switzerland'] = countries.get('Switzerland', 0) + 1
        else:
            countries['Other EU'] = countries.get('Other EU', 0) + 1
    
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"   {country}: {count} companies")
    
    # Source breakdown
    print(f"\n📈 DISCOVERY SOURCES:")
    sources = {}
    for result in all_results:
        source = result['source']
        if source not in sources:
            sources[source] = {'total': 0, 'live': 0, 'healthcare': 0}
        sources[source]['total'] += 1
        if result['is_live']:
            sources[source]['live'] += 1
            if result['is_healthcare']:
                sources[source]['healthcare'] += 1
    
    for source, stats in sources.items():
        print(f"   {source}:")
        print(f"     Total: {stats['total']}, Live: {stats['live']}, Healthcare: {stats['healthcare']}")
    
    # Quality metrics
    if live_urls:
        response_times = [r['response_time'] for r in live_urls if r['response_time']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Average response time: {avg_response_time:.2f} seconds")
    
    # Sector distribution (estimated)
    print(f"\n🏥 ESTIMATED SECTOR DISTRIBUTION:")
    sector_keywords = {
        'Digital Therapeutics': ['therapeut', 'dtx', 'prescription'],
        'Telemedicine': ['tele', 'remote', 'virtual'],
        'Medical Devices': ['device', 'equipment', 'diagnostic'],
        'Health Analytics': ['analytic', 'data', 'insight'],
        'Mental Health': ['mental', 'psychology', 'behavior'],
        'AI/ML Health': ['ai', 'artificial', 'machine learning'],
    }
    
    for sector, keywords in sector_keywords.items():
        count = 0
        for result in healthcare_urls:
            text = f"{result.get('title', '')} {result.get('description', '')} {result['url']}".lower()
            if any(keyword in text for keyword in keywords):
                count += 1
        if count > 0:
            print(f"   {sector}: ~{count} companies")


def save_enhanced_results(results: List[Dict], timestamp: str):
    """
    Save enhanced results with better organization
    """
    # Save all results
    all_csv = f"enhanced_healthcare_urls_all_{timestamp}.csv"
    all_json = f"enhanced_healthcare_urls_all_{timestamp}.json"
    
    # Create DataFrame with enhanced columns
    df = pd.DataFrame(results)
    
    # Add analysis columns
    df['domain'] = df['url'].apply(utils.extract_domain)
    df['country_estimate'] = df['url'].apply(lambda x: 
        'Germany' if '.de' in x else
        'France' if '.fr' in x else
        'Netherlands' if '.nl' in x else
        'UK' if '.uk' in x or '.co.uk' in x else
        'Switzerland' if '.ch' in x else
        'Other EU'
    )
    
    # Reorder columns
    column_order = ['url', 'domain', 'country_estimate', 'source', 'is_live', 'is_healthcare', 
                   'status_code', 'title', 'description', 'response_time', 'error']
    df = df[column_order]
    
    # Save all results
    df.to_csv(all_csv, index=False, encoding='utf-8')
    
    # Save JSON with metadata
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'discovery_method': 'Enhanced Multi-source Discovery',
            'target_regions': 'Europe (all countries)',
            'search_queries': len(econfig.ENHANCED_SEARCH_QUERIES),
            'discovery_sources': sum(len(sources) for sources in econfig.ENHANCED_DISCOVERY_SOURCES.values()),
            'total_urls': len(results),
            'live_urls': len([r for r in results if r['is_live']]),
            'healthcare_urls': len([r for r in results if r.get('is_live') and r.get('is_healthcare')])
        },
        'urls': results
    }
    
    with open(all_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 All results saved to: {all_csv} and {all_json}")
    
    # Save healthcare-only results
    healthcare_only = df[(df['is_live'] == True) & (df['is_healthcare'] == True)]
    
    if len(healthcare_only) > 0:
        healthcare_csv = f"enhanced_healthcare_urls_live_{timestamp}.csv"
        healthcare_json = f"enhanced_healthcare_urls_live_{timestamp}.json"
        
        healthcare_only.to_csv(healthcare_csv, index=False, encoding='utf-8')
        
        # Healthcare-only JSON
        healthcare_data = {
            'metadata': output_data['metadata'].copy(),
            'urls': healthcare_only.to_dict('records')
        }
        healthcare_data['metadata']['description'] = 'Live healthcare companies only'
        
        with open(healthcare_json, 'w', encoding='utf-8') as f:
            json.dump(healthcare_data, f, indent=2, ensure_ascii=False)
        
        print(f"🏥 Healthcare-only results saved to: {healthcare_csv} and {healthcare_json}")
        print(f"   ({len(healthcare_only)} verified healthcare companies)")


async def enhanced_main():
    """
    Enhanced main function targeting 500-2000+ healthcare companies
    """
    print("🚀 ENHANCED Healthcare URL Validator and Discoverer")
    print("=" * 70)
    print("🎯 TARGET: Find 500-2000+ healthcare companies across Europe")
    print("🔍 METHOD: Comprehensive multi-source discovery")
    print(f"⏰ Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    all_results = []
    
    # Step 1: Validate the provided URLs (quick start)
    print(f"📋 Step 1: Validating {len(INITIAL_HEALTHCARE_URLS)} provided URLs...")
    validated_results = url_validator.clean_and_validate_urls(INITIAL_HEALTHCARE_URLS)
    all_results.extend(validated_results)
    
    initial_healthcare = len([r for r in validated_results if r.get('is_live') and r.get('is_healthcare')])
    print(f"   ✅ Initial validation complete: {initial_healthcare} healthcare companies confirmed")
    
    # Step 2: Enhanced discovery (the main improvement)
    print(f"\n🔍 Step 2: ENHANCED discovery from comprehensive sources...")
    print(f"   - {len(econfig.ENHANCED_SEARCH_QUERIES)} search queries")
    print(f"   - {len(econfig.EUROPEAN_HEALTHCARE_HUBS)} European cities")
    print(f"   - {len(econfig.HEALTHCARE_SECTORS)} healthcare sectors")
    print(f"   - Multi-language searches (English, German, French, Dutch)")
    print(f"   - {sum(len(sources) for sources in econfig.ENHANCED_DISCOVERY_SOURCES.values())} specialized sources")
    print("")
    
    try:
        discovered_results = await enhanced_discoverer.discover_enhanced_urls()
        
        if discovered_results:
            print(f"\n🎉 Discovery phase complete! Found {len(discovered_results)} new URLs")
            print(f"🔬 Now validating all discovered URLs...")
            
            urls_to_validate = [r['url'] for r in discovered_results]
            url_source_map = {r['url']: r['source'] for r in discovered_results}
            
            # Validate in batches to show progress
            batch_size = 100
            validated_discovered = []
            
            for i in range(0, len(urls_to_validate), batch_size):
                batch = urls_to_validate[i:i+batch_size]
                print(f"   Validating batch {i//batch_size + 1}/{(len(urls_to_validate)-1)//batch_size + 1} ({len(batch)} URLs)...")
                
                batch_results = url_validator.clean_and_validate_urls(batch)
                
                # Update source information
                for result in batch_results:
                    if result['url'] in url_source_map:
                        result['source'] = url_source_map[result['url']]
                
                validated_discovered.extend(batch_results)
                
                # Progress update
                healthcare_so_far = len([r for r in validated_discovered if r.get('is_live') and r.get('is_healthcare')])
                print(f"     Healthcare companies found so far: {healthcare_so_far}")
            
            all_results.extend(validated_discovered)
        else:
            print("⚠️  No new URLs discovered (may be due to search limitations)")
            
    except Exception as e:
        print(f"❌ Error during enhanced discovery: {e}")
        print("Continuing with initial URLs only...")
    
    # Step 3: Deduplication
    print(f"\n🔄 Step 3: Removing duplicates across all sources...")
    unique_results = []
    seen_urls = set()
    
    for result in all_results:
        if result['url'] not in seen_urls:
            seen_urls.add(result['url'])
            unique_results.append(result)
    
    print(f"   Total unique URLs after deduplication: {len(unique_results)}")
    
    # Step 4: Enhanced statistics
    print_enhanced_statistics(unique_results)
    
    # Step 5: Save enhanced results
    print(f"\n💾 Step 5: Saving enhanced results...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_enhanced_results(unique_results, timestamp)
    
    # Final summary
    healthcare_final = len([r for r in unique_results if r.get('is_live') and r.get('is_healthcare')])
    
    print(f"\n🎉 ENHANCED DISCOVERY COMPLETE!")
    print(f"📊 FINAL RESULTS:")
    print(f"   • Total URLs processed: {len(unique_results)}")
    print(f"   • Verified healthcare companies: {healthcare_final}")
    print(f"   • Improvement over basic method: {healthcare_final - 57} additional companies")
    
    if healthcare_final >= 200:
        print(f"✅ SUCCESS! Found {healthcare_final} healthcare companies (target: 200+)")
    elif healthcare_final >= 100:
        print(f"🟡 GOOD PROGRESS! Found {healthcare_final} companies (keep expanding sources for more)")
    else:
        print(f"🔴 NEEDS MORE WORK: Only {healthcare_final} companies found")
        print("💡 SUGGESTIONS:")
        print("   - Add more specialized healthcare databases")
        print("   - Expand to more European countries")
        print("   - Use professional APIs (Crunchbase Pro, PitchBook)")
        print("   - Search university spin-off databases")
    
    return unique_results


def run_enhanced_main():
    """
    Entry point with enhanced error handling
    """
    print("🔧 Checking environment...")
    
    try:
        loop = asyncio.get_running_loop()
        print("⚠️  Existing event loop detected.")
        print("For best results, run from command line: python enhanced_main.py")
        print("Proceeding with compatibility mode...\n")
    except RuntimeError:
        print("✅ Clean environment detected. Full performance mode enabled.\n")
    
    try:
        results = asyncio.run(enhanced_main())
        
        healthcare_count = len([r for r in results if r.get('is_live') and r.get('is_healthcare')])
        
        if healthcare_count > 57:
            print(f"\n🎉 SUCCESS! Enhanced discovery found {healthcare_count} healthcare companies")
            print(f"📈 That's {healthcare_count - 57} more than the basic method!")
        else:
            print(f"\n📊 Found {healthcare_count} healthcare companies")
        
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("\n⚠️  Event loop conflict detected.")
            print("Please run from command line for full functionality:")
            print("  python enhanced_main.py")
        else:
            print(f"\n❌ Runtime error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your internet connection and try again.")
    
    print("\nThank you for using Enhanced Healthcare URL Discoverer! 🚀")


if __name__ == "__main__":
    run_enhanced_main()
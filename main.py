"""
Healthcare URL Validator and Discoverer
Main script to validate existing URLs and discover new healthcare-related URLs.

This script:
1. Validates and cleans a provided list of healthcare URLs
2. Discovers new healthcare URLs from various sources
3. Outputs results in CSV and JSON formats

Usage:
    python main.py
"""

import asyncio
import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict
import url_validator
import url_discoverer
import config
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


def print_statistics(all_results: List[Dict]):
    """
    Print comprehensive statistics about the URL processing results.
    
    Args:
        all_results (List[Dict]): All URL processing results
    """
    print("\n" + "="*60)
    print("FINAL STATISTICS")
    print("="*60)
    
    # Overall statistics
    total_urls = len(all_results)
    live_urls = [r for r in all_results if r['is_live']]
    healthcare_urls = [r for r in live_urls if r['is_healthcare']]
    
    print(f"Total URLs processed: {total_urls}")
    print(f"Live URLs: {len(live_urls)} ({len(live_urls)/total_urls*100:.1f}%)")
    print(f"Healthcare-related URLs: {len(healthcare_urls)} ({len(healthcare_urls)/total_urls*100:.1f}%)")
    
    # Statistics by source
    print(f"\nBreakdown by source:")
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
        print(f"  {source}:")
        print(f"    Total: {stats['total']}, Live: {stats['live']}, Healthcare: {stats['healthcare']}")
    
    # Response time statistics for live URLs
    if live_urls:
        response_times = [r['response_time'] for r in live_urls if r['response_time']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"\nAverage response time: {avg_response_time:.2f} seconds")
    
    # Common error types
    error_urls = [r for r in all_results if r['error']]
    if error_urls:
        errors = {}
        for result in error_urls:
            error = result['error']
            if error not in errors:
                errors[error] = 0
            errors[error] += 1
        
        print(f"\nCommon errors:")
        for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {error}: {count} times")


def save_results_csv(results: List[Dict], filename: str):
    """
    Save results to a CSV file.
    
    Args:
        results (List[Dict]): Results to save
        filename (str): Output filename
    """
    try:
        df = pd.DataFrame(results)
        
        # Reorder columns for better readability
        columns_order = ['url', 'source', 'is_live', 'is_healthcare', 'status_code', 
                        'title', 'description', 'response_time', 'error']
        
        # Only include columns that exist
        available_columns = [col for col in columns_order if col in df.columns]
        df = df[available_columns]
        
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")
        
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def save_results_json(results: List[Dict], filename: str):
    """
    Save results to a JSON file.
    
    Args:
        results (List[Dict]): Results to save
        filename (str): Output filename
    """
    try:
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_urls': len(results),
                'live_urls': len([r for r in results if r['is_live']]),
                'healthcare_urls': len([r for r in results if r.get('is_live') and r.get('is_healthcare')])
            },
            'urls': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")
        
    except Exception as e:
        print(f"Error saving JSON file: {e}")


async def main():
    """
    Main function that orchestrates the entire URL validation and discovery process.
    """
    print("Healthcare URL Validator and Discoverer")
    print("=" * 50)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Step 1: Validate and clean the provided URLs
    print(f"\nStep 1: Validating {len(INITIAL_HEALTHCARE_URLS)} provided URLs...")
    validated_results = url_validator.clean_and_validate_urls(INITIAL_HEALTHCARE_URLS)
    all_results.extend(validated_results)
    
    # Step 2: Discover new URLs from various sources
    print(f"\nStep 2: Discovering new URLs from various sources...")
    try:
        discovered_results = await url_discoverer.discover_new_urls()
        
        # Validate the discovered URLs
        if discovered_results:
            print(f"Found {len(discovered_results)} new URLs, validating them...")
            urls_to_validate = [r['url'] for r in discovered_results]
            
            # Create a mapping of URLs to their source information
            url_source_map = {r['url']: r['source'] for r in discovered_results}
            
            # Validate the discovered URLs
            validation_results = url_validator.clean_and_validate_urls(urls_to_validate)
            
            # Update source information
            for result in validation_results:
                if result['url'] in url_source_map:
                    result['source'] = url_source_map[result['url']]
            
            all_results.extend(validation_results)
        else:
            print("No new URLs discovered.")
            
    except Exception as e:
        print(f"Error during URL discovery: {e}")
    
    # Step 3: Remove duplicates across all results
    print(f"\nStep 3: Removing duplicates across all sources...")
    unique_results = []
    seen_urls = set()
    
    for result in all_results:
        if result['url'] not in seen_urls:
            seen_urls.add(result['url'])
            unique_results.append(result)
    
    print(f"Total unique URLs after deduplication: {len(unique_results)}")
    
    # Step 4: Print statistics
    print_statistics(unique_results)
    
    # Step 5: Save results
    print(f"\nStep 5: Saving results...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save all results
    csv_filename = f"healthcare_urls_all_{timestamp}.csv"
    json_filename = f"healthcare_urls_all_{timestamp}.json"
    save_results_csv(unique_results, csv_filename)
    save_results_json(unique_results, json_filename)
    
    # Save only live healthcare URLs
    healthcare_only = [r for r in unique_results if r.get('is_live') and r.get('is_healthcare')]
    if healthcare_only:
        csv_healthcare = f"healthcare_urls_live_{timestamp}.csv"
        json_healthcare = f"healthcare_urls_live_{timestamp}.json"
        save_results_csv(healthcare_only, csv_healthcare)
        save_results_json(healthcare_only, json_healthcare)
        print(f"Live healthcare URLs saved separately ({len(healthcare_only)} URLs)")
    
    print(f"\nProcess completed successfully!")
    print(f"Check the output files for detailed results.")
    
    return unique_results


def run_main():
    """
    Entry point that handles event loop issues.
    """
    def get_event_loop_policy():
        """Check if there's already a running event loop."""
        try:
            loop = asyncio.get_running_loop()
            return loop, True  # Loop is running
        except RuntimeError:
            return None, False  # No running loop
    
    loop, is_running = get_event_loop_policy()
    
    if is_running:
        print("⚠️  Detected existing event loop environment.")
        print("This commonly happens in Jupyter notebooks or some IDEs.")
        print("URL discovery will be limited to avoid conflicts.")
        print("For full functionality, run this script in a regular Python environment.\n")
    
    try:
        # Run the main async function
        if is_running:
            # Alternative approach for environments with existing event loops
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            # We'll let the validation handle this gracefully
        
        results = asyncio.run(main())
        
        print(f"\n🎉 Success! Processed {len(results)} URLs total.")
        
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("\n⚠️  Event loop conflict detected.")
            print("Please run this script in a regular Python environment:")
            print("  python main.py")
            print("Or run from command line instead of an interactive environment.")
        else:
            print(f"\n❌ An error occurred: {e}")
            print("Please check your internet connection and try again.")
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your internet connection and try again.")
    
    print("\nThank you for using Healthcare URL Validator and Discoverer!")


if __name__ == "__main__":
    run_main()
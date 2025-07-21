#!/usr/bin/env python3
"""
JSON to CSV Converter for Startup Discovery Results
Converts comprehensive_results_*.json files to CSV format
"""

import json
import csv
import sys
import os
from datetime import datetime

def convert_json_to_csv(json_file_path, output_csv_path=None):
    """Convert comprehensive JSON results to CSV format"""
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"❌ Error: File '{json_file_path}' not found")
        return False
    
    try:
        # Load JSON data
        print(f"📖 Loading JSON data from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract URLs array
        urls = data.get('urls', [])
        if not urls:
            print("❌ Error: No URLs found in JSON file")
            return False
        
        print(f"✅ Found {len(urls)} URLs in JSON file")
        
        # Determine output CSV path
        if output_csv_path is None:
            # Create output filename based on input filename
            base_name = os.path.splitext(os.path.basename(json_file_path))[0]
            output_csv_path = f"{base_name}_converted.csv"
        
        # Define CSV fieldnames (all possible fields from the comprehensive data)
        fieldnames = [
            'url', 'source', 'confidence', 'category', 'method',
            'is_alive', 'status_code', 'final_url', 'content_length',
            'health_score', 'is_health_related', 'industry_label', 'page_title', 'meta_description',
            'keyword_matches', 'languages_detected', 'country', 'discovered_at', 
            'github_stars', 'github_repo', 'error'
        ]
        
        # Write CSV file
        print(f"💾 Writing CSV data to: {output_csv_path}")
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for url_data in urls:
                # Ensure all fields have values (fill missing with empty string)
                row = {}
                for field in fieldnames:
                    value = url_data.get(field, '')
                    # Convert lists/dicts to strings for CSV compatibility
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[field] = value
                writer.writerow(row)
        
        print(f"✅ Successfully converted {len(urls)} URLs to CSV")
        
        # Print summary stats
        print(f"\n📊 Summary Statistics:")
        print(f"  • Total URLs: {len(urls)}")
        print(f"  • Alive URLs: {len([u for u in urls if u.get('is_alive', True)])}")
        print(f"  • Health-related: {len([u for u in urls if u.get('is_health_related', False)])}")
        print(f"  • High confidence (9-10): {len([u for u in urls if u.get('confidence', 0) >= 9])}")
        print(f"  • Medium confidence (5-8): {len([u for u in urls if 5 <= u.get('confidence', 0) < 9])}")
        print(f"  • Low confidence (1-4): {len([u for u in urls if u.get('confidence', 0) < 5])}")
        
        # Print discovery method breakdown
        methods = {}
        for url in urls:
            method = url.get('method', url.get('source', 'Unknown'))
            methods[method] = methods.get(method, 0) + 1
        
        if methods:
            print(f"\n🔍 Discovery Methods:")
            for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {method}: {count} URLs")
        
        # Print engine performance if available
        engine_perf = data.get('engine_performance', {})
        if engine_perf:
            print(f"\n⚡ Search Engine Performance:")
            for engine, stats in engine_perf.items():
                success_rate = stats.get('success_rate', 0)
                attempts = stats.get('attempts', 0)
                successes = stats.get('successes', 0)
                print(f"  • {engine.title()}: {success_rate} success rate ({successes}/{attempts})")
        
        print(f"\n🎉 Conversion complete! Output file: {output_csv_path}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔄 JSON to CSV Converter for Startup Discovery Results")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 json_to_csv_converter.py <json_file> [output_csv_file]")
        print("\nExample:")
        print("  python3 json_to_csv_converter.py comprehensive_results_20250721_223647.json")
        print("  python3 json_to_csv_converter.py comprehensive_results_20250721_223647.json output.csv")
        return
    
    json_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Convert JSON to CSV
    success = convert_json_to_csv(json_file, output_csv)
    
    if success:
        print("\n✅ Conversion completed successfully!")
    else:
        print("\n❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
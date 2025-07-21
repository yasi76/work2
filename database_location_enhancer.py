#!/usr/bin/env python3
"""
🌍 Database Location Enhancer
==============================
Enhance existing healthcare database with state and city information extracted from URLs.
"""

import csv
import json
import os
import glob
from datetime import datetime
from location_extractor import LocationExtractor


def find_latest_database_files():
    """Find the most recent database CSV and JSON files."""
    csv_files = glob.glob("DYNAMIC_MEGA_*_DATABASE_*.csv")
    json_files = glob.glob("DYNAMIC_MEGA_*_DATABASE_*.json")
    
    if not csv_files:
        return None, None
    
    # Sort by modification time and get the latest
    csv_files.sort(key=os.path.getmtime, reverse=True)
    json_files.sort(key=os.path.getmtime, reverse=True)
    
    latest_csv = csv_files[0] if csv_files else None
    latest_json = json_files[0] if json_files else None
    
    return latest_csv, latest_json


def enhance_database_with_locations():
    """Enhance the database with state and city information."""
    print("🌍 Database Location Enhancer")
    print("=" * 50)
    
    # Find latest database files
    csv_file, json_file = find_latest_database_files()
    
    if not csv_file:
        print("❌ No database CSV file found!")
        return
    
    print(f"📁 Found database file: {csv_file}")
    
    # Initialize location extractor
    extractor = LocationExtractor()
    
    # Read existing data
    enhanced_data = []
    total_processed = 0
    locations_found = 0
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['state', 'city', 'location_summary', 'location_method']
        
        print(f"📊 Processing {csv_file}...")
        print("🔍 Extracting location information from URLs...")
        
        for row in reader:
            total_processed += 1
            url = row.get('website', '')
            
            if url:
                # Extract location information
                location_info = extractor.extract_location_info(url)
                location_summary = extractor.get_location_summary(location_info)
                
                # Add location data to row
                row['state'] = location_info.get('state', '')
                row['city'] = location_info.get('city', '')
                row['location_summary'] = location_summary
                row['location_method'] = location_info.get('method', '')
                
                if location_info.get('state') or location_info.get('city'):
                    locations_found += 1
                    
                print(f"  {total_processed:3d}. {row.get('name', 'Unknown'):30s} -> {location_summary}")
            else:
                # No URL, set empty location fields
                row['state'] = ''
                row['city'] = ''
                row['location_summary'] = 'No URL provided'
                row['location_method'] = 'none'
            
            enhanced_data.append(row)
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_csv = f"ENHANCED_HEALTHCARE_DATABASE_WITH_LOCATIONS_{timestamp}.csv"
    output_json = f"ENHANCED_HEALTHCARE_DATABASE_WITH_LOCATIONS_{timestamp}.json"
    
    # Write enhanced CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enhanced_data)
    
    # Write enhanced JSON
    with open(output_json, 'w', encoding='utf-8') as outfile:
        json.dump(enhanced_data, outfile, indent=2, ensure_ascii=False)
    
    # Generate summary statistics
    state_counts = {}
    city_counts = {}
    country_counts = {}
    
    for row in enhanced_data:
        if row.get('state'):
            state_counts[row['state']] = state_counts.get(row['state'], 0) + 1
        if row.get('city'):
            city_counts[row['city']] = city_counts.get(row['city'], 0) + 1
        if row.get('country'):
            country_counts[row['country']] = country_counts.get(row['country'], 0) + 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 LOCATION ENHANCEMENT SUMMARY")
    print("=" * 50)
    print(f"Total companies processed: {total_processed}")
    print(f"Companies with location data: {locations_found}")
    print(f"Success rate: {(locations_found/total_processed)*100:.1f}%" if total_processed > 0 else "0%")
    
    print(f"\n📁 Enhanced database saved as:")
    print(f"   CSV: {output_csv}")
    print(f"   JSON: {output_json}")
    
    # Top states
    if state_counts:
        print(f"\n🏛️ TOP STATES/REGIONS:")
        for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {state}: {count}")
    
    # Top cities
    if city_counts:
        print(f"\n🏙️ TOP CITIES:")
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {city}: {count}")
    
    # Countries
    if country_counts:
        print(f"\n🌍 COUNTRIES:")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {country}: {count}")
    
    return output_csv, output_json


def analyze_database_locations(csv_file):
    """Analyze location patterns in the enhanced database."""
    print(f"\n🔍 DETAILED LOCATION ANALYSIS")
    print("=" * 50)
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = list(reader)
        
        print(f"📊 Analyzing {len(data)} companies...")
        
        # Group by location method
        method_counts = {}
        for row in data:
            method = row.get('location_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        print(f"\n📋 LOCATION EXTRACTION METHODS:")
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {method}: {count}")
        
        # Companies with specific location data
        companies_with_states = [row for row in data if row.get('state')]
        companies_with_cities = [row for row in data if row.get('city')]
        
        print(f"\n🎯 SPECIFIC LOCATION DATA:")
        print(f"   Companies with state/region: {len(companies_with_states)}")
        print(f"   Companies with city: {len(companies_with_cities)}")
        
        # Show some examples
        print(f"\n🏢 EXAMPLES OF COMPANIES WITH DETAILED LOCATIONS:")
        detailed_companies = [row for row in data if row.get('state') and row.get('city')]
        
        for i, company in enumerate(detailed_companies[:10]):
            print(f"   {i+1:2d}. {company.get('name', 'Unknown'):25s} - {company.get('location_summary', 'N/A')}")
        
        if len(detailed_companies) > 10:
            print(f"   ... and {len(detailed_companies) - 10} more companies with detailed locations")
    
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")


def main():
    """Main function to enhance database with location information."""
    try:
        # Enhance the database
        output_csv, output_json = enhance_database_with_locations()
        
        if output_csv:
            # Analyze the enhanced database
            analyze_database_locations(output_csv)
            
            print(f"\n✅ Location enhancement completed successfully!")
            print(f"🎉 Enhanced database files created with state and city information.")
        
    except Exception as e:
        print(f"❌ Error during database enhancement: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
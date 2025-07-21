#!/usr/bin/env python3
"""
📊 Location Analysis Summary
============================
Comprehensive analysis of location data extracted from healthcare company URLs.
"""

import csv
import json
from collections import Counter, defaultdict


def analyze_enhanced_database():
    """Analyze the enhanced database with location information."""
    csv_file = "ENHANCED_HEALTHCARE_DATABASE_WITH_LOCATIONS_20250721_125857.csv"
    
    print("📊 COMPREHENSIVE LOCATION ANALYSIS")
    print("=" * 70)
    
    try:
        # Read the data
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        
        print(f"📁 Database: {csv_file}")
        print(f"📈 Total companies: {len(data)}")
        
        # Separate data by location availability
        companies_with_locations = [row for row in data if row.get('state') or row.get('city')]
        companies_without_locations = [row for row in data if not (row.get('state') or row.get('city'))]
        
        print(f"🎯 Companies with location data: {len(companies_with_locations)}")
        print(f"❌ Companies without location data: {len(companies_without_locations)}")
        print(f"✅ Location extraction success rate: {(len(companies_with_locations)/len(data))*100:.1f}%")
        
        # Country distribution
        print(f"\n🌍 COUNTRY DISTRIBUTION")
        print("-" * 40)
        country_counts = Counter([row.get('country', 'Unknown') for row in data])
        for country, count in country_counts.most_common():
            print(f"  {country:25s}: {count:3d} companies")
        
        # State/Region analysis
        print(f"\n🏛️ STATE/REGION ANALYSIS")
        print("-" * 40)
        state_counts = Counter([row.get('state') for row in data if row.get('state')])
        
        if state_counts:
            print(f"Total states/regions identified: {len(state_counts)}")
            print("Top states/regions:")
            for state, count in state_counts.most_common(10):
                print(f"  {state:25s}: {count:3d} companies")
        else:
            print("No state/region data found")
        
        # City analysis
        print(f"\n🏙️ CITY ANALYSIS")
        print("-" * 40)
        city_counts = Counter([row.get('city') for row in data if row.get('city')])
        
        if city_counts:
            print(f"Total cities identified: {len(city_counts)}")
            print("Top cities:")
            for city, count in city_counts.most_common(10):
                print(f"  {city:25s}: {count:3d} companies")
        else:
            print("No city data found")
        
        # Location extraction method analysis
        print(f"\n🔍 EXTRACTION METHOD ANALYSIS")
        print("-" * 40)
        method_counts = Counter([row.get('location_method', 'unknown') for row in data])
        for method, count in method_counts.most_common():
            print(f"  {method:25s}: {count:3d} companies")
        
        # Detailed location combinations
        print(f"\n📍 DETAILED LOCATION COMBINATIONS")
        print("-" * 40)
        location_combinations = defaultdict(list)
        
        for row in data:
            state = row.get('state', '')
            city = row.get('city', '')
            country = row.get('country', 'Unknown')
            
            if state or city:
                key = f"{city}, {state}, {country}".strip(', ')
                location_combinations[key].append(row.get('name', 'Unknown'))
        
        print(f"Unique location combinations: {len(location_combinations)}")
        for location, companies in sorted(location_combinations.items(), key=lambda x: len(x[1]), reverse=True):
            company_list = ", ".join(companies[:3])  # Show first 3 companies
            more_text = f" (and {len(companies)-3} more)" if len(companies) > 3 else ""
            print(f"  {location:35s}: {company_list}{more_text}")
        
        # German-specific analysis (since many companies are German)
        german_companies = [row for row in data if 'Germany' in row.get('country', '')]
        if german_companies:
            print(f"\n🇩🇪 GERMAN COMPANIES ANALYSIS")
            print("-" * 40)
            print(f"Total German companies: {len(german_companies)}")
            
            german_with_locations = [row for row in german_companies if row.get('state') or row.get('city')]
            print(f"German companies with location data: {len(german_with_locations)}")
            print(f"German location success rate: {(len(german_with_locations)/len(german_companies))*100:.1f}%")
            
            # German cities
            german_cities = Counter([row.get('city') for row in german_companies if row.get('city')])
            if german_cities:
                print("Top German cities:")
                for city, count in german_cities.most_common(5):
                    print(f"  {city:25s}: {count:3d} companies")
        
        # Companies needing manual review
        print(f"\n⚠️ COMPANIES NEEDING MANUAL REVIEW")
        print("-" * 40)
        
        # Companies with no location data
        no_location_companies = [row for row in data if not row.get('state') and not row.get('city')]
        if no_location_companies:
            print(f"Companies without location data ({len(no_location_companies)}):")
            for row in no_location_companies[:10]:  # Show first 10
                url = row.get('website', 'No URL')
                print(f"  {row.get('name', 'Unknown'):25s} - {url}")
            if len(no_location_companies) > 10:
                print(f"  ... and {len(no_location_companies) - 10} more")
        
        # Potential data quality issues
        print(f"\n🔧 DATA QUALITY ANALYSIS")
        print("-" * 40)
        
        # Check for unusual location combinations
        unusual_combinations = []
        for row in data:
            city = row.get('city', '')
            state = row.get('state', '')
            country = row.get('country', '')
            
            # Check for potential mismatches (e.g., German city with US state)
            if ('Germany' in country or '.de' in row.get('website', '')) and state in ['Alabama', 'California', 'Delaware']:
                unusual_combinations.append({
                    'name': row.get('name', 'Unknown'),
                    'city': city,
                    'state': state,
                    'country': country,
                    'url': row.get('website', '')
                })
        
        if unusual_combinations:
            print(f"Potential location mismatches found ({len(unusual_combinations)}):")
            for combo in unusual_combinations[:5]:
                print(f"  {combo['name']:25s} - {combo['city']}, {combo['state']}, {combo['country']}")
                print(f"    URL: {combo['url']}")
        
        # Summary statistics
        print(f"\n📈 SUMMARY STATISTICS")
        print("-" * 40)
        
        total_countries = len(set([row.get('country') for row in data if row.get('country')]))
        total_states = len(set([row.get('state') for row in data if row.get('state')]))
        total_cities = len(set([row.get('city') for row in data if row.get('city')]))
        
        print(f"Total unique countries: {total_countries}")
        print(f"Total unique states/regions: {total_states}")
        print(f"Total unique cities: {total_cities}")
        print(f"Average locations per company: {(total_states + total_cities) / len(data):.2f}")
        
        # Success rate by domain TLD
        print(f"\n🌐 SUCCESS RATE BY DOMAIN TYPE")
        print("-" * 40)
        
        tld_stats = defaultdict(lambda: {'total': 0, 'with_location': 0})
        
        for row in data:
            url = row.get('website', '')
            if '.de' in url:
                tld = '.de'
            elif '.com' in url:
                tld = '.com'
            elif any(tld in url for tld in ['.co', '.eu', '.ai', '.health']):
                if '.co' in url:
                    tld = '.co'
                elif '.eu' in url:
                    tld = '.eu'
                elif '.ai' in url:
                    tld = '.ai'
                elif '.health' in url:
                    tld = '.health'
            else:
                tld = 'other'
            
            tld_stats[tld]['total'] += 1
            if row.get('state') or row.get('city'):
                tld_stats[tld]['with_location'] += 1
        
        for tld, stats in sorted(tld_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            total = stats['total']
            with_loc = stats['with_location']
            rate = (with_loc / total * 100) if total > 0 else 0
            print(f"  {tld:10s}: {with_loc:2d}/{total:2d} companies ({rate:5.1f}% success rate)")
        
        print(f"\n✅ Analysis completed!")
        print(f"📁 Enhanced database available at: {csv_file}")
        
    except FileNotFoundError:
        print(f"❌ Error: Enhanced database file not found: {csv_file}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_enhanced_database()
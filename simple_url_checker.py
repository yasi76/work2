#!/usr/bin/env python3
"""
Simple URL Validator for Healthcare Companies
Uses only standard library modules
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
from datetime import datetime

# Your manually found URLs to validate
MANUAL_URLS = [
    'https://www.acalta.de',
    'https://www.actimi.com',
    'https://www.emmora.de',
    'https://www.alfa-ai.com',
    'https://www.apheris.com',
    'https://www.aporize.com/',
    'https://www.arztlena.com/',
    'https://shop.getnutrio.com/',
    'https://www.auta.health/',
    'https://visioncheckout.com/',
    'https://www.avayl.tech/',
    'https://www.avimedical.com/avi-impact',
    'https://de.becureglobal.com/',
    'https://bellehealth.co/de/',
    'https://www.biotx.ai/',
    'https://www.brainjo.de/',
    'https://brea.app/',
    'https://breathment.com/',
    'https://de.caona.eu/',
    'https://www.careanimations.de/',
    'https://sfs-healthcare.com',
    'https://www.climedo.de/',
    'https://www.cliniserve.de/',
    'https://cogthera.de/#erfahren',
    'https://www.comuny.de/',
    'https://curecurve.de/elina-app/',
    'https://www.cynteract.com/de/rehabilitation',
    'https://www.healthmeapp.de/de/',
    'https://deepeye.ai/',
    'https://www.deepmentation.ai/',
    'https://denton-systems.de/',
    'https://www.derma2go.com/',
    'https://www.dianovi.com/',
    'http://dopavision.com/',
    'https://www.dpv-analytics.com/',
    'http://www.ecovery.de/',
    'https://elixionmedical.com/',
    'https://www.empident.de/',
    'https://eye2you.ai/',
    'https://www.fitwhit.de',
    'https://www.floy.com/',
    'https://fyzo.de/assistant/',
    'https://www.gesund.de/app',
    'https://www.glaice.de/',
    'https://gleea.de/',
    'https://www.guidecare.de/',
    'https://www.apodienste.com/',
    'https://www.help-app.de/',
    'https://www.heynanny.com/',
    'https://incontalert.de/',
    'https://home.informme.info/',
    'https://www.kranushealth.com/de/therapien/haeufiger-harndrang',
    'https://www.kranushealth.com/de/therapien/inkontinenz'
]

# Additional companies found from research
RESEARCH_URLS = [
    'https://lillian-care.de/en/',
    'https://www.doctorly.de/',
    'https://www.roodie-health.com/',
    'https://praxis-eins.de/',
    'https://curecurve.de/',
    'https://www.elona.health/',
    'https://bayern.teleclinic.com/',
    'https://www.vantis-health.com/de/',
    'https://www.flyinghealth.com/',
    'https://www.gomedicus.com/'
]

def validate_url_simple(url, timeout=10):
    """
    Simple URL validation using urllib
    Returns: (is_valid, status_code, title)
    """
    try:
        # Clean up URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Create request with headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # Make the request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8', errors='ignore')
            
            # Extract title
            title = ""
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'\s+', ' ', title)
            
            return True, status_code, title
            
    except Exception as e:
        return False, 0, str(e)

def extract_domain_info(url):
    """Extract domain information from URL"""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    
    # Determine country based on TLD
    country_map = {
        '.de': 'Germany',
        '.com': 'International/US',
        '.eu': 'European Union',
        '.uk': 'United Kingdom',
        '.co.uk': 'United Kingdom',
        '.fr': 'France',
        '.nl': 'Netherlands',
        '.se': 'Sweden',
        '.dk': 'Denmark',
        '.no': 'Norway',
        '.fi': 'Finland',
        '.ch': 'Switzerland',
        '.at': 'Austria',
        '.be': 'Belgium',
        '.it': 'Italy',
        '.es': 'Spain',
        '.pl': 'Poland',
        '.health': 'Health Domain',
        '.app': 'App Domain',
        '.ai': 'AI Domain',
        '.tech': 'Tech Domain'
    }
    
    country = "Unknown"
    for tld, country_name in country_map.items():
        if domain.endswith(tld):
            country = country_name
            break
    
    return domain, country

def categorize_healthcare_type(url, title):
    """Categorize healthcare solution type"""
    content = (url + " " + title).lower()
    
    # Healthcare categories with keywords
    categories = [
        ('Digital Health Platform', ['platform', 'digital health', 'health tech', 'healthtech']),
        ('Telemedicine', ['telemedicine', 'teleclinic', 'telehealth', 'video consultation', 'remote']),
        ('AI/ML Healthcare', ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning']),
        ('Medical Devices', ['medical device', 'medtech', 'diagnostic', 'monitoring device']),
        ('Mental Health', ['mental health', 'psychology', 'therapy', 'depression', 'anxiety']),
        ('Practice Management', ['practice management', 'clinic management', 'appointment', 'scheduling']),
        ('Pharmaceutical', ['pharma', 'drug', 'medication', 'pharmaceutical']),
        ('Wearables/IoT', ['wearable', 'iot', 'sensor', 'monitoring', 'tracker']),
        ('Healthcare Analytics', ['analytics', 'data analysis', 'insights', 'reporting']),
        ('Patient Care', ['patient care', 'care management', 'patient portal']),
        ('Rehabilitation', ['rehabilitation', 'therapy', 'recovery', 'physio']),
        ('Diagnostics', ['diagnostic', 'diagnosis', 'screening', 'test'])
    ]
    
    for category, keywords in categories:
        if any(keyword in content for keyword in keywords):
            return category
    
    return 'Other'

def main():
    """Main function"""
    print("European Healthcare Startups & SMEs Database Validator")
    print("=" * 60)
    
    all_urls = MANUAL_URLS + RESEARCH_URLS
    results = []
    
    print(f"Validating {len(all_urls)} URLs...")
    print()
    
    active_count = 0
    inactive_count = 0
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i:2d}/{len(all_urls)}] {url}")
        
        # Validate URL
        is_valid, status_code, title = validate_url_simple(url)
        domain, country = extract_domain_info(url)
        healthcare_type = categorize_healthcare_type(url, title)
        
        status = 'Active' if is_valid and status_code == 200 else 'Inactive'
        if status == 'Active':
            active_count += 1
        else:
            inactive_count += 1
        
        result = {
            'URL': url,
            'Domain': domain,
            'Country': country,
            'Status': status,
            'Status_Code': status_code,
            'Title': title[:80] + '...' if len(title) > 80 else title,
            'Healthcare_Type': healthcare_type,
            'Source': 'Manual' if url in MANUAL_URLS else 'Research',
            'Validated_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        results.append(result)
        
        # Status display
        status_symbol = "✓" if status == 'Active' else "✗"
        print(f"      {status_symbol} {status} ({status_code}) - {title[:60]}")
        print()
        
        # Rate limiting
        time.sleep(1)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total URLs checked: {len(all_urls)}")
    print(f"Active companies: {active_count} ({active_count/len(all_urls)*100:.1f}%)")
    print(f"Inactive/Error: {inactive_count} ({inactive_count/len(all_urls)*100:.1f}%)")
    
    # Country breakdown
    countries = {}
    for result in results:
        if result['Status'] == 'Active':
            country = result['Country']
            countries[country] = countries.get(country, 0) + 1
    
    print(f"\nActive companies by country:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {count}")
    
    # Healthcare type breakdown
    types = {}
    for result in results:
        if result['Status'] == 'Active':
            hc_type = result['Healthcare_Type']
            types[hc_type] = types.get(hc_type, 0) + 1
    
    print(f"\nActive companies by healthcare type:")
    for hc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {hc_type}: {count}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # CSV output
    csv_filename = f'european_healthcare_companies_{timestamp}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # JSON output
    json_filename = f'european_healthcare_companies_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"\nFiles saved:")
    print(f"  - {csv_filename}")
    print(f"  - {json_filename}")
    
    # Show active companies
    print(f"\n🎯 ACTIVE COMPANIES ({active_count} total):")
    print("-" * 80)
    for result in results:
        if result['Status'] == 'Active':
            print(f"✓ {result['URL']}")
            print(f"  📍 {result['Country']} | 🏥 {result['Healthcare_Type']}")
            print(f"  📝 {result['Title']}")
            print()

if __name__ == "__main__":
    main()
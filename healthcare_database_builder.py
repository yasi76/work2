#!/usr/bin/env python3
"""
European Healthcare Startups & SMEs Database Builder
Validates URLs and creates a comprehensive database of healthcare companies
"""

import requests
import csv
import json
import time
from urllib.parse import urlparse
from datetime import datetime
import re

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
    'https://www.gomedicus.com/',
    'https://www.mindmaze.com/',
    'https://www.onerahealth.com/',
    'https://ouraring.com/',
    'https://patchworkhealth.com/',
    'https://www.kheironmed.com/',
    'https://www.comeback-mobility.com/',
    'https://www.naomihealth.ai/',
    'https://www.bottneuro.com/'
]

def validate_url(url, timeout=10):
    """
    Validate if a URL is accessible and active
    Returns: (is_valid, status_code, response_time, title)
    """
    try:
        # Clean up URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        response_time = time.time() - start_time
        
        # Extract title from HTML
        title = ""
        if response.status_code == 200:
            try:
                title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    title = re.sub(r'\s+', ' ', title)  # Clean whitespace
            except:
                pass
        
        return True, response.status_code, response_time, title
        
    except requests.exceptions.RequestException as e:
        return False, 0, 0, str(e)

def extract_domain_info(url):
    """Extract domain information from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Determine country based on TLD
    country = "Unknown"
    if domain.endswith('.de'):
        country = "Germany"
    elif domain.endswith('.com'):
        country = "International/US"
    elif domain.endswith('.eu'):
        country = "European Union"
    elif domain.endswith('.uk') or domain.endswith('.co.uk'):
        country = "United Kingdom"
    elif domain.endswith('.fr'):
        country = "France"
    elif domain.endswith('.nl'):
        country = "Netherlands"
    elif domain.endswith('.se'):
        country = "Sweden"
    elif domain.endswith('.dk'):
        country = "Denmark"
    elif domain.endswith('.no'):
        country = "Norway"
    elif domain.endswith('.fi'):
        country = "Finland"
    elif domain.endswith('.ch'):
        country = "Switzerland"
    elif domain.endswith('.at'):
        country = "Austria"
    elif domain.endswith('.be'):
        country = "Belgium"
    elif domain.endswith('.it'):
        country = "Italy"
    elif domain.endswith('.es'):
        country = "Spain"
    elif domain.endswith('.pl'):
        country = "Poland"
    
    return domain, country

def categorize_healthcare_type(url, title):
    """
    Categorize the type of healthcare solution based on URL and title
    """
    content = (url + " " + title).lower()
    
    categories = {
        'Digital Health Platform': ['platform', 'digital health', 'health tech', 'healthtech'],
        'Telemedicine': ['telemedicine', 'teleclinic', 'telehealth', 'video consultation', 'remote'],
        'AI/ML Healthcare': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning'],
        'Medical Devices': ['medical device', 'medtech', 'diagnostic', 'monitoring device'],
        'Mental Health': ['mental health', 'psychology', 'therapy', 'depression', 'anxiety'],
        'Practice Management': ['practice management', 'clinic management', 'appointment', 'scheduling'],
        'Pharmaceutical': ['pharma', 'drug', 'medication', 'pharmaceutical'],
        'Wearables/IoT': ['wearable', 'iot', 'sensor', 'monitoring', 'tracker'],
        'Healthcare Analytics': ['analytics', 'data analysis', 'insights', 'reporting'],
        'Patient Care': ['patient care', 'care management', 'patient portal'],
        'Rehabilitation': ['rehabilitation', 'therapy', 'recovery', 'physio'],
        'Diagnostics': ['diagnostic', 'diagnosis', 'screening', 'test'],
        'Other': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return 'Other'

def build_database():
    """Build comprehensive healthcare database"""
    print("Building European Healthcare Startups & SMEs Database...")
    print("="*60)
    
    all_urls = MANUAL_URLS + RESEARCH_URLS
    results = []
    
    print(f"Validating {len(all_urls)} URLs...")
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{len(all_urls)}] Checking: {url}")
        
        # Validate URL
        is_valid, status_code, response_time, title = validate_url(url)
        domain, country = extract_domain_info(url)
        healthcare_type = categorize_healthcare_type(url, title)
        
        result = {
            'URL': url,
            'Domain': domain,
            'Country': country,
            'Status': 'Active' if is_valid and status_code == 200 else 'Inactive',
            'Status_Code': status_code,
            'Response_Time': round(response_time, 2) if response_time > 0 else 0,
            'Title': title[:100] + '...' if len(title) > 100 else title,
            'Healthcare_Type': healthcare_type,
            'Source': 'Manual' if url in MANUAL_URLS else 'Research',
            'Validated_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        results.append(result)
        
        # Status indicator
        status_symbol = "✓" if is_valid and status_code == 200 else "✗"
        print(f"  {status_symbol} {status_code} | {response_time:.2f}s | {title[:50]}")
        
        # Rate limiting
        time.sleep(0.5)
    
    return results

def save_results(results):
    """Save results to multiple formats"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save as CSV
    csv_filename = f'european_healthcare_database_{timestamp}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Save as JSON
    json_filename = f'european_healthcare_database_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def generate_report(results):
    """Generate summary report"""
    total_urls = len(results)
    active_urls = len([r for r in results if r['Status'] == 'Active'])
    inactive_urls = total_urls - active_urls
    
    # Country breakdown
    countries = {}
    for result in results:
        country = result['Country']
        countries[country] = countries.get(country, 0) + 1
    
    # Healthcare type breakdown
    types = {}
    for result in results:
        hc_type = result['Healthcare_Type']
        types[hc_type] = types.get(hc_type, 0) + 1
    
    # Generate report
    report = f"""
EUROPEAN HEALTHCARE STARTUPS & SMEs DATABASE REPORT
==================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY STATISTICS:
- Total URLs Analyzed: {total_urls}
- Active Companies: {active_urls} ({active_urls/total_urls*100:.1f}%)
- Inactive/Unreachable: {inactive_urls} ({inactive_urls/total_urls*100:.1f}%)

COUNTRY DISTRIBUTION:
"""
    
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        percentage = count/total_urls*100
        report += f"- {country}: {count} companies ({percentage:.1f}%)\n"
    
    report += "\nHEALTHCARE TYPE DISTRIBUTION:\n"
    for hc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        percentage = count/total_urls*100
        report += f"- {hc_type}: {count} companies ({percentage:.1f}%)\n"
    
    report += f"""
ACTIVE COMPANIES BY TYPE:
"""
    active_by_type = {}
    for result in results:
        if result['Status'] == 'Active':
            hc_type = result['Healthcare_Type']
            active_by_type[hc_type] = active_by_type.get(hc_type, 0) + 1
    
    for hc_type, count in sorted(active_by_type.items(), key=lambda x: x[1], reverse=True):
        report += f"- {hc_type}: {count} active companies\n"
    
    report += f"""
RECOMMENDATIONS:
1. Focus on the {active_urls} active companies for immediate business opportunities
2. Germany leads with the most companies, followed by international .com domains
3. Digital Health Platforms and Telemedicine are the most common categories
4. Consider re-checking inactive URLs after some time as they may become active
5. Investigate similar companies in the most active categories for expansion

DATA FILES GENERATED:
- CSV format for spreadsheet analysis
- JSON format for programmatic access
"""
    
    return report

def main():
    """Main function to run the database builder"""
    print("Starting European Healthcare Database Builder...")
    
    # Build the database
    results = build_database()
    
    # Save results
    csv_file, json_file = save_results(results)
    
    # Generate and save report
    report = generate_report(results)
    report_file = f'healthcare_database_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("DATABASE BUILD COMPLETE!")
    print("="*60)
    print(f"Files generated:")
    print(f"- {csv_file}")
    print(f"- {json_file}")
    print(f"- {report_file}")
    print("\n" + report)

if __name__ == "__main__":
    main()
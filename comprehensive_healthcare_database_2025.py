#!/usr/bin/env python3
"""
Comprehensive European Healthcare Startups & SMEs Database Builder
Combines existing validated URLs with new discoveries from web searches
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
from datetime import datetime
from urllib.parse import urlparse

# Updated comprehensive list of healthcare companies
COMPREHENSIVE_HEALTHCARE_URLS = [
    # Previously validated URLs
    'https://www.acalta.de',
    'https://www.actimi.com',
    'https://www.emmora.de',
    'https://www.alfa-ai.com',
    'https://www.apheris.com',
    'https://www.aporize.com/',
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
    'https://www.careanimations.de/',
    'https://sfs-healthcare.com',
    'https://www.climedo.de/',
    'https://www.cliniserve.de/',
    'https://cogthera.de/',
    'https://www.comuny.de/',
    'https://curecurve.de/elina-app/',
    'https://www.cynteract.com/de/rehabilitation',
    'https://www.healthmeapp.de/de/',
    'https://deepeye.ai/',
    'https://www.deepmentation.ai/',
    'https://denton-systems.de/',
    'https://www.derma2go.com/',
    'https://www.dianovi.com/',
    'https://www.dpv-analytics.com/',
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
    'https://www.kranushealth.com/',
    
    # New discoveries from web searches
    'https://www.angell-tech.com',
    'https://www.doctorly.de',
    'https://www.roodie-health.com',
    'https://goyahealth.de',
    'https://www.gostalabs.com',
    'https://beehealthy.com',
    'https://www.healthcaters.ai',
    'https://www.elona.health',
    'https://www.longevity-ai.com',
    'https://curecurve.de',
    'https://www.telehealth.de',
    'https://www.flyinghealth.com',
    'https://www.hihealth.de',
    'https://patient21.com',
    'https://praxis-eins.de',
    'https://kumihealth.de',
    'https://www.avelios.com',
    'https://www.drwait.de',
    
    # Norwegian healthcare companies
    'https://www.kry.no',
    'https://dignio.com',
    'https://www.nettlegevakt.no',
    'https://www.norsefeedback.no',
    'https://hjemmelegene.no',
    'https://smartlegen.no',
    
    # German health tech from Seedtable listings
    'https://odysseytx.com',
    'https://www.modag.com',
    'https://www.greencitysolutions.com',
    'https://www.heidelberg-pharma.com',
    'https://www.tubulis.com',
    'https://cytena.com',
    'https://advancecor.com',
    'https://rapidmicrobio.com',
    'https://www.formo.bio',
    'https://innoplexus.com',
    'https://www.caresyntax.com',
    'https://www.centogene.com',
    'https://changers.com',
    'https://paion.com',
    'https://www.hummingbird.de',
    'https://www.m2p-labs.com',
    'https://www.molecularhealth.com',
    'https://ottobock.com',
    'https://www.novaliq.com',
    'https://oncgnostics.com',
    'https://www.diamontech.de',
    'https://heartbeat-medical.com',
    'https://zava.com',
    'https://unitelabs.io',
    'https://neoplas.com',
    'https://omeicos.com',
    'https://www.ekfdiagnostics.com',
    'https://analyticon.com',
    'https://atriva.com',
    'https://topas-therapeutics.com',
    'https://illuminoss.com',
    'https://aicuris.com',
    'https://oaklabs.com',
    'https://4teen4.de',
    'https://allecra.com',
    'https://neuway-pharma.com',
    'https://merlion-pharma.com',
    'https://differential.bio',
    'https://lucid-genomics.com',
    'https://more.science',
    'https://www.eucalyptus.com',
    'https://eleva.de',
    'https://nuuron.com',
    'https://actitrexx.com',
    'https://pepperprint.com',
    'https://algiax.com',
    'https://hema.to',
    'https://indivumed.com',
    'https://sympatient.com',
    'https://luxendo.com',
    'https://ovo-labs.com',
    'https://proteros.com',
    'https://preomics.com',
    'https://medloop.com',
    'https://apogenix.com',
    
    # Recently funded German startups
    'https://ovom.care',
    'https://aera.health',
    'https://likeminded.care',
    'https://theblood.co',
    'https://mindahead.io',
]

def get_domain_info(url):
    """Extract domain and country information from URL"""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Determine likely country based on domain
        if domain.endswith('.de'):
            country = 'Germany'
        elif domain.endswith('.no'):
            country = 'Norway'
        elif domain.endswith('.se'):
            country = 'Sweden'
        elif domain.endswith('.dk'):
            country = 'Denmark'
        elif domain.endswith('.fi'):
            country = 'Finland'
        elif domain.endswith('.nl'):
            country = 'Netherlands'
        elif domain.endswith('.be'):
            country = 'Belgium'
        elif domain.endswith('.fr'):
            country = 'France'
        elif domain.endswith('.it'):
            country = 'Italy'
        elif domain.endswith('.es'):
            country = 'Spain'
        elif domain.endswith('.at'):
            country = 'Austria'
        elif domain.endswith('.ch'):
            country = 'Switzerland'
        elif domain.endswith('.uk') or domain.endswith('.co.uk'):
            country = 'United Kingdom'
        elif domain.endswith('.ie'):
            country = 'Ireland'
        elif domain.endswith('.eu'):
            country = 'European Union'
        elif domain.endswith('.com') or domain.endswith('.org') or domain.endswith('.net'):
            if 'berlin' in domain or 'munich' in domain or 'hamburg' in domain:
                country = 'Germany'
            elif 'oslo' in domain or 'bergen' in domain:
                country = 'Norway'
            else:
                country = 'International/US'
        else:
            country = 'Unknown'
        
        return domain, country
    except Exception as e:
        return url, 'Unknown'

def categorize_healthcare_type(url, title, content=''):
    """Categorize the type of healthcare solution based on URL, title and content"""
    combined_text = f"{url} {title} {content}".lower()
    
    # AI/ML Healthcare
    if any(keyword in combined_text for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural', 'algorithm']):
        return 'AI/ML Healthcare'
    
    # Digital Health Platform
    if any(keyword in combined_text for keyword in ['digital health', 'platform', 'app', 'digital', 'praxis', 'clinic']):
        return 'Digital Health Platform'
    
    # Telemedicine
    if any(keyword in combined_text for keyword in ['telemedicine', 'telehealth', 'video', 'remote', 'online doctor', 'digital doctor', 'lege']):
        return 'Telemedicine'
    
    # Diagnostics
    if any(keyword in combined_text for keyword in ['diagnostic', 'diagnostics', 'test', 'screening', 'biomarker', 'analysis']):
        return 'Diagnostics'
    
    # Mental Health
    if any(keyword in combined_text for keyword in ['mental health', 'psychology', 'psychiatry', 'therapy', 'depression', 'anxiety']):
        return 'Mental Health'
    
    # Wearables/IoT
    if any(keyword in combined_text for keyword in ['wearable', 'iot', 'sensor', 'monitoring', 'tracker', 'device']):
        return 'Wearables/IoT'
    
    # Pharmaceuticals
    if any(keyword in combined_text for keyword in ['pharma', 'drug', 'therapeutic', 'medicine', 'prescription']):
        return 'Pharmaceuticals'
    
    # Healthcare Management
    if any(keyword in combined_text for keyword in ['management', 'administration', 'billing', 'scheduling', 'workflow']):
        return 'Healthcare Management'
    
    return 'Other'

def validate_url(url):
    """Validate URL and extract basic information"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8', errors='ignore')
            
            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ''
            
            # Clean up title
            if len(title) > 100:
                title = title[:97] + '...'
            
            domain, country = get_domain_info(url)
            healthcare_type = categorize_healthcare_type(url, title, content[:1000])
            
            return {
                'url': url,
                'domain': domain,
                'country': country,
                'status': 'Active',
                'status_code': status_code,
                'title': title,
                'healthcare_type': healthcare_type,
                'source': 'Comprehensive Search',
                'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
    except urllib.error.HTTPError as e:
        domain, country = get_domain_info(url)
        return {
            'url': url,
            'domain': domain,
            'country': country,
            'status': 'HTTP Error',
            'status_code': e.code,
            'title': f'HTTP {e.code} Error',
            'healthcare_type': 'Other',
            'source': 'Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except urllib.error.URLError as e:
        domain, country = get_domain_info(url)
        return {
            'url': url,
            'domain': domain,
            'country': country,
            'status': 'Inactive',
            'status_code': 0,
            'title': str(e.reason),
            'healthcare_type': 'Other',
            'source': 'Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        domain, country = get_domain_info(url)
        return {
            'url': url,
            'domain': domain,
            'country': country,
            'status': 'Error',
            'status_code': 0,
            'title': str(e),
            'healthcare_type': 'Other',
            'source': 'Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    print("🏥 Building Comprehensive European Healthcare Database...")
    print(f"📊 Total URLs to validate: {len(COMPREHENSIVE_HEALTHCARE_URLS)}")
    
    results = []
    
    for i, url in enumerate(COMPREHENSIVE_HEALTHCARE_URLS, 1):
        print(f"🔍 Validating {i}/{len(COMPREHENSIVE_HEALTHCARE_URLS)}: {url}")
        
        result = validate_url(url)
        results.append(result)
        
        print(f"✅ {result['status']} - {result['title'][:50]}...")
        
        # Add delay to be respectful
        time.sleep(1)
    
    # Create timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to CSV
    csv_filename = f'comprehensive_european_healthcare_companies_{timestamp}.csv'
    csv_headers = ['URL', 'Domain', 'Country', 'Status', 'Status_Code', 'Title', 'Healthcare_Type', 'Source', 'Validated_Date']
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)
        
        for result in results:
            writer.writerow([
                result['url'],
                result['domain'],
                result['country'],
                result['status'],
                result['status_code'],
                result['title'],
                result['healthcare_type'],
                result['source'],
                result['validated_date']
            ])
    
    # Save to JSON
    json_filename = f'comprehensive_european_healthcare_companies_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, ensure_ascii=False)
    
    # Print summary statistics
    print("\n🎯 Database Summary:")
    print(f"📁 CSV file: {csv_filename}")
    print(f"📁 JSON file: {json_filename}")
    print(f"📊 Total companies: {len(results)}")
    
    # Status breakdown
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📈 Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")
    
    # Country breakdown
    country_counts = {}
    for result in results:
        country = result['country']
        country_counts[country] = country_counts.get(country, 0) + 1
    
    print("\n🌍 Country Breakdown:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {country}: {count}")
    
    # Healthcare type breakdown
    type_counts = {}
    for result in results:
        hc_type = result['healthcare_type']
        type_counts[hc_type] = type_counts.get(hc_type, 0) + 1
    
    print("\n🏥 Healthcare Type Breakdown:")
    for hc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {hc_type}: {count}")
    
    print(f"\n✅ Comprehensive European Healthcare Database completed!")
    print(f"📊 Active companies: {status_counts.get('Active', 0)}")
    print(f"📊 Total companies processed: {len(results)}")

if __name__ == "__main__":
    main()
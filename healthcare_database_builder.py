#!/usr/bin/env python3
"""
European Healthcare Startups & SMEs Database Builder
Validates URLs and creates a comprehensive database of healthcare companies
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

# Additional European healthcare companies discovered through research
ADDITIONAL_URLS = [
    # German companies
    'https://www.doctolib.de/',
    'https://www.nect.com/',
    'https://www.deepc.ai/',
    'https://www.vivy.com/',
    'https://www.kaia-health.com/',
    'https://www.mindpeak.ai/',
    'https://www.medbelle.com/',
    'https://www.diagnosia.com/',
    'https://www.medwing.com/',
    'https://www.medlanes.com/',
    
    # UK companies
    'https://www.babylon-health.com/',
    'https://www.zava.com/',
    'https://www.sensyne.com/',
    'https://www.healx.com/',
    'https://www.huma.com/',
    'https://www.benevolent.com/',
    'https://www.ultromics.com/',
    'https://www.speechmatics.com/',
    'https://www.kheiron.com/',
    'https://www.mindmazegroup.com/',
    
    # French companies
    'https://www.cardiologs.com/',
    'https://www.owkin.com/',
    'https://www.medadom.com/',
    'https://www.wandercraft.eu/',
    'https://www.qynapse.com/',
    'https://www.therapixel.com/',
    'https://www.gleamer.ai/',
    'https://www.voluntis.com/',
    'https://www.medelinked.com/',
    'https://www.mapatho.com/',
    
    # Netherlands companies
    'https://www.luscii.com/',
    'https://www.aidence.com/',
    'https://www.thirona.eu/',
    'https://www.veracyte.com/',
    'https://www.orfeus-ai.com/',
    'https://www.contextflow.com/',
    'https://www.skin-vision.com/',
    'https://www.pacmed.ai/',
    'https://www.philips.com/healthcare',
    'https://www.nedap-healthcare.com/',
    
    # Swedish companies
    'https://www.kry.se/',
    'https://www.min-doktor.se/',
    'https://www.doctrin.se/',
    'https://www.carechain.io/',
    'https://www.getinge.com/',
    'https://www.elekta.com/',
    'https://www.sectra.com/',
    'https://www.cambio.se/',
    'https://www.heart2save.com/',
    'https://www.infomedica.se/',
    
    # Swiss companies
    'https://www.sophia-genetics.com/',
    'https://www.mindmaze.com/',
    'https://www.ava.ch/',
    'https://www.lunaphore.com/',
    'https://www.versantis.com/',
    'https://www.debiopharm.com/',
    'https://www.neuravi.com/',
    'https://www.abionic.com/',
    'https://www.cytosurge.com/',
    'https://www.eyekon-medical.com/',
    
    # Spanish companies
    'https://www.vitio.io/',
    'https://www.orikine.com/',
    'https://www.doctoralia.com/',
    'https://www.top-doctors.com/',
    'https://www.mediktor.com/',
    'https://www.almirall.com/',
    'https://www.ferrer.com/',
    'https://www.grifols.com/',
    'https://www.rovi.es/',
    'https://www.faes.es/',
    
    # Italian companies
    'https://www.miacare.org/',
    'https://www.pazienti.it/',
    'https://www.dottori.it/',
    'https://www.medicalexcellence.it/',
    'https://www.healthware.it/',
    'https://www.bracco.com/',
    'https://www.recordati.com/',
    'https://www.diasorin.com/',
    'https://www.kedrion.com/',
    'https://www.alfasigma.com/'
]

def validate_url(url):
    """
    Validate a URL and extract basic information
    """
    try:
        # Clean up the URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Create request with user agent
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        # Make request with timeout
        response = urllib.request.urlopen(req, timeout=10)
        
        # Read and decode content
        content = response.read()
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='ignore')
            except:
                content = str(content)
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "No title found"
        
        # Determine healthcare type based on content and URL
        healthcare_type = determine_healthcare_type(url, content, title)
        
        # Extract country from domain or content
        country = extract_country(url, content)
        
        return {
            'url': url,
            'domain': urlparse(url).netloc,
            'status': 'Active',
            'status_code': response.getcode(),
            'title': title,
            'healthcare_type': healthcare_type,
            'country': country,
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except urllib.error.HTTPError as e:
        return {
            'url': url,
            'domain': urlparse(url).netloc,
            'status': f'HTTP Error {e.code}',
            'status_code': e.code,
            'title': 'Error',
            'healthcare_type': 'Unknown',
            'country': 'Unknown',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'url': url,
            'domain': urlparse(url).netloc,
            'status': f'Error: {str(e)}',
            'status_code': 0,
            'title': 'Error',
            'healthcare_type': 'Unknown',
            'country': 'Unknown',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def determine_healthcare_type(url, content, title):
    """
    Determine the healthcare type based on URL, content, and title
    """
    text = f"{url} {content} {title}".lower()
    
    # AI/ML Healthcare
    if any(keyword in text for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural', 'algorithm']):
        return 'AI/ML Healthcare'
    
    # Telemedicine/Digital Health
    elif any(keyword in text for keyword in ['telemedicine', 'telehealth', 'digital health', 'remote', 'virtual consultation', 'online doctor']):
        return 'Digital Health'
    
    # Medical Devices
    elif any(keyword in text for keyword in ['medical device', 'diagnostic', 'monitoring', 'scanner', 'equipment', 'instrument']):
        return 'Medical Devices'
    
    # Biotechnology
    elif any(keyword in text for keyword in ['biotech', 'biotechnology', 'drug', 'pharmaceutical', 'therapy', 'clinical trial']):
        return 'Biotechnology'
    
    # Healthcare IT
    elif any(keyword in text for keyword in ['healthcare it', 'hospital software', 'ehr', 'emr', 'health information']):
        return 'Healthcare IT'
    
    # Default
    else:
        return 'Healthcare Services'

def extract_country(url, content):
    """
    Extract country information from URL or content
    """
    domain = urlparse(url).netloc.lower()
    
    # Country code mapping
    country_codes = {
        '.de': 'Germany',
        '.uk': 'United Kingdom',
        '.fr': 'France',
        '.nl': 'Netherlands',
        '.se': 'Sweden',
        '.ch': 'Switzerland',
        '.es': 'Spain',
        '.it': 'Italy',
        '.at': 'Austria',
        '.be': 'Belgium',
        '.dk': 'Denmark',
        '.fi': 'Finland',
        '.no': 'Norway',
        '.pl': 'Poland',
        '.cz': 'Czech Republic',
        '.ie': 'Ireland'
    }
    
    # Check domain extension
    for code, country in country_codes.items():
        if domain.endswith(code):
            return country
    
    # Check for country mentions in content
    content_lower = content.lower()
    countries = ['germany', 'united kingdom', 'france', 'netherlands', 'sweden', 'switzerland', 
                'spain', 'italy', 'austria', 'belgium', 'denmark', 'finland', 'norway',
                'poland', 'czech republic', 'ireland']
    
    for country in countries:
        if country in content_lower:
            return country.title()
    
    return 'Europe'

def save_to_csv(companies, filename):
    """
    Save companies data to CSV file
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'domain', 'country', 'status', 'status_code', 'title', 'healthcare_type', 'validated_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for company in companies:
            writer.writerow(company)

def save_to_json(companies, filename):
    """
    Save companies data to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(companies, jsonfile, indent=2, ensure_ascii=False)

def main():
    """
    Main function to validate all URLs and create database
    """
    print("🏥 European Healthcare Database Builder")
    print("=" * 50)
    
    # Combine all URLs
    all_urls = MANUAL_URLS + ADDITIONAL_URLS
    validated_companies = []
    
    print(f"📊 Processing {len(all_urls)} healthcare companies...")
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{len(all_urls)}] Validating: {url}")
        
        company_data = validate_url(url)
        validated_companies.append(company_data)
        
        # Print result
        status_emoji = "✅" if company_data['status'] == 'Active' else "❌"
        print(f"  {status_emoji} {company_data['status']} - {company_data['healthcare_type']} ({company_data['country']})")
        
        # Be respectful - small delay between requests
        time.sleep(1)
    
    # Generate filenames with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"european_healthcare_companies_{timestamp}.csv"
    json_filename = f"european_healthcare_companies_{timestamp}.json"
    
    # Save results
    save_to_csv(validated_companies, csv_filename)
    save_to_json(validated_companies, json_filename)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 VALIDATION SUMMARY")
    print("=" * 50)
    
    active_count = sum(1 for c in validated_companies if c['status'] == 'Active')
    error_count = len(validated_companies) - active_count
    
    print(f"✅ Active websites: {active_count}")
    print(f"❌ Errors/Inactive: {error_count}")
    print(f"📊 Success rate: {(active_count/len(validated_companies)*100):.1f}%")
    
    # Count by healthcare type
    healthcare_types = {}
    for company in validated_companies:
        if company['status'] == 'Active':
            htype = company['healthcare_type']
            healthcare_types[htype] = healthcare_types.get(htype, 0) + 1
    
    print(f"\n🏥 Healthcare Categories:")
    for htype, count in sorted(healthcare_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {htype}: {count} companies")
    
    # Count by country
    countries = {}
    for company in validated_companies:
        if company['status'] == 'Active':
            country = company['country']
            countries[country] = countries.get(country, 0) + 1
    
    print(f"\n🌍 Geographic Distribution:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {country}: {count} companies")
    
    print(f"\n💾 Files saved:")
    print(f"  • {csv_filename}")
    print(f"  • {json_filename}")
    
    print(f"\n🎉 European Healthcare Database completed successfully!")

if __name__ == "__main__":
    main()
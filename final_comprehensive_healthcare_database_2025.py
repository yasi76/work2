#!/usr/bin/env python3
"""
Final Comprehensive European Healthcare Startups & SMEs Database Builder
Combines all validated URLs with new discoveries from expanded web searches
Updated January 2025
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
from datetime import datetime
from urllib.parse import urlparse

# Final comprehensive list of European healthcare companies
FINAL_COMPREHENSIVE_HEALTHCARE_URLS = [
    # Previously validated German URLs
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
    'https://de.caona.eu/',
    'https://www.careanimations.de/',
    'https://sfs-healthcare.com',
    'https://www.climedo.de/',
    'https://www.cliniserve.de/',
    'https://cogthera.de/',
    'https://www.comuny.de/',
    'https://curecurve.de/',
    'https://www.cynteract.com/',
    'https://www.healthmeapp.de/',
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
    'https://fyzo.de/',
    'https://www.gesund.de/',
    'https://www.glaice.de/',
    'https://gleea.de/',
    'https://www.guidecare.de/',
    'https://www.apodienste.com/',
    'https://www.help-app.de/',
    'https://www.heynanny.com/',
    'https://incontalert.de/',
    'https://home.informme.info/',
    'https://www.kranushealth.com/',
    
    # New companies from 2025 searches - German
    'https://avelios.com',  # Munich healthcare IT startup, $31M Series A
    'https://dreryk.pl/',  # Polish medical software for clinics
    'https://medunit.pl/',  # Polish telemedicine platform
    'https://www.aurero.com/',  # Polish medical practice management
    'https://labplus.pl/',  # Polish medical test interpretation
    'https://labplus.ai/',  # International expansion of Labplus
    'https://www.halodoctor.pl/',  # Polish online medical consultations
    'https://aldebaran.care/',  # French digital medical assistant
    
    # French healthcare companies
    'https://www.libheros.fr/',  # French home healthcare platform
    'https://www.domain-therapeutics.com/',  # Strasbourg, €98.6M raised
    'https://mymojo.ai/',  # Lyon fertility tech, €6.5M raised
    'https://www.algama.com/',  # Paris microalgae foods, €5.9M
    'https://www.tissium.com/',  # Paris tissue reconstruction, €254.4M
    'https://www.lnc-therapeutics.com/',  # Bordeaux therapeutics, €7.7M
    'https://www.treefrog-therapeutics.com/',  # Cell therapy, €157.3M
    'https://www.biomodex.com/',  # 3D printing for surgery, €18.7M
    'https://www.therapixel.com/',  # Nice AI medical imaging, €43M
    'https://www.vivet-therapeutics.com/',  # Paris gene therapy, €767M
    'https://www.pep-therapy.com/',  # Paris peptide therapy, €3.1M
    'https://www.tilak-healthcare.com/',  # Paris mobile health games, €2.7M
    'https://www.biolog-id.com/',  # Healthcare traceability, €25M
    'https://www.micropep.com/',  # Biotech natural alternatives, €24.3M
    'https://www.afyren.com/',  # Biotech organic acids, €67.9M
    'https://www.brenus-pharma.com/',  # Lyon cancer vaccines, €29.5M
    'https://www.abolis.fr/',  # Évry microorganisms, €38.8M
    'https://www.m2i-lifesciences.com/',  # Saint-Cloud agtech, €92.5M
    'https://www.dynacure.com/',  # Illkirch antisense, €109.4M
    'https://www.abivax.com/',  # Paris viral diseases, €62.7M
    'https://www.carroucell.com/',  # Microcarriers, €3M
    'https://www.olgram.com/',  # Marine molecules, €3.6M
    'https://www.step-pharma.com/',  # Paris immunomodulators, €77M
    'https://www.advanced-biodesign.com/',  # Lyon R&D, €9.9M
    'https://www.phagos-biotech.com/',  # Paris biotech, €2.3M
    'https://www.samabriva.com/',  # Paris enzymes, €4.3M
    'https://www.keranova.fr/',  # Ophthalmology
    'https://www.alize-pharma.com/',  # Biopharmaceuticals, €4.1M
    'https://www.msinsight.fr/',  # Paris cancer diagnosis, €1.8M
    'https://bacta.life/',  # Paris biosynthetic rubber, €3.6M
    'https://www.inotrem.com/',  # Peptide therapy, €64.3M
    'https://www.vaxinano.com/',  # Nasal vaccines, €6.5M
    'https://generare.bio/',  # Paris drug discovery, €5.5M
    'https://theremia.health/',  # Paris AI drug development, €3.3M
    'https://www.ecoat.fr/',  # Grasse low-carbon coatings, €23M
    'https://biolevate.com/',  # Paris AI for pharma, €6.3M
    'https://www.superbranche.com/',  # Strasbourg nanoparticles, €13.5M
    'https://www.ynsect.com/',  # Insect biotech, €224M
    'https://www.neuroclues.com/',  # Eye-tracking for brain health, €5M
    
    # Swiss healthcare companies
    'https://aeon.life/',  # Swiss full-body MRI startup, €8.2M
    'https://www.hedia.com/',  # Denmark diabetes management (European expansion)
    'https://o2matic.com/',  # Denmark oxygen therapy automation
    'https://ampamedical.com/',  # Denmark ostomy care innovation
    'https://www.egoo.health/',  # Denmark biomarker self-testing
    'https://ward247.com/',  # Denmark patient monitoring 24/7
    'https://mavenhealth.ch/',  # Swiss metabolic health testing
    'https://www.samantree.com/',  # Swiss surgical imaging technology
    'https://www.healthcaters.ai/',  # German workplace health screenings
    'https://www.deepcare.ch/',  # Swiss precision health at home
    
    # UK and Nordic healthcare companies
    'https://www.numan.com/',  # UK digital health platform, $60M
    'https://www.biorce.com/',  # Barcelona drug development AI, €5M
    
    # Additional German companies from searches
    'https://www.intermedcare.com/',  # Munich medical devices
    'https://vital-age.de/',  # German medical equipment
    'https://carebetter.de/',  # Bad Oeynhausen medical devices
    'https://yamedicare.de/',  # Winsen medical equipment
    'https://www.medcare-solutions.de/',  # Baden-Württemberg medical equipment
    
    # Polish healthcare tech companies
    'https://dreryk.pl/',  # Medical software for clinics
    'https://medunit.pl/',  # Telemedicine and e-prescriptions
    'https://www.aurero.com/',  # Medical practice management software
    'https://labplus.pl/',  # Medical test interpretation platform
    'https://www.halodoctor.pl/',  # Online medical consultations
    
    # Additional Nordic companies discovered
    'https://www.hedia.com/',  # Danish diabetes digital therapeutics
    'https://o2matic.com/',  # Danish automatic oxygen therapy
    'https://ampamedical.com/',  # Danish ostomy care innovation
    'https://www.egoo.health/',  # Danish biomarker testing
    'https://ward247.com/',  # Danish patient deterioration monitoring
]

def clean_url(url):
    """Clean and standardize URL format"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def get_domain_from_url(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
    except:
        return 'unknown'

def get_country_from_domain(domain):
    """Determine country based on domain and content"""
    if '.de' in domain or 'german' in domain.lower():
        return 'Germany'
    elif '.fr' in domain or 'french' in domain.lower():
        return 'France'
    elif '.pl' in domain or 'polish' in domain.lower():
        return 'Poland'
    elif '.ch' in domain:
        return 'Switzerland'
    elif '.dk' in domain:
        return 'Denmark'
    elif '.co.uk' in domain or '.uk' in domain:
        return 'United Kingdom'
    elif '.nl' in domain:
        return 'Netherlands'
    elif '.se' in domain:
        return 'Sweden'
    elif '.no' in domain:
        return 'Norway'
    elif '.fi' in domain:
        return 'Finland'
    elif '.it' in domain:
        return 'Italy'
    elif '.es' in domain:
        return 'Spain'
    elif '.at' in domain:
        return 'Austria'
    elif '.be' in domain:
        return 'Belgium'
    else:
        return 'Unknown'

def determine_healthcare_type(url, title, domain):
    """Determine the type of healthcare company"""
    url_lower = url.lower()
    title_lower = title.lower() if title else ''
    domain_lower = domain.lower()
    
    # AI/ML patterns
    if any(keyword in url_lower + title_lower + domain_lower for keyword in 
           ['ai', 'artificial', 'machine-learning', 'ml', 'algorithm', 'deepeye', 'biotx']):
        return 'AI/ML Healthcare'
    
    # Digital health patterns
    elif any(keyword in url_lower + title_lower + domain_lower for keyword in 
             ['digital', 'app', 'platform', 'online', 'telemedicine', 'telehealth']):
        return 'Digital Health'
    
    # Biotech patterns
    elif any(keyword in url_lower + title_lower + domain_lower for keyword in 
             ['biotech', 'pharma', 'drug', 'therapeutic', 'clinical']):
        return 'Biotechnology'
    
    # Medical devices
    elif any(keyword in url_lower + title_lower + domain_lower for keyword in 
             ['device', 'equipment', 'scanner', 'diagnostic', 'medical-device']):
        return 'Medical Devices'
    
    # Preventive health
    elif any(keyword in url_lower + title_lower + domain_lower for keyword in 
             ['prevention', 'screening', 'check-up', 'early-detection']):
        return 'Preventive Health'
    
    else:
        return 'Healthcare Services'

def validate_url(url):
    """Validate URL and extract basic information"""
    try:
        clean_url_val = clean_url(url)
        
        # Create request with headers to mimic a real browser
        req = urllib.request.Request(
            clean_url_val,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Set timeout
        response = urllib.request.urlopen(req, timeout=10)
        status_code = response.getcode()
        
        # Try to get title
        content = response.read().decode('utf-8', errors='ignore')
        title = 'No title found'
        if '<title>' in content and '</title>' in content:
            title_start = content.find('<title>') + 7
            title_end = content.find('</title>')
            title = content[title_start:title_end].strip()
            if len(title) > 100:
                title = title[:100] + '...'
        
        domain = get_domain_from_url(clean_url_val)
        country = get_country_from_domain(domain)
        healthcare_type = determine_healthcare_type(clean_url_val, title, domain)
        
        return {
            'url': clean_url_val,
            'domain': domain,
            'country': country,
            'status': 'Active',
            'status_code': status_code,
            'title': title,
            'healthcare_type': healthcare_type,
            'source': 'Final Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except urllib.error.HTTPError as e:
        domain = get_domain_from_url(clean_url(url))
        country = get_country_from_domain(domain)
        return {
            'url': clean_url(url),
            'domain': domain,
            'country': country,
            'status': 'HTTP Error',
            'status_code': e.code,
            'title': f'HTTP Error {e.code}',
            'healthcare_type': 'Unknown',
            'source': 'Final Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        domain = get_domain_from_url(clean_url(url))
        country = get_country_from_domain(domain)
        return {
            'url': clean_url(url),
            'domain': domain,
            'country': country,
            'status': 'Error',
            'status_code': 'N/A',
            'title': f'Error: {str(e)[:50]}',
            'healthcare_type': 'Unknown',
            'source': 'Final Comprehensive Search',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """Main function to validate URLs and create final comprehensive database"""
    print("🏥 Final Comprehensive European Healthcare Database Builder")
    print("=" * 60)
    print(f"Total URLs to validate: {len(FINAL_COMPREHENSIVE_HEALTHCARE_URLS)}")
    print("=" * 60)
    
    results = []
    
    for i, url in enumerate(FINAL_COMPREHENSIVE_HEALTHCARE_URLS, 1):
        print(f"[{i}/{len(FINAL_COMPREHENSIVE_HEALTHCARE_URLS)}] Validating: {url}")
        
        result = validate_url(url)
        results.append(result)
        
        # Print result
        status_icon = "✅" if result['status'] == 'Active' else "❌"
        print(f"  {status_icon} {result['status']} ({result['status_code']}) - {result['country']} - {result['healthcare_type']}")
        
        # Small delay to be respectful
        time.sleep(1)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to CSV
    csv_filename = f'final_european_healthcare_companies_{timestamp}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['URL', 'Domain', 'Country', 'Status', 'Status_Code', 'Title', 'Healthcare_Type', 'Source', 'Validated_Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'URL': result['url'],
                'Domain': result['domain'],
                'Country': result['country'],
                'Status': result['status'],
                'Status_Code': result['status_code'],
                'Title': result['title'],
                'Healthcare_Type': result['healthcare_type'],
                'Source': result['source'],
                'Validated_Date': result['validated_date']
            })
    
    # Save to JSON
    json_filename = f'final_european_healthcare_companies_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, ensure_ascii=False)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 FINAL DATABASE SUMMARY")
    print("=" * 60)
    
    total_companies = len(results)
    active_companies = sum(1 for r in results if r['status'] == 'Active')
    
    print(f"Total companies processed: {total_companies}")
    print(f"Active companies: {active_companies}")
    print(f"Success rate: {(active_companies/total_companies)*100:.1f}%")
    
    # Country breakdown
    countries = {}
    for result in results:
        country = result['country']
        countries[country] = countries.get(country, 0) + 1
    
    print(f"\n🌍 Country Distribution:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {count} companies")
    
    # Healthcare type breakdown
    healthcare_types = {}
    for result in results:
        htype = result['healthcare_type']
        healthcare_types[htype] = healthcare_types.get(htype, 0) + 1
    
    print(f"\n🏥 Healthcare Type Distribution:")
    for htype, count in sorted(healthcare_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {htype}: {count} companies")
    
    print(f"\n💾 Files saved:")
    print(f"  📄 CSV: {csv_filename}")
    print(f"  📋 JSON: {json_filename}")
    
    print(f"\n✅ Final comprehensive database build complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
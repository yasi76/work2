#!/usr/bin/env python3
"""
🏥 Dynamic MEGA European Healthcare Database Builder
🚀 Uses URLs from Dynamic Research Discovery + Your Manual URLs
===============================================================
This script loads URLs from the dynamic research discovery process
and combines them with your manual URLs for comprehensive validation.
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
import ssl
import os
import glob
from datetime import datetime
from urllib.parse import urlparse, urljoin

# Your Original Manual URLs (always preserved)
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

def load_discovered_urls():
    """
    Load URLs from the dynamic research discovery script
    """
    print("🔍 Loading URLs from Dynamic Research Discovery...")
    
    discovered_urls = []
    
    # Look for the most recent URL files
    url_files = glob.glob("SIMPLE_URL_LIST_*.txt")
    json_files = glob.glob("DISCOVERED_URLS_FOR_MEGA_*.json")
    
    if url_files:
        # Use the most recent simple URL list
        latest_url_file = max(url_files, key=os.path.getctime)
        print(f"📂 Found URL file: {latest_url_file}")
        
        try:
            with open(latest_url_file, 'r', encoding='utf-8') as f:
                discovered_urls = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(discovered_urls)} URLs from {latest_url_file}")
        except Exception as e:
            print(f"❌ Error loading {latest_url_file}: {e}")
    
    elif json_files:
        # Use the most recent JSON file if no simple file found
        latest_json_file = max(json_files, key=os.path.getctime)
        print(f"📂 Found JSON file: {latest_json_file}")
        
        try:
            with open(latest_json_file, 'r', encoding='utf-8') as f:
                url_data = json.load(f)
                discovered_urls = [item['url'] for item in url_data if 'url' in item]
            print(f"✅ Loaded {len(discovered_urls)} URLs from {latest_json_file}")
        except Exception as e:
            print(f"❌ Error loading {latest_json_file}: {e}")
    
    else:
        print("⚠️ No discovered URL files found.")
        print("💡 Run DYNAMIC_RESEARCH_DISCOVERY.py first to generate URLs.")
        discovered_urls = []
    
    return discovered_urls

def create_safe_request(url, timeout=15):
    """Create a safe HTTP request with error handling"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        response = urllib.request.urlopen(request, context=ssl_context, timeout=timeout)
        content = response.read()
        
        encoding = response.headers.get_content_charset() or 'utf-8'
        try:
            decoded_content = content.decode(encoding, errors='ignore')
        except:
            decoded_content = content.decode('utf-8', errors='ignore')
            
        return decoded_content, response.getcode()
    except Exception as e:
        return None, str(e)

def clean_and_deduplicate_urls(discovered_urls, manual_urls):
    """Clean and deduplicate all URLs"""
    print("\n🧹 Combining and Deduplicating URLs...")
    
    all_urls = set()
    
    # Add manual URLs
    for url in manual_urls:
        clean_url = url.strip().rstrip('/')
        if clean_url:
            all_urls.add(clean_url)
    
    # Add discovered URLs
    for url in discovered_urls:
        clean_url = url.strip().rstrip('/')
        if clean_url and is_company_url(clean_url):
            all_urls.add(clean_url)
    
    # Convert back to list and sort
    final_urls = sorted(list(all_urls))
    
    print(f"📊 Manual URLs: {len(manual_urls)}")
    print(f"📊 Discovered URLs: {len(discovered_urls)}")
    print(f"📊 Total unique URLs: {len(final_urls)}")
    print(f"📊 Dynamic discoveries: {len(final_urls) - len(manual_urls)}")
    
    return final_urls

def is_company_url(url):
    """Filter out non-company URLs"""
    url_lower = url.lower()
    
    # Exclude patterns
    exclude_patterns = [
        'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'instagram.com',
        'google.com', 'wikipedia.org', 'github.com', 'stackoverflow.com',
        'news', 'blog', 'forum', 'discussion', 'comment', 'article',
        'privacy', 'terms', 'legal', 'contact', 'about-us', 'imprint',
        '.pdf', '.doc', '.jpg', '.png', '.gif', '.mp4', '.mp3',
        'mailto:', 'tel:', 'javascript:', '#'
    ]
    
    for pattern in exclude_patterns:
        if pattern in url_lower:
            return False
    
    return True

def validate_url(url):
    """Validate URL and extract company information"""
    try:
        content, status_code = create_safe_request(url)
        
        if content and str(status_code).startswith('2'):
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = clean_text(title_match.group(1)) if title_match else "Unknown Company"
            
            # Extract description
            desc_patterns = [
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
                r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']',
                r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
            ]
            
            description = "No description available"
            for pattern in desc_patterns:
                desc_match = re.search(pattern, content, re.IGNORECASE)
                if desc_match:
                    description = clean_text(desc_match.group(1))
                    break
            
            # Determine healthcare type and country
            healthcare_type = determine_healthcare_type(url, content, title)
            country = extract_country(url)
            
            # Determine source
            source = "Manual" if url in MANUAL_URLS else "Discovered"
            
            return {
                'name': title,
                'website': url,
                'description': description,
                'country': country,
                'healthcare_type': healthcare_type,
                'status': 'Active',
                'status_code': status_code,
                'source': source,
                'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return create_error_record(url, f"HTTP {status_code}")
            
    except Exception as e:
        return create_error_record(url, f"Network error")

def create_error_record(url, error_msg):
    """Create error record for failed validations"""
    healthcare_type = determine_healthcare_type(url, "", "")
    country = extract_country(url)
    source = "Manual" if url in MANUAL_URLS else "Discovered"
    
    return {
        'name': 'Error - Could not access',
        'website': url,
        'description': f'Error: {error_msg}',
        'country': country,
        'healthcare_type': healthcare_type,
        'status': 'Error',
        'status_code': error_msg,
        'source': source,
        'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def clean_text(text):
    """Clean HTML and CSS from text"""
    if not text:
        return "No information available"
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove CSS
    text = re.sub(r'\{[^}]*\}', '', text)
    
    # Remove JavaScript
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
        '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™'
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text[:500] if len(text) > 500 else text

def determine_healthcare_type(url, content, title):
    """Determine healthcare category based on URL and content"""
    combined_text = f"{url} {content} {title}".lower()
    
    # AI/ML Healthcare
    ai_keywords = ['artificial intelligence', 'machine learning', 'ai', 'ml', 'algorithm', 'neural', 'deep learning', 'computer vision', 'nlp', 'analytics', 'data science']
    if any(keyword in combined_text for keyword in ai_keywords):
        return "AI/ML Healthcare"
    
    # Digital Health
    digital_keywords = ['telemedicine', 'telehealth', 'remote monitoring', 'mobile health', 'app', 'digital', 'online consultation', 'virtual care']
    if any(keyword in combined_text for keyword in digital_keywords):
        return "Digital Health"
    
    # Biotechnology
    biotech_keywords = ['biotech', 'biotechnology', 'pharmaceutical', 'drug development', 'clinical trials', 'biopharma', 'genetics', 'genomics']
    if any(keyword in combined_text for keyword in biotech_keywords):
        return "Biotechnology"
    
    # Medical Devices
    device_keywords = ['medical device', 'medtech', 'diagnostic equipment', 'surgical', 'imaging', 'monitoring device', 'wearable']
    if any(keyword in combined_text for keyword in device_keywords):
        return "Medical Devices"
    
    # Mental Health
    mental_keywords = ['mental health', 'psychology', 'psychiatry', 'therapy', 'counseling', 'meditation', 'mindfulness', 'depression', 'anxiety']
    if any(keyword in combined_text for keyword in mental_keywords):
        return "Mental Health"
    
    # Default
    return "Healthcare Services"

def extract_country(url):
    """Extract country from URL domain"""
    domain = urlparse(url).netloc.lower()
    
    country_map = {
        '.de': 'Germany', '.uk': 'United Kingdom', '.co.uk': 'United Kingdom',
        '.fr': 'France', '.es': 'Spain', '.it': 'Italy', '.nl': 'Netherlands',
        '.se': 'Sweden', '.dk': 'Denmark', '.no': 'Norway', '.fi': 'Finland',
        '.ch': 'Switzerland', '.at': 'Austria', '.be': 'Belgium', '.pt': 'Portugal',
        '.ie': 'Ireland', '.gr': 'Greece', '.pl': 'Poland', '.cz': 'Czech Republic',
        '.hu': 'Hungary', '.sk': 'Slovakia', '.si': 'Slovenia', '.hr': 'Croatia',
        '.bg': 'Bulgaria', '.ro': 'Romania', '.lt': 'Lithuania', '.lv': 'Latvia',
        '.ee': 'Estonia', '.lu': 'Luxembourg', '.mt': 'Malta', '.cy': 'Cyprus'
    }
    
    for tld, country in country_map.items():
        if domain.endswith(tld):
            return country
    
    return "Europe"

def save_to_files(companies, base_filename):
    """Save companies data to CSV and JSON files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{base_filename}_{timestamp}.csv"
    json_filename = f"{base_filename}_{timestamp}.json"
    
    # Save to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'website', 'description', 'country', 'healthcare_type', 'status', 'status_code', 'source', 'validated_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for company in companies:
            writer.writerow(company)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(companies, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def main():
    """Main execution function"""
    print("🏥 Dynamic MEGA European Healthcare Database Builder")
    print("🚀 Using Dynamic Research Discovery + Your Manual URLs")
    print("======================================================================")
    
    # Load discovered URLs from research script
    discovered_urls = load_discovered_urls()
    
    if not discovered_urls:
        print("⚠️ No discovered URLs found. Using only manual URLs.")
        print("💡 Run 'python3 DYNAMIC_RESEARCH_DISCOVERY.py' first for best results.")
    
    # Combine and clean URLs
    all_urls = clean_and_deduplicate_urls(discovered_urls, MANUAL_URLS)
    
    if not all_urls:
        print("❌ No URLs to process. Exiting.")
        return
    
    # Validation phase
    print(f"\n🔍 Starting Validation Phase...")
    print(f"📊 Total URLs to validate: {len(all_urls)}")
    print("======================================================================")
    
    companies = []
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{len(all_urls)}] Validating: {url}")
        
        company_data = validate_url(url)
        companies.append(company_data)
        
        # Show progress
        status_icon = "✅" if company_data['status'] == 'Active' else "❌"
        type_icon = "🔍" if 'AI/ML' in company_data['healthcare_type'] else "📝"
        source_icon = "📋" if company_data['source'] == 'Manual' else "🔍"
        print(f"  {status_icon}{type_icon}{source_icon} {company_data['status']} - {company_data['healthcare_type']} ({company_data['country']})")
        
        # Respectful delay
        time.sleep(1)
    
    # Save results
    csv_file, json_file = save_to_files(companies, "DYNAMIC_MEGA_EUROPEAN_HEALTHCARE_DATABASE")
    
    # Generate comprehensive report
    active_companies = [c for c in companies if c['status'] == 'Active']
    manual_companies = [c for c in companies if c['source'] == 'Manual']
    discovered_companies = [c for c in companies if c['source'] == 'Discovered']
    
    # Count by healthcare type
    type_counts = {}
    for company in active_companies:
        type_name = company['healthcare_type']
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # Count by country
    country_counts = {}
    for company in active_companies:
        country_name = company['country']
        country_counts[country_name] = country_counts.get(country_name, 0) + 1
    
    # Final report
    print("\n======================================================================")
    print("📈 DYNAMIC MEGA FINAL REPORT")
    print("======================================================================")
    print("📊 OVERVIEW:")
    print(f"  • Total companies processed: {len(companies)}")
    print(f"  • Active websites: {len(active_companies)}")
    print(f"  • Manual URLs: {len(manual_companies)}")
    print(f"  • Dynamically discovered: {len(discovered_companies)}")
    print(f"  • Success rate: {(len(active_companies)/len(companies)*100):.1f}%")
    
    print(f"\n🏥 HEALTHCARE CATEGORIES:")
    for healthcare_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {healthcare_type}: {count} companies")
    
    print(f"\n🌍 COUNTRIES:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:  # Top 10
        print(f"  • {country}: {count} companies")
    
    print(f"\n📈 SOURCES:")
    print(f"  • Manual (your original): {len(manual_companies)} companies")
    print(f"  • Dynamic discovery: {len(discovered_companies)} companies")
    
    print(f"\n💾 FILES SAVED:")
    print(f"  • {csv_file}")
    print(f"  • {json_file}")
    
    print(f"\n🎉 Dynamic MEGA Enhanced Database completed!")
    print(f"📊 {len(companies)} companies total with dynamic research integration!")
    print(f"💡 This combines your manual URLs with dynamically discovered companies!")

if __name__ == "__main__":
    main()
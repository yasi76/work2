#!/usr/bin/env python3
"""
🏥 Dynamic MEGA Healthcare URL Validator & Accuracy Assessor
🚀 Validates URLs from Dynamic Research Discovery + Your Manual URLs
====================================================================
This script focuses on URL validation and accuracy assessment.
It combines URLs from the dynamic research discovery process
with your manual URLs to find the most accurate and accessible URLs.
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
    """Validate URL accessibility and extract basic information for accuracy assessment"""
    try:
        content, status_code = create_safe_request(url)
        
        if content and str(status_code).startswith('2'):
            # Extract title for validation purposes
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            raw_title = title_match.group(1) if title_match else ""
            
            # Extract description for validation
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
            
            # Determine healthcare type and country for categorization
            healthcare_type = determine_healthcare_type(url, content, raw_title)
            country = extract_country(url)
            
            # Determine source
            source = "Manual" if url in MANUAL_URLS else "Discovered"
            
            return {
                'website': url,
                'description': description,
                'country': country,
                'healthcare_type': healthcare_type,
                'status': 'Active',
                'status_code': status_code,
                'source': source,
                'raw_title': clean_text(raw_title)[:100] if raw_title else "",
                'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content_length': len(content),
                'has_healthcare_keywords': is_healthcare_related(content)
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
        'website': url,
        'description': f'Error: {error_msg}',
        'country': country,
        'healthcare_type': healthcare_type,
        'status': 'Error',
        'status_code': error_msg,
        'source': source,
        'raw_title': '',
        'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'content_length': 0,
        'has_healthcare_keywords': False
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

def is_healthcare_related(content):
    """Check if content contains healthcare-related keywords"""
    if not content:
        return False
    
    content_lower = content.lower()
    healthcare_keywords = [
        'health', 'medical', 'pharma', 'biotech', 'medicine', 'therapy',
        'diagnostic', 'treatment', 'patient', 'clinical', 'hospital',
        'drug', 'healthcare', 'telemedicine', 'digital health'
    ]
    
    return any(keyword in content_lower for keyword in healthcare_keywords)

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
        fieldnames = ['website', 'description', 'country', 'healthcare_type', 'status', 'status_code', 'source', 'raw_title', 'validated_date', 'content_length', 'has_healthcare_keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for company in companies:
            writer.writerow(company)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(companies, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def main():
    """Main execution function - focuses on URL validation and accuracy assessment"""
    print("🏥 Dynamic MEGA Healthcare URL Validator & Accuracy Assessor")
    print("🚀 Validating URLs from Dynamic Research Discovery + Your Manual URLs")
    print("======================================================================")
    print("💡 This script validates URLs and assesses their accuracy - no name extraction")
    print("🎯 Use company_name_extractor.py for extracting company names from validated URLs")
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
        
        url_data = validate_url(url)
        companies.append(url_data)
        
        # Show progress
        status_icon = "✅" if url_data['status'] == 'Active' else "❌"
        type_icon = "🔍" if 'AI/ML' in url_data['healthcare_type'] else "📝"
        source_icon = "📋" if url_data['source'] == 'Manual' else "🔍"
        healthcare_icon = "🏥" if url_data.get('has_healthcare_keywords') else "❓"
        
        # Show URL and basic info
        url_info = f"{url} ({url_data.get('content_length', 0)} bytes)"
        
        print(f"  {status_icon}{type_icon}{source_icon}{healthcare_icon} {url_info}")
        print(f"      Status: {url_data['status']} | Type: {url_data['healthcare_type']} | Country: {url_data['country']}")
        if url_data.get('description') and url_data['description'] != 'No description available':
            print(f"      Description: {url_data['description'][:100]}...")
        
        # Respectful delay
        time.sleep(1)
    
    # Save results
    csv_file, json_file = save_to_files(companies, "DYNAMIC_MEGA_URL_VALIDATION_REPORT")
    
    # Generate comprehensive report
    active_urls = [c for c in companies if c['status'] == 'Active']
    manual_urls = [c for c in companies if c['source'] == 'Manual']
    discovered_urls = [c for c in companies if c['source'] == 'Discovered']
    healthcare_confirmed = [c for c in companies if c.get('has_healthcare_keywords', False)]
    
    # Count by healthcare type
    type_counts = {}
    for url_data in active_urls:
        type_name = url_data['healthcare_type']
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # Count by country
    country_counts = {}
    for url_data in active_urls:
        country_name = url_data['country']
        country_counts[country_name] = country_counts.get(country_name, 0) + 1
    
    # Final report
    print("\n======================================================================")
    print("📈 DYNAMIC MEGA URL VALIDATION REPORT")
    print("======================================================================")
    print("📊 VALIDATION OVERVIEW:")
    print(f"  • Total URLs processed: {len(companies)}")
    print(f"  • Active/accessible URLs: {len(active_urls)}")
    print(f"  • Manual URLs: {len(manual_urls)}")
    print(f"  • Dynamically discovered: {len(discovered_urls)}")
    print(f"  • Healthcare content confirmed: {len(healthcare_confirmed)}")
    print(f"  • Success rate: {(len(active_urls)/len(companies)*100):.1f}%")
    print(f"  • Healthcare accuracy: {(len(healthcare_confirmed)/len(active_urls)*100 if active_urls else 0):.1f}%")
    
    print(f"\n🏥 HEALTHCARE CATEGORIES (Active URLs):")
    for healthcare_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {healthcare_type}: {count} URLs")
    
    print(f"\n🌍 COUNTRIES (Active URLs):")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:  # Top 10
        print(f"  • {country}: {count} URLs")
    
    print(f"\n📈 URL SOURCES:")
    print(f"  • Manual (your original): {len(manual_urls)} URLs")
    print(f"  • Dynamic discovery: {len(discovered_urls)} URLs")
    
    print(f"\n💾 FILES SAVED:")
    print(f"  • {csv_file}")
    print(f"  • {json_file}")
    
    print(f"\n🎉 URL Validation and Accuracy Assessment completed!")
    print(f"📊 {len(active_urls)} validated URLs from {len(companies)} total!")
    print(f"💡 Use these validated URLs with company_name_extractor.py for name extraction!")
    print(f"🔗 Most accurate URLs saved for further processing!")

if __name__ == "__main__":
    main()
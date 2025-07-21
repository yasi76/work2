#!/usr/bin/env python3
"""
🏥 Dynamic MEGA European Healthcare Database Builder
🚀 Validates URLs and extracts company names from websites
===============================================================
This script validates URLs and extracts company names using:
1. Homepage content analysis
2. Impressum page (legal disclosure)
3. Website title and metadata
4. About/Contact sections
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
    """Load URLs from the dynamic research discovery script"""
    print("🔍 Loading URLs from Dynamic Research Discovery...")
    
    discovered_urls = []
    
    # Look for the most recent URL files
    url_files = glob.glob("SIMPLE_URL_LIST_*.txt")
    json_files = glob.glob("DISCOVERED_URLS_FOR_MEGA_*.json")
    
    if url_files:
        latest_url_file = max(url_files, key=os.path.getctime)
        print(f"📂 Found URL file: {latest_url_file}")
        
        try:
            with open(latest_url_file, 'r', encoding='utf-8') as f:
                discovered_urls = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(discovered_urls)} URLs from {latest_url_file}")
        except Exception as e:
            print(f"❌ Error loading {latest_url_file}: {e}")
    
    elif json_files:
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
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
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

def clean_text(text):
    """Clean HTML and normalize text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
        '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™', '&auml;': 'ä',
        '&ouml;': 'ö', '&uuml;': 'ü', '&Auml;': 'Ä', '&Ouml;': 'Ö', '&Uuml;': 'Ü',
        '&szlig;': 'ß'
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text

def try_impressum_page(base_url):
    """Try to access the Impressum page for company information"""
    impressum_paths = [
        '/impressum',
        '/impressum.html',
        '/legal',
        '/legal.html',
        '/imprint',
        '/imprint.html',
        '/datenschutz',
        '/kontakt',
        '/contact'
    ]
    
    for path in impressum_paths:
        try:
            impressum_url = urljoin(base_url, path)
            content, status = create_safe_request(impressum_url)
            
            if content and str(status).startswith('2'):
                # Extract company name from Impressum
                company_name = extract_company_from_impressum(content)
                if company_name:
                    return company_name, 'Impressum page'
        except:
            continue
    
    return None, None

def extract_company_from_impressum(content):
    """Extract company name from Impressum/legal page"""
    # German Impressum patterns
    patterns = [
        # "Firma: Company Name" or "Unternehmen: Company Name"
        r'(?:Firma|Unternehmen|Betreiber|Anbieter):\s*([^<\n]+?)(?:\s*(?:GmbH|AG|UG|e\.K\.|KG))?',
        
        # "Company Name GmbH" at start of line
        r'^([A-ZÄÖÜ][^<\n]*?(?:GmbH|AG|UG|e\.K\.|KG))',
        
        # "Geschäftsführer: Name" followed by company
        r'(?:Geschäftsführer|CEO|Managing Director)[^<\n]*?\n([A-ZÄÖÜ][^<\n]*?(?:GmbH|AG|UG|e\.K\.|KG))',
        
        # Address format: Company name before address
        r'([A-ZÄÖÜ][^<\n]*?(?:GmbH|AG|UG|e\.K\.|KG))[^<\n]*?\n[^<\n]*?(?:\d{5}|\d{4})\s+[A-ZÄÖÜ][a-zäöüß]+',
        
        # General company pattern
        r'([A-ZÄÖÜ][A-Za-zäöüß\s&\-\.]{2,40}(?:GmbH|AG|UG|e\.K\.|KG))',
    ]
    
    content_clean = clean_text(content)
    
    for pattern in patterns:
        matches = re.findall(pattern, content_clean, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            
            company_name = clean_company_name(match)
            if company_name and len(company_name) > 3 and is_valid_company_name(company_name):
                return company_name
    
    return None

def extract_company_from_title(title):
    """Extract company name from page title"""
    if not title:
        return None
    
    title = clean_text(title)
    
    # Title patterns to extract company name
    patterns = [
        # "Company Name | Tagline"
        r'^([^|]+?)\s*\|',
        # "Company Name - Tagline"
        r'^([^-–—]+?)\s*[-–—]',
        # "Company Name: Tagline"
        r'^([^:]+?)\s*:',
        # "Welcome to Company Name"
        r'(?:Welcome to|Willkommen bei)\s+([^|–—\-:]+)',
        # Just the first part
        r'^([A-ZÄÖÜ][^|–—\-:()]{3,40})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            company_name = clean_company_name(match.group(1))
            if company_name and is_valid_company_name(company_name):
                return company_name
    
    return None

def extract_company_from_meta(content):
    """Extract company name from meta tags"""
    meta_patterns = [
        # og:site_name
        r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']',
        # application-name
        r'<meta[^>]*name=["\']application-name["\'][^>]*content=["\']([^"\']+)["\']',
        # author
        r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
        # company
        r'<meta[^>]*name=["\']company["\'][^>]*content=["\']([^"\']+)["\']',
        # twitter:site
        r'<meta[^>]*name=["\']twitter:site["\'][^>]*content=["\']@?([^"\']+)["\']',
        # description with company name
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*(?:GmbH|AG|UG)[^"\']*)["\']',
    ]
    
    for pattern in meta_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            company_name = clean_company_name(match.group(1))
            if company_name and is_valid_company_name(company_name):
                return company_name
    
    return None

def extract_company_from_content(content):
    """Extract company name from main content"""
    content_clean = clean_text(content)
    
    # Look for company patterns in headers and main content
    patterns = [
        # About Us sections
        r'(?:Über uns|About us|About|Unternehmen)[^<]*?([A-ZÄÖÜ][^<\n]{5,50}(?:GmbH|AG|UG|e\.K\.|KG))',
        
        # Header/footer company names
        r'<(?:h1|h2|h3)[^>]*>([^<]*?(?:GmbH|AG|UG|e\.K\.|KG)[^<]*?)</(?:h1|h2|h3)>',
        
        # Copyright notices
        r'©[^<\n]*?([A-ZÄÖÜ][^<\n]{3,40}(?:GmbH|AG|UG|e\.K\.|KG))',
        
        # Contact information
        r'(?:Kontakt|Contact)[^<]*?([A-ZÄÖÜ][^<\n]{5,50}(?:GmbH|AG|UG|e\.K\.|KG))',
        
        # First prominent company name
        r'\b([A-ZÄÖÜ][A-Za-zäöüß\s&\-\.]{2,30}(?:GmbH|AG|UG|e\.K\.|KG))\b',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches[:3]:  # Only check first 3 matches
            company_name = clean_company_name(match)
            if company_name and is_valid_company_name(company_name):
                return company_name
    
    return None

def clean_company_name(name):
    """Clean and normalize company name"""
    if not name:
        return None
    
    name = clean_text(name)
    
    # Remove common prefixes/suffixes
    name = re.sub(r'^(?:Welcome to|Willkommen bei|Die|Der|Das)\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*[-–—|:]\s*(?:Home|Official|Website|Site|Startseite).*$', '', name, flags=re.IGNORECASE)
    
    # Clean up punctuation
    name = re.sub(r'[<>(){}[\]]', '', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    # Ensure it starts with capital letter
    if name and len(name) > 1:
        name = name[0].upper() + name[1:]
    
    return name if len(name) > 2 else None

def is_valid_company_name(name):
    """Check if the extracted name is likely a valid company name"""
    if not name or len(name) < 3:
        return False
    
    # Exclude generic terms
    generic_terms = [
        'Home', 'About', 'Contact', 'Welcome', 'Privacy', 'Terms', 'Cookie',
        'Login', 'Register', 'Search', 'Menu', 'Navigation', 'Footer', 'Header',
        'Startseite', 'Kontakt', 'Impressum', 'Datenschutz', 'AGB'
    ]
    
    name_lower = name.lower()
    if any(term.lower() in name_lower for term in generic_terms):
        return False
    
    # Must contain at least one letter
    if not re.search(r'[A-Za-zäöüÄÖÜß]', name):
        return False
    
    return True

def extract_company_name(url, content, title):
    """Extract company name using multiple methods with priority order"""
    extraction_methods = []
    
    # Method 1: Try Impressum page (highest priority for German sites)
    impressum_name, impressum_method = try_impressum_page(url)
    if impressum_name:
        return impressum_name, impressum_method
    
    # Method 2: Meta tags
    meta_name = extract_company_from_meta(content)
    if meta_name:
        return meta_name, 'Meta tags'
    
    # Method 3: Page title
    title_name = extract_company_from_title(title)
    if title_name:
        return title_name, 'Page title'
    
    # Method 4: Content analysis
    content_name = extract_company_from_content(content)
    if content_name:
        return content_name, 'Content analysis'
    
    # Method 5: Fallback to domain
    domain_name = extract_company_from_domain(url)
    if domain_name:
        return domain_name, 'Domain name'
    
    return 'Unknown Company', 'No extraction method successful'

def extract_company_from_domain(url):
    """Extract company name from domain as fallback"""
    try:
        domain = urlparse(url).netloc.lower()
        # Remove www, shop, app, etc.
        domain = re.sub(r'^(?:www\.|shop\.|app\.|api\.|blog\.)', '', domain)
        # Get main domain part
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            company_part = domain_parts[0]
            # Clean and capitalize
            company_part = re.sub(r'[^a-zA-Z0-9]', '', company_part)
            if len(company_part) > 2:
                return company_part.capitalize()
    except:
        pass
    return None

def extract_description(content):
    """Extract company description from meta tags"""
    desc_patterns = [
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']{20,300})["\']',
        r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']{20,300})["\']',
    ]
    
    for pattern in desc_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            description = clean_text(match.group(1))
            if len(description) > 20:
                return description[:300]
    
    return "No description available"

def determine_country(url):
    """Determine country from URL domain"""
    domain = urlparse(url).netloc.lower()
    
    country_map = {
        '.de': 'Germany', '.uk': 'United Kingdom', '.co.uk': 'United Kingdom',
        '.fr': 'France', '.es': 'Spain', '.it': 'Italy', '.nl': 'Netherlands',
        '.se': 'Sweden', '.dk': 'Denmark', '.no': 'Norway', '.fi': 'Finland',
        '.ch': 'Switzerland', '.at': 'Austria', '.be': 'Belgium', '.pt': 'Portugal',
        '.ie': 'Ireland', '.gr': 'Greece', '.pl': 'Poland', '.cz': 'Czech Republic'
    }
    
    for tld, country in country_map.items():
        if domain.endswith(tld):
            return country
    
    return 'Europe'

def combine_and_clean_urls(discovered_urls, manual_urls):
    """Combine and deduplicate all URLs"""
    print("\n🧹 Combining and Cleaning URLs...")
    
    all_urls = set()
    
    # Add manual URLs
    for url in manual_urls:
        clean_url = url.strip().rstrip('/')
        if clean_url:
            all_urls.add(clean_url)
    
    # Add discovered URLs
    for url in discovered_urls:
        clean_url = url.strip().rstrip('/')
        if clean_url:
            all_urls.add(clean_url)
    
    final_urls = sorted(list(all_urls))
    
    print(f"📊 Manual URLs: {len(manual_urls)}")
    print(f"📊 Discovered URLs: {len(discovered_urls)}")
    print(f"📊 Total unique URLs: {len(final_urls)}")
    
    return final_urls

def validate_url(url):
    """Validate URL and extract all company information"""
    try:
        content, status_code = create_safe_request(url)
        
        if content and str(status_code).startswith('2'):
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = clean_text(title_match.group(1)) if title_match else ""
            
            # Extract company name using comprehensive methods
            company_name, extraction_method = extract_company_name(url, content, title)
            
            # Extract description
            description = extract_description(content)
            
            # Determine source and country
            source = "Manual" if url in MANUAL_URLS else "Discovered"
            country = determine_country(url)
            
            return {
                'name': company_name,
                'website': url,
                'description': description,
                'country': country,
                'status': 'Active',
                'status_code': status_code,
                'source': source,
                'extraction_method': extraction_method,
                'title': title[:100] if title else "",
                'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return create_error_record(url, f"HTTP {status_code}")
            
    except Exception as e:
        return create_error_record(url, "Network error")

def create_error_record(url, error_msg):
    """Create error record for failed validations"""
    source = "Manual" if url in MANUAL_URLS else "Discovered"
    country = determine_country(url)
    domain_name = extract_company_from_domain(url)
    
    return {
        'name': domain_name or 'Error - Could not access',
        'website': url,
        'description': f'Error: {error_msg}',
        'country': country,
        'status': 'Error',
        'status_code': error_msg,
        'source': source,
        'extraction_method': 'Domain (error)',
        'title': '',
        'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def save_results(companies, filename_base="MEGA_HEALTHCARE_DATABASE"):
    """Save results to CSV and JSON files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{filename_base}_{timestamp}.csv"
    json_filename = f"{filename_base}_{timestamp}.json"
    
    # Save to CSV
    fieldnames = ['name', 'website', 'description', 'country', 'status', 'status_code', 'source', 'extraction_method', 'title', 'validated_date']
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
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
    print("🏥 DYNAMIC MEGA EUROPEAN HEALTHCARE DATABASE BUILDER")
    print("🚀 Advanced Company Name Extraction from Websites")
    print("=" * 70)
    
    # Load discovered URLs
    discovered_urls = load_discovered_urls()
    
    # Combine all URLs
    all_urls = combine_and_clean_urls(discovered_urls, MANUAL_URLS)
    
    if not all_urls:
        print("❌ No URLs to process. Exiting.")
        return
    
    print(f"\n🔍 Starting Validation Phase...")
    print(f"📊 Total URLs to validate: {len(all_urls)}")
    print("=" * 70)
    
    companies = []
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{len(all_urls)}] Validating: {url}")
        
        company_data = validate_url(url)
        companies.append(company_data)
        
        # Show progress
        status_icon = "✅" if company_data['status'] == 'Active' else "❌"
        source_icon = "📋" if company_data['source'] == 'Manual' else "🔍"
        
        print(f"  {status_icon}{source_icon} {company_data['name']}")
        print(f"      Method: {company_data['extraction_method']} | Status: {company_data['status']} | Country: {company_data['country']}")
        
        # Respectful delay
        time.sleep(1)
    
    # Save results
    csv_file, json_file = save_results(companies)
    
    # Generate report
    active_companies = [c for c in companies if c['status'] == 'Active']
    manual_companies = [c for c in companies if c['source'] == 'Manual']
    discovered_companies = [c for c in companies if c['source'] == 'Discovered']
    
    # Count by extraction method
    method_counts = {}
    for company in active_companies:
        method = company['extraction_method']
        method_counts[method] = method_counts.get(method, 0) + 1
    
    # Count by country
    country_counts = {}
    for company in active_companies:
        country = company['country']
        country_counts[country] = country_counts.get(country, 0) + 1
    
    print("\n" + "=" * 70)
    print("📈 FINAL REPORT")
    print("=" * 70)
    print("📊 OVERVIEW:")
    print(f"  • Total companies processed: {len(companies)}")
    print(f"  • Active websites: {len(active_companies)}")
    print(f"  • Manual URLs: {len(manual_companies)}")
    print(f"  • Discovered URLs: {len(discovered_companies)}")
    print(f"  • Success rate: {(len(active_companies)/len(companies)*100):.1f}%")
    
    print(f"\n🔍 EXTRACTION METHODS:")
    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {method}: {count} companies")
    
    print(f"\n🌍 COUNTRIES:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {country}: {count} companies")
    
    print(f"\n💾 FILES SAVED:")
    print(f"  • {csv_file}")
    print(f"  • {json_file}")
    
    print(f"\n🎉 Database completed with advanced company name extraction!")

if __name__ == "__main__":
    main()
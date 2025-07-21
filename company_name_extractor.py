#!/usr/bin/env python3
"""
🏢 Company Name Extractor for Healthcare URLs
💡 Lightweight script for extracting company names from clean valid URLs
===============================================================
This script focuses solely on company name extraction without the heavy
database operations of the mega script.
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
from urllib.parse import urlparse

def create_safe_request(url, timeout=10):
    """Create a lightweight HTTP request focused on getting just the title/meta info"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'close',  # Don't keep connections open
            }
        )
        
        response = urllib.request.urlopen(request, context=ssl_context, timeout=timeout)
        
        # Only read first 8KB - enough for head section with title/meta tags
        content = response.read(8192)  # Much smaller read than mega script
        
        encoding = response.headers.get_content_charset() or 'utf-8'
        try:
            decoded_content = content.decode(encoding, errors='ignore')
        except:
            decoded_content = content.decode('utf-8', errors='ignore')
            
        return decoded_content, response.getcode()
    except Exception as e:
        return None, str(e)

def extract_company_name_from_url(url):
    """Extract company name from URL domain - fast method"""
    try:
        domain = urlparse(url).netloc.lower()
        
        # Remove common prefixes
        domain = re.sub(r'^(www\.|shop\.|app\.|api\.|blog\.|news\.|portal\.)', '', domain)
        
        # Get the main domain part (before TLD)
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            company_part = domain_parts[0]
            
            # Clean up common patterns
            company_part = re.sub(r'(health|medical|pharma|biotech|med|care)$', '', company_part)
            company_part = company_part.strip('-_')
            
            # Capitalize properly
            if company_part and len(company_part) > 2:
                return company_part.capitalize()
    
    except:
        pass
    
    return None

def extract_company_name_from_title(title):
    """Extract company name from page title"""
    if not title:
        return None
    
    title = clean_text(title)
    
    # Common title patterns to extract company name
    patterns = [
        # "Company Name | Tagline" or "Company Name - Tagline"
        r'^([^||\-–—]+)[\s]*[||\-–—]',
        # "Company Name: Tagline"
        r'^([^:]+):',
        # "Welcome to Company Name" 
        r'welcome\s+to\s+([^||\-–—]+)',
        # "Company Name - Official Site"
        r'^([^||\-–—]+)\s*[\-–—]\s*(official|home|website)',
        # Just take first part before common separators
        r'^([^||\-–—\(\[]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            
            # Clean up the extracted name
            company_name = clean_company_name(company_name)
            if company_name and len(company_name) > 2 and not is_generic_text(company_name):
                return company_name
    
    return None

def extract_company_name_from_meta(content):
    """Extract company name from meta tags - lightweight extraction"""
    meta_patterns = [
        # og:site_name (best for company names)
        r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']',
        # application-name
        r'<meta[^>]*name=["\']application-name["\'][^>]*content=["\']([^"\']+)["\']',
        # twitter:site
        r'<meta[^>]*name=["\']twitter:site["\'][^>]*content=["\']@?([^"\']+)["\']',
    ]
    
    for pattern in meta_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            company_name = clean_text(match.group(1))
            company_name = clean_company_name(company_name)
            if company_name and len(company_name) > 2 and not is_generic_text(company_name):
                return company_name
    
    return None

def clean_company_name(name):
    """Clean and normalize company name"""
    if not name:
        return None
    
    name = clean_text(name)
    
    # Remove common suffixes/prefixes
    name = re.sub(r'\s*[-–—|:]\s*(home|official|website|site).*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^(welcome\s+to\s+)', '', name, flags=re.IGNORECASE)
    
    # Remove HTML artifacts
    name = re.sub(r'[<>]', '', name)
    
    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    # Remove single character words at the end
    name = re.sub(r'\s+[a-zA-Z]\s*$', '', name)
    
    return name if len(name) > 2 else None

def clean_text(text):
    """Clean HTML from text - lightweight version"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Decode basic HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
        '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™'
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text

def is_generic_text(text):
    """Check if text is too generic to be a company name"""
    generic_words = [
        'home', 'about', 'contact', 'welcome', 'page', 'site', 'website',
        'official', 'login', 'register', 'search', 'menu', 'navigation',
        'privacy', 'terms', 'conditions', 'policy', 'copyright', 'reserved',
        'error', '404', '403', 'not found', 'access denied'
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in generic_words)

def extract_company_name(url):
    """Main function to extract company name from URL - lightweight version"""
    try:
        # Method 1: Try to get from URL domain first (fastest)
        url_name = extract_company_name_from_url(url)
        
        # Method 2: Get page content (only head section)
        content, status_code = create_safe_request(url)
        
        if content and str(status_code).startswith('2'):
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            raw_title = title_match.group(1) if title_match else ""
            
            # Extract from title and meta
            title_name = extract_company_name_from_title(raw_title)
            meta_name = extract_company_name_from_meta(content)
            
            # Choose the best company name
            candidates = [
                (meta_name, 'Meta tags'),
                (title_name, 'Page title'),
                (url_name, 'URL domain')
            ]
            
            # Pick first valid candidate
            for name, method in candidates:
                if name and len(name) > 2:
                    return {
                        'url': url,
                        'company_name': name,
                        'extraction_method': method,
                        'status': 'Success',
                        'raw_title': clean_text(raw_title)[:100] if raw_title else "",
                        'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
        
        # Fallback to URL-based name
        if url_name:
            return {
                'url': url,
                'company_name': url_name,
                'extraction_method': 'URL domain (fallback)',
                'status': 'Partial',
                'raw_title': '',
                'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Complete failure
        return {
            'url': url,
            'company_name': 'Unknown',
            'extraction_method': 'Failed',
            'status': 'Error',
            'raw_title': '',
            'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'url': url,
            'company_name': 'Error',
            'extraction_method': 'Exception',
            'status': f'Error: {str(e)[:50]}',
            'raw_title': '',
            'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def load_urls_from_file(filename):
    """Load URLs from various file formats"""
    urls = []
    
    try:
        if filename.endswith('.txt'):
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        
        elif filename.endswith('.json'):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Simple list of URLs
                    if all(isinstance(item, str) for item in data):
                        urls = [url for url in data if url.startswith('http')]
                    # List of objects with 'url' field
                    else:
                        urls = [item.get('url', item.get('website', '')) for item in data if 'url' in item or 'website' in item]
                        urls = [url for url in urls if url and url.startswith('http')]
        
        elif filename.endswith('.csv'):
            with open(filename, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    url = row.get('url', row.get('website', ''))
                    if url and url.startswith('http'):
                        urls.append(url)
        
        print(f"✅ Loaded {len(urls)} URLs from {filename}")
        return urls
        
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return []

def load_urls_from_discovery_files():
    """Load URLs from dynamic research discovery files"""
    urls = []
    
    # Look for discovery files
    url_files = glob.glob("SIMPLE_URL_LIST_*.txt") + glob.glob("DISCOVERED_URLS_FOR_MEGA_*.json")
    
    if url_files:
        # Use the most recent file
        latest_file = max(url_files, key=os.path.getctime)
        print(f"🔍 Found discovery file: {latest_file}")
        urls = load_urls_from_file(latest_file)
    else:
        print("⚠️ No discovery files found. Looking for any URL files...")
        # Look for any URL files
        possible_files = glob.glob("*.txt") + glob.glob("*.json") + glob.glob("*.csv")
        for file in possible_files:
            if any(keyword in file.lower() for keyword in ['url', 'company', 'website']):
                print(f"📁 Trying file: {file}")
                file_urls = load_urls_from_file(file)
                if file_urls:
                    urls.extend(file_urls)
                    break
    
    return list(set(urls))  # Remove duplicates

def save_results(results, base_filename="company_names"):
    """Save extraction results to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{base_filename}_{timestamp}.csv"
    json_filename = f"{base_filename}_{timestamp}.json"
    
    # Save to CSV
    if results:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'company_name', 'extraction_method', 'status', 'raw_title', 'extracted_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def main():
    """Main execution function"""
    print("🏢 Company Name Extractor for Healthcare URLs")
    print("💡 Lightweight extraction focused on company names only")
    print("=" * 60)
    
    # Get URLs from various sources
    urls = []
    
    # Method 1: Load from discovery files
    discovery_urls = load_urls_from_discovery_files()
    if discovery_urls:
        urls.extend(discovery_urls)
        print(f"📊 Loaded {len(discovery_urls)} URLs from discovery files")
    
    # Method 2: Manual URLs from mega script (as backup)
    manual_urls = [
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
    
    if not urls:
        print("⚠️ No discovery URLs found, using manual URL list")
        urls = manual_urls
    else:
        # Add manual URLs that aren't already in discovery
        for url in manual_urls:
            if url not in urls:
                urls.append(url)
        print(f"➕ Added {len(manual_urls)} manual URLs")
    
    # Remove duplicates and clean
    urls = list(set([url.strip().rstrip('/') for url in urls if url.strip()]))
    
    print(f"🎯 Total URLs to process: {len(urls)}")
    print("=" * 60)
    
    # Extract company names
    results = []
    successful_extractions = 0
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Extracting: {url}")
        
        result = extract_company_name(url)
        results.append(result)
        
        # Show result
        status_icon = "✅" if result['status'] == 'Success' else "⚠️" if result['status'] == 'Partial' else "❌"
        print(f"  {status_icon} {result['company_name']} ({result['extraction_method']})")
        
        if result['status'] in ['Success', 'Partial']:
            successful_extractions += 1
        
        # Small delay to be respectful
        time.sleep(0.5)
    
    # Save results
    csv_file, json_file = save_results(results)
    
    # Summary
    success_rate = (successful_extractions / len(urls)) * 100 if urls else 0
    
    print("\n" + "=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"📈 Total URLs processed: {len(urls)}")
    print(f"✅ Successful extractions: {successful_extractions}")
    print(f"📊 Success rate: {success_rate:.1f}%")
    
    # Method breakdown
    method_counts = {}
    for result in results:
        if result['status'] in ['Success', 'Partial']:
            method = result['extraction_method']
            method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"\n🔍 EXTRACTION METHODS:")
    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {method}: {count} companies")
    
    print(f"\n💾 FILES SAVED:")
    print(f"  • CSV: {csv_file}")
    print(f"  • JSON: {json_file}")
    
    print(f"\n🎉 Company name extraction completed!")
    print(f"💡 This lightweight script extracted {successful_extractions} company names")
    print(f"🚀 Much faster than the heavy mega database script!")

if __name__ == "__main__":
    main()
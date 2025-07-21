#!/usr/bin/env python3
"""
🏢 Company Name Extractor
🎯 Accurately extracts company names from URLs using multiple methods
=======================================================================
Loads URLs from discovery results and extracts clean company names
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
import ssl
import glob
import os
from datetime import datetime

def create_safe_request(url, timeout=10):
    """Create a safe HTTP request with error handling"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
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
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
        '&nbsp;': ' ', '&copy;': '©', '&reg;': '®', '&trade;': '™',
        '&mdash;': '—', '&ndash;': '–', '&hellip;': '...'
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text

def extract_company_name_from_url(url):
    """Extract company name from URL domain"""
    try:
        domain = urllib.parse.urlparse(url).netloc.lower()
        
        # Remove www, subdomain prefixes
        domain = re.sub(r'^(www\.|shop\.|app\.|api\.|blog\.|news\.)', '', domain)
        
        # Get the main domain part (before TLD)
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            company_part = domain_parts[0]
            
            # Clean up common patterns
            company_part = re.sub(r'(health|medical|pharma|biotech|med|care)$', '', company_part)
            company_part = company_part.strip('-_')
            
            # Capitalize properly
            if company_part:
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
            if company_name and len(company_name) > 2:
                return company_name
    
    return None

def extract_company_name_from_meta(content):
    """Extract company name from meta tags"""
    meta_patterns = [
        # og:site_name
        r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']',
        # application-name
        r'<meta[^>]*name=["\']application-name["\'][^>]*content=["\']([^"\']+)["\']',
        # author (sometimes company name)
        r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
        # twitter:site
        r'<meta[^>]*name=["\']twitter:site["\'][^>]*content=["\']@?([^"\']+)["\']',
    ]
    
    for pattern in meta_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            company_name = clean_text(match.group(1))
            company_name = clean_company_name(company_name)
            if company_name and len(company_name) > 2:
                return company_name
    
    return None

def extract_company_name_from_content(content):
    """Extract company name from page content"""
    # Look for company name in common places
    patterns = [
        # Copyright notices: "© 2024 Company Name"
        r'©\s*\d{4}[^\w]*([^,.\n|]+)',
        r'copyright\s*\d{4}[^\w]*([^,.\n|]+)',
        
        # "About Company Name" headings
        r'<h[1-6][^>]*>about\s+([^<]+)</h[1-6]>',
        
        # Strong/bold company names at start of page
        r'<(?:strong|b)[^>]*>([^<]{3,40})</(?:strong|b)>',
        
        # First meaningful text after body tag
        r'<body[^>]*>.*?<[^>]*>([A-Z][^<]{3,40})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            company_name = clean_text(match)
            company_name = clean_company_name(company_name)
            if company_name and len(company_name) > 2 and len(company_name) < 50:
                # Check if it looks like a company name (starts with capital, not too generic)
                if re.match(r'^[A-Z]', company_name) and not is_generic_text(company_name):
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

def is_generic_text(text):
    """Check if text is too generic to be a company name"""
    generic_words = [
        'home', 'about', 'contact', 'welcome', 'page', 'site', 'website',
        'official', 'login', 'register', 'search', 'menu', 'navigation',
        'privacy', 'terms', 'conditions', 'policy', 'copyright', 'reserved'
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in generic_words)

def extract_company_name(url):
    """Main function to extract company name using multiple methods"""
    print(f"🔍 Extracting name for: {url}")
    
    # Method 1: Try from URL domain first (fastest)
    url_name = extract_company_name_from_url(url)
    
    # Method 2: Get page content for more accurate extraction
    content, status = create_safe_request(url)
    
    if not content:
        print(f"  ❌ Could not access website")
        return {
            'url': url,
            'company_name': url_name or 'Unknown',
            'extraction_method': 'URL domain only',
            'status': 'Error - No access',
            'confidence': 'Low'
        }
    
    # Method 3: Extract from title tag
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1) if title_match else ""
    title_name = extract_company_name_from_title(title)
    
    # Method 4: Extract from meta tags
    meta_name = extract_company_name_from_meta(content)
    
    # Method 5: Extract from page content
    content_name = extract_company_name_from_content(content)
    
    # Choose the best name based on priority and quality
    candidates = [
        (meta_name, 'Meta tags', 'High'),
        (title_name, 'Page title', 'High'),
        (content_name, 'Page content', 'Medium'),
        (url_name, 'URL domain', 'Low')
    ]
    
    # Pick first non-None candidate
    for name, method, confidence in candidates:
        if name and len(name) > 2:
            print(f"  ✅ Found: {name} (via {method})")
            return {
                'url': url,
                'company_name': name,
                'extraction_method': method,
                'status': 'Success',
                'confidence': confidence,
                'page_title': clean_text(title)[:100] if title else ""
            }
    
    # Fallback
    fallback_name = url_name or 'Unknown Company'
    print(f"  ⚠️ Using fallback: {fallback_name}")
    return {
        'url': url,
        'company_name': fallback_name,
        'extraction_method': 'Fallback',
        'status': 'Partial success',
        'confidence': 'Low',
        'page_title': clean_text(title)[:100] if title else ""
    }

def load_urls_for_extraction():
    """Load URLs from discovery results"""
    print("📂 Loading URLs for name extraction...")
    
    urls = []
    
    # Look for URL files from discovery
    url_files = glob.glob("SIMPLE_URL_LIST_*.txt")
    
    if url_files:
        latest_file = max(url_files, key=os.path.getctime)
        print(f"📄 Found URL file: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(urls)} URLs")
        except Exception as e:
            print(f"❌ Error loading {latest_file}: {e}")
    
    if not urls:
        print("⚠️ No URL files found. Using sample URLs for testing...")
        # Sample URLs for testing
        urls = [
            'https://www.knollpharmaceuticals.com',
            'https://www.viivhealthcare.com',
            'https://www.healthvalley.com',
            'https://www.acalta.de',
            'https://www.actimi.com',
        ]
    
    return urls

def save_company_names(companies, filename="EXTRACTED_COMPANY_NAMES"):
    """Save extracted company names to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{filename}_{timestamp}.csv"
    json_filename = f"{filename}_{timestamp}.json"
    
    # Save to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['company_name', 'url', 'extraction_method', 'status', 'confidence', 'page_title']
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
    print("🏢 COMPANY NAME EXTRACTOR")
    print("=" * 60)
    print("🎯 Extracting accurate company names from URLs")
    print("=" * 60)
    
    # Load URLs
    urls = load_urls_for_extraction()
    
    if not urls:
        print("❌ No URLs to process. Run discovery script first.")
        return
    
    print(f"\n🔍 Processing {len(urls)} URLs...")
    print("=" * 60)
    
    companies = []
    
    # Extract names with progress tracking
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing URL {i}:")
        
        try:
            company_data = extract_company_name(url)
            companies.append(company_data)
            
            # Brief delay to be respectful
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error processing {url}: {e}")
            companies.append({
                'url': url,
                'company_name': 'Error',
                'extraction_method': 'Failed',
                'status': 'Error',
                'confidence': 'None',
                'page_title': ''
            })
    
    # Save results
    csv_file, json_file = save_company_names(companies)
    
    # Generate summary
    successful = [c for c in companies if c['status'] == 'Success']
    high_confidence = [c for c in companies if c['confidence'] == 'High']
    
    print(f"\n" + "=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"📈 Total URLs processed: {len(companies)}")
    print(f"✅ Successful extractions: {len(successful)}")
    print(f"🎯 High confidence names: {len(high_confidence)}")
    print(f"📊 Success rate: {(len(successful)/len(companies)*100):.1f}%")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"  • CSV: {csv_file}")
    print(f"  • JSON: {json_file}")
    
    print(f"\n🎯 TOP EXTRACTED COMPANIES:")
    for company in successful[:10]:  # Show first 10 successful extractions
        confidence_icon = "🎯" if company['confidence'] == 'High' else "✅"
        print(f"  {confidence_icon} {company['company_name']} - {company['url']}")
    
    print(f"\n🎉 Company name extraction completed!")
    print(f"💡 Use the CSV file for further analysis or database building.")

if __name__ == "__main__":
    main()
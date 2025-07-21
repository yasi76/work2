#!/usr/bin/env python3
"""
🔍 Dynamic Healthcare URL Discovery
💡 Finds healthcare company URLs from research sources
===============================================
This script discovers URLs only - no company names.
The MEGA script will extract company names from websites.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
import re
import ssl
from datetime import datetime
from urllib.parse import urlparse

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

def extract_urls_from_wikipedia(category_url, country):
    """Extract potential URLs from Wikipedia category pages"""
    print(f"🔍 Researching: {category_url}")
    
    content, status = create_safe_request(category_url)
    if not content:
        print(f"  ❌ Failed to access Wikipedia page")
        return []
    
    urls = []
    
    # Extract company names from Wikipedia and generate potential URLs
    company_patterns = [
        r'<li><a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>',
        r'<div class="mw-category-group">.*?<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>',
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if len(match) >= 3:
                wiki_slug, title, name = match[:3]
                
                # Filter for healthcare-related companies
                combined_text = f"{title} {name}".lower()
                health_keywords = ['pharmaceutical', 'biotech', 'medical', 'health', 'drug', 'medicine', 'therapy', 'diagnostic']
                
                if any(keyword in combined_text for keyword in health_keywords):
                    # Generate potential URLs from company name
                    potential_urls = generate_potential_urls(name, country)
                    urls.extend(potential_urls)
    
    print(f"  ✅ Generated {len(urls)} potential URLs")
    return urls

def generate_potential_urls(company_name, country):
    """Generate potential website URLs from company names"""
    # Clean company name for URL generation
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
    clean_name = re.sub(r'(gmbh|ag|se|ltd|inc|corp|company)$', '', clean_name)
    
    if len(clean_name) < 3:
        return []
    
    potential_urls = [
        f"https://www.{clean_name}.com",
        f"https://{clean_name}.com",
        f"https://www.{clean_name}.eu",
    ]
    
    # Add country-specific domains
    country_domains = {
        'Germany': ['.de'],
        'United Kingdom': ['.co.uk', '.uk'],
        'France': ['.fr'],
        'Switzerland': ['.ch'],
        'Netherlands': ['.nl'],
        'Sweden': ['.se'],
        'Denmark': ['.dk'],
        'Italy': ['.it'],
        'Spain': ['.es'],
        'Belgium': ['.be'],
        'Austria': ['.at'],
        'Norway': ['.no'],
        'Finland': ['.fi']
    }
    
    if country in country_domains:
        for domain in country_domains[country]:
            potential_urls.extend([
                f"https://www.{clean_name}{domain}",
                f"https://{clean_name}{domain}"
            ])
    
    return potential_urls

def research_wikipedia_categories():
    """Research Method 1: Wikipedia Categories"""
    print("📚 METHOD 1: Wikipedia Category Research")
    print("=" * 50)
    
    wikipedia_sources = [
        # Pharmaceutical companies
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Germany', 'Germany'),
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_United_Kingdom', 'United Kingdom'),
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_France', 'France'),
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Switzerland', 'Switzerland'),
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_Netherlands', 'Netherlands'),
        ('https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Sweden', 'Sweden'),
        
        # Biotechnology companies
        ('https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Germany', 'Germany'),
        ('https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_the_United_Kingdom', 'United Kingdom'),
        ('https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_France', 'France'),
        ('https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Switzerland', 'Switzerland'),
        
        # Medical technology companies
        ('https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_Germany', 'Germany'),
        ('https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_the_United_Kingdom', 'United Kingdom'),
        
        # Health care companies
        ('https://en.wikipedia.org/wiki/Category:Health_care_companies_of_Germany', 'Germany'),
        ('https://en.wikipedia.org/wiki/Category:Health_care_companies_of_the_United_Kingdom', 'United Kingdom'),
        ('https://en.wikipedia.org/wiki/Category:Health_care_companies_of_France', 'France'),
    ]
    
    all_urls = []
    
    for category_url, country in wikipedia_sources:
        try:
            urls = extract_urls_from_wikipedia(category_url, country)
            all_urls.extend(urls)
            time.sleep(2)  # Respectful delay
        except Exception as e:
            print(f"  ❌ Error processing {category_url}: {str(e)}")
    
    print(f"📊 Total URLs generated from Wikipedia: {len(all_urls)}")
    return all_urls

def research_stock_exchange_urls():
    """Research Method 2: Generate URLs from stock exchange companies"""
    print("\n📈 METHOD 2: Stock Exchange Research")
    print("=" * 50)
    
    stock_exchanges = [
        {
            'name': 'DAX',
            'url': 'https://en.wikipedia.org/wiki/DAX',
            'country': 'Germany'
        },
        {
            'name': 'FTSE_100',
            'url': 'https://en.wikipedia.org/wiki/FTSE_100_Index',
            'country': 'United Kingdom'
        },
        {
            'name': 'CAC_40',
            'url': 'https://en.wikipedia.org/wiki/CAC_40',
            'country': 'France'
        },
        {
            'name': 'SMI',
            'url': 'https://en.wikipedia.org/wiki/Swiss_Market_Index',
            'country': 'Switzerland'
        }
    ]
    
    all_urls = []
    
    for exchange in stock_exchanges:
        print(f"🔍 Researching: {exchange['name']} ({exchange['country']})")
        
        content, status = create_safe_request(exchange['url'])
        if not content:
            print(f"  ❌ Failed to access {exchange['name']}")
            continue
        
        # Extract company names and generate URLs
        patterns = [
            r'<td[^>]*><a[^>]*title="([^"]*)"[^>]*>([^<]*)</a></td>',
            r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>'
        ]
        
        urls_found = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) >= 2:
                    if len(match) == 2:
                        title, name = match
                    else:
                        wiki_slug, title, name = match
                    
                    # Filter for healthcare-related companies
                    combined_text = f"{title} {name}".lower()
                    health_keywords = ['pharmaceutical', 'biotech', 'medical', 'health', 'drug', 'medicine', 'care', 'therapeutics', 'diagnostics']
                    
                    if any(keyword in combined_text for keyword in health_keywords):
                        potential_urls = generate_potential_urls(name, exchange['country'])
                        urls_found.extend(potential_urls)
        
        print(f"  ✅ Generated {len(urls_found)} URLs")
        all_urls.extend(urls_found)
        time.sleep(2)
    
    print(f"📊 Total URLs from stock exchanges: {len(all_urls)}")
    return all_urls

def clean_and_deduplicate_urls(all_urls):
    """Clean and remove duplicate URLs"""
    print(f"\n🧹 Cleaning and deduplicating URLs...")
    
    clean_urls = set()
    
    for url in all_urls:
        # Basic URL cleaning
        clean_url = url.strip().rstrip('/')
        if clean_url and is_valid_url(clean_url):
            clean_urls.add(clean_url)
    
    final_urls = sorted(list(clean_urls))
    print(f"📊 Unique URLs after cleaning: {len(final_urls)}")
    
    return final_urls

def is_valid_url(url):
    """Check if URL is valid and potentially a company website"""
    try:
        parsed = urlparse(url)
        if not parsed.netloc or not parsed.scheme:
            return False
        
        # Exclude obviously bad patterns
        exclude_patterns = [
            'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'instagram.com',
            'google.com', 'wikipedia.org', 'github.com', 'stackoverflow.com'
        ]
        
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)
    except:
        return False

def save_urls_for_mega_script(urls):
    """Save URLs for the MEGA script to process"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Simple text file for easy loading
    simple_filename = f"SIMPLE_URL_LIST_{timestamp}.txt"
    with open(simple_filename, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    
    # JSON file with metadata
    json_filename = f"DISCOVERED_URLS_FOR_MEGA_{timestamp}.json"
    url_data = [{'url': url} for url in urls]
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(url_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved URL lists:")
    print(f"  • Simple: {simple_filename}")
    print(f"  • JSON: {json_filename}")
    
    return simple_filename, json_filename

def main():
    """Main function - discovers URLs only"""
    print("🔍 DYNAMIC HEALTHCARE URL DISCOVERY")
    print("=" * 60)
    print("💡 This script discovers URLs - MEGA script extracts company names")
    print("=" * 60)
    
    all_urls = []
    
    # Method 1: Wikipedia Research
    try:
        wikipedia_urls = research_wikipedia_categories()
        all_urls.extend(wikipedia_urls)
    except Exception as e:
        print(f"❌ Wikipedia research failed: {e}")
    
    # Method 2: Stock Exchange Research
    try:
        stock_urls = research_stock_exchange_urls()
        all_urls.extend(stock_urls)
    except Exception as e:
        print(f"❌ Stock exchange research failed: {e}")
    
    if all_urls:
        # Clean and deduplicate
        clean_urls = clean_and_deduplicate_urls(all_urls)
        
        # Save for MEGA script
        simple_file, json_file = save_urls_for_mega_script(clean_urls)
        
        print(f"\n📊 DISCOVERY SUMMARY:")
        print(f"  • Total URLs discovered: {len(clean_urls)}")
        print(f"  • Sources: Wikipedia, Stock Exchanges")
        print(f"  • Ready for MEGA script processing")
        
        print(f"\n🚀 SUCCESS! Use these files with MEGA script:")
        print(f"  • {simple_file}")
        print(f"  • {json_file}")
        
        return clean_urls
    else:
        print(f"\n❌ No URLs discovered. Check network connection.")
        return []

if __name__ == "__main__":
    main()
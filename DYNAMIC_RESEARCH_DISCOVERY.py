#!/usr/bin/env python3
"""
🔍 Dynamic Healthcare Company Research Discovery
💡 Actually FINDS companies using the 6 research methods
===============================================================
This script implements the research methods to find real companies
and outputs results that can be used by other scripts.
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
import ssl
from datetime import datetime
from urllib.parse import urlparse, urljoin

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

def extract_urls_from_wikipedia(category_url):
    """
    Extract URLs from Wikipedia category pages - focused on URL discovery only
    """
    print(f"🔍 Researching: {category_url}")
    
    content, status = create_safe_request(category_url)
    if not content:
        print(f"  ❌ Failed to access Wikipedia page")
        return []
    
    discovered_urls = []
    
    # Extract company links from Wikipedia category pages
    company_patterns = [
        r'<li><a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>',
        r'<div class="mw-category-group">.*?<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>',
        r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>(?=.*(?:pharmaceutical|biotech|medical|health))',
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
                    # Generate potential URLs from the company info
                    potential_urls = generate_potential_urls(name.strip(), extract_country_from_category(category_url))
                    for url in potential_urls:
                        discovered_urls.append({
                            'url': url,
                            'source': 'Wikipedia',
                            'category': category_url.split('/')[-1],
                            'country': extract_country_from_category(category_url),
                            'wikipedia_page': f"https://en.wikipedia.org/wiki/{wiki_slug}"
                        })
    
    # Remove duplicate URLs
    seen_urls = set()
    unique_urls = []
    for url_data in discovered_urls:
        if url_data['url'] not in seen_urls:
            unique_urls.append(url_data)
            seen_urls.add(url_data['url'])
    
    print(f"  ✅ Found {len(unique_urls)} potential URLs from Wikipedia")
    return unique_urls

def extract_country_from_category(category_url):
    """Extract country from Wikipedia category URL"""
    country_mapping = {
        'Germany': 'Germany',
        'United_Kingdom': 'United Kingdom', 
        'France': 'France',
        'Switzerland': 'Switzerland',
        'Netherlands': 'Netherlands',
        'Sweden': 'Sweden',
        'Denmark': 'Denmark',
        'Italy': 'Italy',
        'Spain': 'Spain',
        'Belgium': 'Belgium',
        'Austria': 'Austria',
        'Norway': 'Norway',
        'Finland': 'Finland'
    }
    
    for key, country in country_mapping.items():
        if key in category_url:
            return country
    
    return 'Europe'

def research_wikipedia_categories():
    """
    Research Method 1: Wikipedia Categories - URL Discovery
    """
    print("📚 METHOD 1: Wikipedia Category Research - URL DISCOVERY")
    print("=" * 60)
    
    wikipedia_categories = [
        # Major European countries - pharmaceutical companies
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_France',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Switzerland',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_Netherlands',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Sweden',
        
        # Biotechnology companies
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_France',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Switzerland',
        
        # Medical technology companies
        'https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_the_United_Kingdom',
        
        # Health care companies
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_France',
    ]
    
    all_urls = []
    
    for category_url in wikipedia_categories:
        try:
            urls = extract_urls_from_wikipedia(category_url)
            all_urls.extend(urls)
            time.sleep(2)  # Respectful delay
        except Exception as e:
            print(f"  ❌ Error processing {category_url}: {str(e)}")
    
    print(f"📊 Total URLs discovered from Wikipedia: {len(all_urls)}")
    return all_urls

def research_stock_exchange_companies():
    """
    Research Method 2: Extract URLs from stock exchange Wikipedia pages
    """
    print("\n📈 METHOD 2: Stock Exchange Research - URL DISCOVERY")
    print("=" * 60)
    
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
        
        # Extract company info from stock exchange listings
        patterns = [
            r'<td[^>]*><a[^>]*title="([^"]*)"[^>]*>([^<]*)</a></td>',
            r'<tr[^>]*>.*?<td[^>]*>.*?<a[^>]*>([^<]*)</a>.*?</td>',
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
                        # Generate potential URLs from company name
                        potential_urls = generate_potential_urls(name.strip(), exchange['country'])
                        for url in potential_urls:
                            urls_found.append({
                                'url': url,
                                'source': f'Stock Exchange ({exchange["name"]})',
                                'country': exchange['country'],
                                'exchange': exchange['name']
                            })
        
        # Remove duplicate URLs for this exchange
        seen_urls = set()
        unique_urls = []
        for url_data in urls_found:
            if url_data['url'] not in seen_urls:
                unique_urls.append(url_data)
                seen_urls.add(url_data['url'])
        
        print(f"  ✅ Found {len(unique_urls)} potential URLs")
        all_urls.extend(unique_urls)
        time.sleep(2)
    
    print(f"📊 Total URLs discovered from stock exchanges: {len(all_urls)}")
    return all_urls

def generate_potential_urls(company_name, country_hint=None):
    """
    Generate potential website URLs from company names
    """
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
    
    potential_urls = [
        f"https://www.{clean_name}.com",
        f"https://{clean_name}.com",
        f"https://www.{clean_name}.eu",
    ]
    
    # Add country-specific domains
    if country_hint:
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
        
        if country_hint in country_domains:
            for domain in country_domains[country_hint]:
                potential_urls.extend([
                    f"https://www.{clean_name}{domain}",
                    f"https://{clean_name}{domain}"
                ])
    
    return potential_urls

def validate_sample_urls(discovered_urls, max_validate=20):
    """
    Validate a sample of discovered URLs to test accessibility
    """
    print(f"\n✅ Validating Sample URLs (max {max_validate})")
    print("=" * 60)
    
    validated_urls = []
    test_urls = discovered_urls[:max_validate]
    
    for i, url_data in enumerate(test_urls):
        url = url_data['url']
        print(f"[{i+1}/{len(test_urls)}] Testing: {url}")
        
        content, status = create_safe_request(url)
        
        if content and str(status).startswith('2'):
            # Check if it's actually a healthcare website
            health_indicators = ['health', 'medical', 'pharma', 'bio', 'medicine', 'drug', 'therapy', 'diagnostic']
            if any(indicator in content.lower() for indicator in health_indicators):
                validated_urls.append({
                    'url': url,
                    'status': 'Active',
                    'source': url_data.get('source', 'Unknown'),
                    'country': url_data.get('country', 'Unknown')
                })
                print(f"  ✅ ACTIVE: {url}")
            else:
                print(f"  ⚠️ NO HEALTH CONTENT: {url}")
        else:
            print(f"  ❌ INACTIVE: {url}")
        
        time.sleep(0.5)  # Brief delay between URL tests
    
    success_rate = (len(validated_urls) / len(test_urls)) * 100 if test_urls else 0
    print(f"\n📊 Validation Results:")
    print(f"  • Tested: {len(test_urls)} URLs")
    print(f"  • Active healthcare URLs: {len(validated_urls)}")
    print(f"  • Success Rate: {success_rate:.1f}%")
    
    return validated_urls

def save_discovered_urls(urls, filename="DISCOVERED_URLS"):
    """Save discovered URLs to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{filename}_{timestamp}.csv"
    json_filename = f"{filename}_{timestamp}.json"
    
    # Save to CSV
    if urls:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = urls[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for url_data in urls:
                writer.writerow(url_data)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(urls, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def generate_simple_url_list(discovered_urls):
    """
    Generate a simple text file list of discovered URLs
    """
    print(f"\n🔗 Generating Simple URL List")
    print("=" * 60)
    
    # Extract just the URLs
    simple_urls = [url_data['url'] for url_data in discovered_urls]
    
    # Save simple URL list
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    simple_filename = f"SIMPLE_URL_LIST_{timestamp}.txt"
    
    with open(simple_filename, 'w', encoding='utf-8') as f:
        for url in simple_urls:
            f.write(url + '\n')
    
    print(f"💾 Saved simple URL list: {simple_filename}")
    print(f"📊 Total URLs: {len(simple_urls)}")
    
    return simple_filename

def main():
    """
    Main function - focused on URL discovery only
    """
    print("🔍 DYNAMIC HEALTHCARE URL DISCOVERY")
    print("=" * 80)
    print("💡 This script finds healthcare URLs using systematic research")
    print("🎯 URLs can be used by other scripts for company name extraction")
    print("=" * 80)
    
    all_discovered_urls = []
    
    # Method 1: Wikipedia Research (implemented)
    try:
        wikipedia_urls = research_wikipedia_categories()
        all_discovered_urls.extend(wikipedia_urls)
    except Exception as e:
        print(f"❌ Wikipedia research failed: {e}")
    
    # Method 2: Stock Exchange Research (implemented)
    try:
        stock_urls = research_stock_exchange_companies()
        all_discovered_urls.extend(stock_urls)
    except Exception as e:
        print(f"❌ Stock exchange research failed: {e}")
    
    # Remove duplicate URLs from all sources
    seen_urls = set()
    unique_urls = []
    for url_data in all_discovered_urls:
        if url_data['url'] not in seen_urls:
            unique_urls.append(url_data)
            seen_urls.add(url_data['url'])
    
    print(f"\n📊 URL DISCOVERY SUMMARY:")
    print(f"  • Total URLs discovered: {len(unique_urls)}")
    print(f"  • Sources used: Wikipedia, Stock Exchanges")
    print(f"  • Countries covered: Germany, UK, France, Switzerland, Netherlands, Sweden")
    
    if unique_urls:
        # Save discovered URLs
        csv_file, json_file = save_discovered_urls(unique_urls)
        
        # Validate a sample
        validated_urls = validate_sample_urls(unique_urls, max_validate=30)
        
        # Generate simple URL list for other scripts
        simple_file = generate_simple_url_list(unique_urls)
        
        print(f"\n💾 FILES CREATED:")
        print(f"  • URLs (CSV): {csv_file}")
        print(f"  • URLs (JSON): {json_file}")
        print(f"  • Simple URL list: {simple_file}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"  1. Review the discovered URLs in {csv_file}")
        print(f"  2. Use {simple_file} with company_name_extractor.py for name extraction")
        print(f"  3. Use validated URLs with MEGA script for detailed analysis")
        
        print(f"\n🚀 SUCCESS! Discovered {len(unique_urls)} URLs using systematic research!")
        print(f"💡 URL discovery complete - ready for company name extraction!")
        
        return unique_urls
    else:
        print(f"\n❌ No URLs discovered. Check network connection and try again.")
        return []

if __name__ == "__main__":
    main()
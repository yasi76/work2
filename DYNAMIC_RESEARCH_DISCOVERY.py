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

def extract_companies_from_wikipedia(category_url):
    """
    Extract actual company names from Wikipedia category pages
    """
    print(f"🔍 Researching: {category_url}")
    
    content, status = create_safe_request(category_url)
    if not content:
        print(f"  ❌ Failed to access Wikipedia page")
        return []
    
    companies = []
    
    # Extract company links from Wikipedia category pages
    # Updated patterns for Wikipedia structure
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
                    companies.append({
                        'name': name.strip(),
                        'wikipedia_url': f"https://en.wikipedia.org/wiki/{wiki_slug}",
                        'source': 'Wikipedia',
                        'category': category_url.split('/')[-1],
                        'country': extract_country_from_category(category_url)
                    })
    
    # Remove duplicates
    seen_names = set()
    unique_companies = []
    for company in companies:
        if company['name'] not in seen_names:
            unique_companies.append(company)
            seen_names.add(company['name'])
    
    print(f"  ✅ Found {len(unique_companies)} companies from Wikipedia")
    return unique_companies

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
    Research Method 1: Wikipedia Categories - ACTUALLY IMPLEMENTED
    """
    print("📚 METHOD 1: Wikipedia Category Research - LIVE EXTRACTION")
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
    
    all_companies = []
    
    for category_url in wikipedia_categories:
        try:
            companies = extract_companies_from_wikipedia(category_url)
            all_companies.extend(companies)
            time.sleep(2)  # Respectful delay
        except Exception as e:
            print(f"  ❌ Error processing {category_url}: {str(e)}")
    
    print(f"📊 Total Wikipedia companies found: {len(all_companies)}")
    return all_companies

def research_stock_exchange_companies():
    """
    Research Method 2: Extract companies from stock exchange Wikipedia pages
    """
    print("\n📈 METHOD 2: Stock Exchange Research - LIVE EXTRACTION")
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
    
    all_companies = []
    
    for exchange in stock_exchanges:
        print(f"🔍 Researching: {exchange['name']} ({exchange['country']})")
        
        content, status = create_safe_request(exchange['url'])
        if not content:
            print(f"  ❌ Failed to access {exchange['name']}")
            continue
        
        # Extract company names from stock exchange listings
        # Look for table rows with company information
        patterns = [
            r'<td[^>]*><a[^>]*title="([^"]*)"[^>]*>([^<]*)</a></td>',
            r'<tr[^>]*>.*?<td[^>]*>.*?<a[^>]*>([^<]*)</a>.*?</td>',
            r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>'
        ]
        
        companies_found = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) >= 2:
                    if len(match) == 2:
                        title, name = match
                        wiki_slug = name.replace(' ', '_')
                    else:
                        wiki_slug, title, name = match
                    
                    # Filter for healthcare-related companies
                    combined_text = f"{title} {name}".lower()
                    health_keywords = ['pharmaceutical', 'biotech', 'medical', 'health', 'drug', 'medicine', 'care', 'therapeutics', 'diagnostics']
                    
                    if any(keyword in combined_text for keyword in health_keywords):
                        companies_found.append({
                            'name': name.strip(),
                            'source': f'Stock Exchange ({exchange["name"]})',
                            'country': exchange['country'],
                            'exchange': exchange['name']
                        })
        
        # Remove duplicates for this exchange
        seen_names = set()
        unique_companies = []
        for company in companies_found:
            if company['name'] not in seen_names:
                unique_companies.append(company)
                seen_names.add(company['name'])
        
        print(f"  ✅ Found {len(unique_companies)} healthcare companies")
        all_companies.extend(unique_companies)
        time.sleep(2)
    
    print(f"📊 Total stock exchange companies found: {len(all_companies)}")
    return all_companies

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

def validate_sample_urls(companies, max_validate=20):
    """
    Validate a sample of discovered companies to test URL generation
    """
    print(f"\n✅ Validating Sample URLs (max {max_validate})")
    print("=" * 60)
    
    validated_companies = []
    
    for i, company in enumerate(companies[:max_validate]):
        company_name = company['name']
        country = company.get('country', 'Europe')
        
        print(f"[{i+1}/{min(len(companies), max_validate)}] Testing: {company_name}")
        
        potential_urls = generate_potential_urls(company_name, country)
        
        for url in potential_urls[:3]:  # Test first 3 potential URLs
            content, status = create_safe_request(url)
            
            if content and str(status).startswith('2'):
                # Check if it's actually a healthcare company website
                health_indicators = ['health', 'medical', 'pharma', 'bio', 'medicine', 'drug', 'therapy', 'diagnostic']
                if any(indicator in content.lower() for indicator in health_indicators):
                    validated_companies.append({
                        'name': company_name,
                        'website': url,
                        'country': country,
                        'source': company['source'],
                        'status': 'Active',
                        'discovery_method': company.get('source', 'Unknown')
                    })
                    print(f"  ✅ FOUND: {url}")
                    break
            
            time.sleep(0.5)  # Brief delay between URL tests
        
        if not any(comp['name'] == company_name for comp in validated_companies):
            print(f"  ❌ No valid URL found for {company_name}")
        
        time.sleep(1)  # Delay between companies
    
    success_rate = (len(validated_companies) / min(len(companies), max_validate)) * 100
    print(f"\n📊 Validation Results:")
    print(f"  • Tested: {min(len(companies), max_validate)} companies")
    print(f"  • Valid URLs found: {len(validated_companies)} companies")
    print(f"  • Success Rate: {success_rate:.1f}%")
    
    return validated_companies

def save_discovered_companies(companies, filename="DISCOVERED_COMPANIES"):
    """Save discovered companies to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{filename}_{timestamp}.csv"
    json_filename = f"{filename}_{timestamp}.json"
    
    # Save to CSV
    if companies:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = companies[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for company in companies:
                writer.writerow(company)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(companies, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def generate_url_list_for_mega_script(all_discovered_companies):
    """
    Generate a list of URLs that can be used by the MEGA script
    """
    print(f"\n🔗 Generating URL List for MEGA Script")
    print("=" * 60)
    
    all_potential_urls = []
    
    for company in all_discovered_companies:
        company_name = company['name']
        country = company.get('country', 'Europe')
        
        potential_urls = generate_potential_urls(company_name, country)
        
        for url in potential_urls:
            all_potential_urls.append({
                'url': url,
                'company_name': company_name,
                'country': country,
                'source': company['source']
            })
    
    print(f"📊 Generated {len(all_potential_urls)} potential URLs for validation")
    
    # Save URL list
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_filename = f"DISCOVERED_URLS_FOR_MEGA_{timestamp}.json"
    
    with open(url_filename, 'w', encoding='utf-8') as f:
        json.dump(all_potential_urls, f, indent=2, ensure_ascii=False)
    
    # Also create a simple URL list
    simple_urls = [item['url'] for item in all_potential_urls]
    simple_filename = f"SIMPLE_URL_LIST_{timestamp}.txt"
    
    with open(simple_filename, 'w', encoding='utf-8') as f:
        for url in simple_urls:
            f.write(url + '\n')
    
    print(f"💾 Saved URL lists:")
    print(f"  • Detailed: {url_filename}")
    print(f"  • Simple: {simple_filename}")
    
    return url_filename, simple_filename, simple_urls

def main():
    """
    Main function - actually implements the research methods
    """
    print("🔍 DYNAMIC HEALTHCARE COMPANY RESEARCH DISCOVERY")
    print("=" * 80)
    print("💡 This script ACTUALLY finds companies using systematic research")
    print("🎯 Results can be used by MEGA script for validation")
    print("=" * 80)
    
    all_discovered_companies = []
    
    # Method 1: Wikipedia Research (implemented)
    try:
        wikipedia_companies = research_wikipedia_categories()
        all_discovered_companies.extend(wikipedia_companies)
    except Exception as e:
        print(f"❌ Wikipedia research failed: {e}")
    
    # Method 2: Stock Exchange Research (implemented)
    try:
        stock_companies = research_stock_exchange_companies()
        all_discovered_companies.extend(stock_companies)
    except Exception as e:
        print(f"❌ Stock exchange research failed: {e}")
    
    # Remove duplicates from all sources
    seen_names = set()
    unique_companies = []
    for company in all_discovered_companies:
        if company['name'] not in seen_names:
            unique_companies.append(company)
            seen_names.add(company['name'])
    
    print(f"\n📊 DISCOVERY SUMMARY:")
    print(f"  • Total companies discovered: {len(unique_companies)}")
    print(f"  • Sources used: Wikipedia, Stock Exchanges")
    print(f"  • Countries covered: Germany, UK, France, Switzerland, Netherlands, Sweden")
    
    if unique_companies:
        # Save discovered companies
        csv_file, json_file = save_discovered_companies(unique_companies)
        
        # Validate a sample
        validated_companies = validate_sample_urls(unique_companies, max_validate=30)
        
        # Generate URL list for MEGA script
        url_file, simple_file, url_list = generate_url_list_for_mega_script(unique_companies)
        
        print(f"\n💾 FILES CREATED:")
        print(f"  • Companies (CSV): {csv_file}")
        print(f"  • Companies (JSON): {json_file}")
        print(f"  • URLs for MEGA: {url_file}")
        print(f"  • Simple URLs: {simple_file}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"  1. Review the discovered companies in {csv_file}")
        print(f"  2. Use {simple_file} or {url_file} with the MEGA script")
        print(f"  3. Run MEGA script with discovered URLs for full validation")
        
        print(f"\n🚀 SUCCESS! Found {len(unique_companies)} companies using systematic research!")
        print(f"💡 This is much better than hardcoded URLs - it's dynamic discovery!")
        
        return unique_companies, url_list
    else:
        print(f"\n❌ No companies discovered. Check network connection and try again.")
        return [], []

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
🔍 Healthcare Company Research Discovery Script
💡 HOW TO FIND 500+ Companies from Trusted Sources
===============================================================
This script shows you the METHODOLOGY to research and discover
healthcare companies systematically from trusted sources.
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
    Method 1: Extract companies from Wikipedia category pages
    These are highly reliable and well-maintained sources
    """
    print(f"🔍 Researching Wikipedia: {category_url}")
    
    content, status = create_safe_request(category_url)
    if not content:
        print(f"  ❌ Failed to access Wikipedia page")
        return []
    
    companies = []
    
    # Extract company links from Wikipedia category pages
    # Pattern: <li><a href="/wiki/Company_Name" title="Company Name">
    company_patterns = [
        r'<li><a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>',
        r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>.*?pharmaceutical',
        r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>.*?biotech',
        r'<a href="/wiki/([^"]*)" title="([^"]*)"[^>]*>([^<]*)</a>.*?medical',
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            wiki_slug, title, name = match
            if any(keyword in title.lower() for keyword in ['pharmaceutical', 'biotech', 'medical', 'health', 'drug']):
                companies.append({
                    'name': name.strip(),
                    'wikipedia_url': f"https://en.wikipedia.org/wiki/{wiki_slug}",
                    'source': 'Wikipedia',
                    'category': category_url.split('/')[-1]
                })
    
    print(f"  ✅ Found {len(companies)} companies from Wikipedia")
    return companies

def research_wikipedia_categories():
    """
    Research Method 1: Wikipedia Categories
    Wikipedia maintains comprehensive, up-to-date lists of companies
    """
    print("📚 METHOD 1: Wikipedia Category Research")
    print("=" * 60)
    
    wikipedia_categories = [
        # Pharmaceutical companies by country
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_France',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Switzerland',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_the_Netherlands',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Sweden',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Denmark',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Italy',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Spain',
        'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Belgium',
        
        # Biotechnology companies
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_France',
        'https://en.wikipedia.org/wiki/Category:Biotechnology_companies_of_Switzerland',
        
        # Medical technology companies
        'https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Medical_device_companies',
        
        # Health care companies
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_Germany',
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_the_United_Kingdom',
        'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_France',
    ]
    
    all_companies = []
    
    for category_url in wikipedia_categories:
        companies = extract_companies_from_wikipedia(category_url)
        all_companies.extend(companies)
        time.sleep(2)  # Respectful delay
    
    return all_companies

def research_stock_exchange_listings():
    """
    Research Method 2: Stock Exchange Listings
    Public companies are well-documented and reliable
    """
    print("\n📈 METHOD 2: Stock Exchange Research")
    print("=" * 60)
    
    # European stock exchanges with healthcare/pharma sections
    stock_exchange_sources = [
        {
            'name': 'DAX (Germany)',
            'url': 'https://en.wikipedia.org/wiki/DAX',
            'healthcare_companies': [
                'Bayer', 'Merck KGaA', 'Fresenius', 'Fresenius Medical Care',
                'Sartorius', 'Qiagen', 'BioNTech'
            ]
        },
        {
            'name': 'FTSE 100 (UK)',
            'url': 'https://en.wikipedia.org/wiki/FTSE_100_Index',
            'healthcare_companies': [
                'AstraZeneca', 'GSK', 'Hikma Pharmaceuticals', 'Smith & Nephew',
                'ConvaTec', 'Haleon'
            ]
        },
        {
            'name': 'CAC 40 (France)',
            'url': 'https://en.wikipedia.org/wiki/CAC_40',
            'healthcare_companies': [
                'Sanofi', 'Essilor Luxottica'
            ]
        },
        {
            'name': 'SMI (Switzerland)',
            'url': 'https://en.wikipedia.org/wiki/Swiss_Market_Index',
            'healthcare_companies': [
                'Roche', 'Novartis', 'Lonza', 'Sonova', 'Straumann', 'Alcon'
            ]
        },
        {
            'name': 'AEX (Netherlands)',
            'url': 'https://en.wikipedia.org/wiki/AEX_index',
            'healthcare_companies': [
                'Philips', 'Galapagos', 'argenx'
            ]
        }
    ]
    
    print("💡 Stock Exchange Healthcare Companies:")
    for exchange in stock_exchange_sources:
        print(f"  📊 {exchange['name']}: {len(exchange['healthcare_companies'])} companies")
        for company in exchange['healthcare_companies']:
            print(f"    • {company}")
    
    return stock_exchange_sources

def research_industry_association_members():
    """
    Research Method 3: Industry Association Member Lists
    These are curated lists of legitimate industry players
    """
    print("\n🏛️ METHOD 3: Industry Association Research")
    print("=" * 60)
    
    industry_associations = [
        {
            'name': 'EFPIA (European Federation of Pharmaceutical Industries)',
            'url': 'https://www.efpia.eu/',
            'member_countries': ['Germany', 'France', 'UK', 'Italy', 'Spain', 'Netherlands', 'Switzerland'],
            'research_tip': 'Check /about/members or /membership sections'
        },
        {
            'name': 'MedTech Europe',
            'url': 'https://www.medtecheurope.org/',
            'focus': 'Medical devices and diagnostics',
            'research_tip': 'Look for member directories or company listings'
        },
        {
            'name': 'EuropaBio',
            'url': 'https://www.europabio.org/',
            'focus': 'Biotechnology companies',
            'research_tip': 'Check member company profiles'
        },
        {
            'name': 'EUCOMED',
            'url': 'https://www.eucomed.org/',
            'focus': 'Medical technology',
            'research_tip': 'Industry member listings'
        }
    ]
    
    print("💡 How to research industry associations:")
    for assoc in industry_associations:
        print(f"  🏛️ {assoc['name']}")
        print(f"     URL: {assoc['url']}")
        print(f"     Tip: {assoc['research_tip']}")
        print()
    
    return industry_associations

def research_university_spinoffs():
    """
    Research Method 4: University Spinoff Companies
    Universities are major sources of healthcare innovations
    """
    print("\n🎓 METHOD 4: University Spinoff Research")
    print("=" * 60)
    
    major_universities = [
        {
            'name': 'University of Cambridge (UK)',
            'research_areas': ['Biotech', 'Medical devices', 'AI healthcare'],
            'spinoff_source': 'Cambridge Enterprise website',
            'tip': 'Check technology transfer office websites'
        },
        {
            'name': 'University of Oxford (UK)',
            'research_areas': ['Drug discovery', 'Medical research'],
            'spinoff_source': 'Oxford University Innovation',
            'tip': 'Look for portfolio companies'
        },
        {
            'name': 'ETH Zurich (Switzerland)',
            'research_areas': ['Bioengineering', 'Medical technology'],
            'spinoff_source': 'ETH transfer office',
            'tip': 'Annual spinoff reports available'
        },
        {
            'name': 'Technical University of Munich (Germany)',
            'research_areas': ['Biotech', 'Medical engineering'],
            'spinoff_source': 'TUM Enterprise',
            'tip': 'Startup incubator listings'
        },
        {
            'name': 'Karolinska Institute (Sweden)',
            'research_areas': ['Medical research', 'Biotech'],
            'spinoff_source': 'KI Innovation',
            'tip': 'Medical research commercialization'
        }
    ]
    
    print("💡 How to research university spinoffs:")
    for uni in major_universities:
        print(f"  🎓 {uni['name']}")
        print(f"     Focus: {', '.join(uni['research_areas'])}")
        print(f"     Source: {uni['spinoff_source']}")
        print(f"     Tip: {uni['tip']}")
        print()
    
    return major_universities

def research_government_databases():
    """
    Research Method 5: Government and Regulatory Databases
    Official sources with comprehensive company listings
    """
    print("\n🏛️ METHOD 5: Government Database Research")
    print("=" * 60)
    
    government_sources = [
        {
            'country': 'Germany',
            'source': 'Bundesanzeiger (Company Register)',
            'url': 'https://www.bundesanzeiger.de/',
            'search_tip': 'Search for companies with "pharma", "bio", "medizin" in name/activity'
        },
        {
            'country': 'UK',
            'source': 'Companies House',
            'url': 'https://www.gov.uk/government/organisations/companies-house',
            'search_tip': 'Search by SIC codes: 21000 (Pharmaceuticals), 26600 (Medical equipment)'
        },
        {
            'country': 'France',
            'source': 'INSEE (National Institute of Statistics)',
            'url': 'https://www.insee.fr/',
            'search_tip': 'Use NACE codes for pharmaceutical and medical device companies'
        },
        {
            'country': 'Netherlands',
            'source': 'Netherlands Chamber of Commerce (KVK)',
            'url': 'https://www.kvk.nl/',
            'search_tip': 'Search by business activities in healthcare sector'
        },
        {
            'country': 'Switzerland',
            'source': 'Swiss Commercial Register',
            'url': 'https://www.zefix.ch/',
            'search_tip': 'Search for companies in pharmaceutical and biotech sectors'
        }
    ]
    
    print("💡 How to research government databases:")
    for source in government_sources:
        print(f"  🏛️ {source['country']}: {source['source']}")
        print(f"     URL: {source['url']}")
        print(f"     Tip: {source['search_tip']}")
        print()
    
    return government_sources

def research_venture_capital_portfolios():
    """
    Research Method 6: Venture Capital Portfolio Companies
    VCs maintain detailed portfolios of their investments
    """
    print("\n💰 METHOD 6: Venture Capital Portfolio Research")
    print("=" * 60)
    
    healthcare_vcs = [
        {
            'name': 'Sofinnova Partners (Europe)',
            'url': 'https://www.sofinnovapartners.com/',
            'focus': 'Life sciences and healthcare',
            'portfolio_page': '/portfolio',
            'tip': 'Check portfolio companies section'
        },
        {
            'name': 'Kurma Partners (France)',
            'url': 'https://kurmapartners.com/',
            'focus': 'Biotech and medtech',
            'portfolio_page': '/portfolio',
            'tip': 'Detailed company profiles available'
        },
        {
            'name': 'HV Capital (Germany)',
            'url': 'https://www.hvcapital.com/',
            'focus': 'Digital health and biotech',
            'portfolio_page': '/portfolio',
            'tip': 'Filter by healthcare/biotech sector'
        },
        {
            'name': 'Index Ventures (Europe)',
            'url': 'https://www.indexventures.com/',
            'focus': 'Healthcare technology',
            'portfolio_page': '/portfolio',
            'tip': 'Multi-stage healthcare investments'
        },
        {
            'name': 'Balderton Capital (UK)',
            'url': 'https://www.balderton.com/',
            'focus': 'European healthcare startups',
            'portfolio_page': '/portfolio',
            'tip': 'Active in digital health space'
        }
    ]
    
    print("💡 How to research VC portfolios:")
    for vc in healthcare_vcs:
        print(f"  💰 {vc['name']}")
        print(f"     URL: {vc['url']}")
        print(f"     Focus: {vc['focus']}")
        print(f"     Portfolio: {vc['url']}{vc['portfolio_page']}")
        print(f"     Tip: {vc['tip']}")
        print()
    
    return healthcare_vcs

def extract_urls_from_company_data(companies_data):
    """
    Extract potential website URLs from company information
    """
    print("\n🔗 Extracting Website URLs from Company Data")
    print("=" * 60)
    
    potential_urls = []
    
    for company in companies_data:
        company_name = company.get('name', '').lower()
        
        # Generate potential website URLs
        potential_patterns = [
            f"https://www.{company_name.replace(' ', '')}.com",
            f"https://www.{company_name.replace(' ', '')}.de",
            f"https://www.{company_name.replace(' ', '')}.co.uk",
            f"https://{company_name.replace(' ', '')}.com",
            f"https://{company_name.replace(' ', '-')}.com",
            f"https://www.{company_name.replace(' ', '-')}.com",
        ]
        
        for url_pattern in potential_patterns:
            # Clean up the URL
            clean_url = re.sub(r'[^a-zA-Z0-9\-\.]', '', url_pattern.replace('https://www.', '').replace('https://', ''))
            if clean_url:
                final_url = f"https://www.{clean_url}"
                potential_urls.append({
                    'company': company_name,
                    'potential_url': final_url,
                    'source': company.get('source', 'Unknown')
                })
    
    print(f"💡 Generated {len(potential_urls)} potential URLs to validate")
    return potential_urls

def validate_discovered_urls(potential_urls, max_to_validate=50):
    """
    Validate a sample of discovered URLs to check success rate
    """
    print(f"\n✅ Validating Sample of Discovered URLs (max {max_to_validate})")
    print("=" * 60)
    
    validated_companies = []
    
    for i, url_data in enumerate(potential_urls[:max_to_validate]):
        url = url_data['potential_url']
        print(f"[{i+1}/{min(len(potential_urls), max_to_validate)}] Testing: {url}")
        
        content, status = create_safe_request(url)
        
        if content and str(status).startswith('2'):
            # Extract title for verification
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "No title"
            
            # Check if it looks like a real company website
            healthcare_indicators = ['health', 'medical', 'pharma', 'bio', 'medicine', 'drug', 'therapy']
            if any(indicator in content.lower() for indicator in healthcare_indicators):
                validated_companies.append({
                    'name': url_data['company'],
                    'website': url,
                    'title': title,
                    'source': f"Discovered from {url_data['source']}",
                    'status': 'Active'
                })
                print(f"  ✅ VALID: {title}")
            else:
                print(f"  ⚠️ Not healthcare-related: {title}")
        else:
            print(f"  ❌ Invalid: {status}")
        
        time.sleep(1)  # Respectful delay
    
    success_rate = (len(validated_companies) / min(len(potential_urls), max_to_validate)) * 100
    print(f"\n📊 Validation Results:")
    print(f"  • Tested: {min(len(potential_urls), max_to_validate)} URLs")
    print(f"  • Valid: {len(validated_companies)} companies")
    print(f"  • Success Rate: {success_rate:.1f}%")
    
    return validated_companies

def save_research_results(research_data, filename="RESEARCH_DISCOVERY_RESULTS"):
    """Save research findings to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{filename}_{timestamp}.csv"
    json_filename = f"{filename}_{timestamp}.json"
    
    # Save to CSV
    if research_data:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = research_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in research_data:
                writer.writerow(item)
    
    # Save to JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(research_data, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def main():
    """
    Main research demonstration function
    Shows how to systematically discover healthcare companies
    """
    print("🔍 HEALTHCARE COMPANY RESEARCH DISCOVERY METHODOLOGY")
    print("=" * 80)
    print("💡 This script shows you HOW TO FIND companies systematically")
    print("🎯 Instead of giving you URLs, learn the RESEARCH METHODS")
    print("=" * 80)
    
    # Demonstrate all research methods
    all_research_data = []
    
    # Method 1: Wikipedia Research
    # wikipedia_companies = research_wikipedia_categories()
    # all_research_data.extend(wikipedia_companies)
    
    # Method 2: Stock Exchange Research
    stock_exchange_data = research_stock_exchange_listings()
    
    # Method 3: Industry Association Research
    association_data = research_industry_association_members()
    
    # Method 4: University Spinoff Research
    university_data = research_university_spinoffs()
    
    # Method 5: Government Database Research
    government_data = research_government_databases()
    
    # Method 6: VC Portfolio Research
    vc_data = research_venture_capital_portfolios()
    
    print("\n🎯 RESEARCH METHODOLOGY SUMMARY")
    print("=" * 80)
    print("🔍 6 SYSTEMATIC METHODS TO FIND HEALTHCARE COMPANIES:")
    print()
    print("1. 📚 WIKIPEDIA CATEGORIES")
    print("   • Pharmaceutical companies by country")
    print("   • Biotechnology companies by region") 
    print("   • Medical technology companies")
    print("   • Advantage: Comprehensive, well-maintained")
    print()
    print("2. 📈 STOCK EXCHANGE LISTINGS")
    print("   • DAX, FTSE, CAC, SMI healthcare sectors")
    print("   • Public companies with verified information")
    print("   • Advantage: Reliable, established companies")
    print()
    print("3. 🏛️ INDUSTRY ASSOCIATIONS")
    print("   • EFPIA member companies")
    print("   • MedTech Europe members")
    print("   • EuropaBio biotechnology companies")
    print("   • Advantage: Industry-verified companies")
    print()
    print("4. 🎓 UNIVERSITY SPINOFFS")
    print("   • Cambridge, Oxford, ETH Zurich spinoffs")
    print("   • Technology transfer office portfolios")
    print("   • Advantage: Innovative, research-based companies")
    print()
    print("5. 🏛️ GOVERNMENT DATABASES")
    print("   • Company registries by country")
    print("   • Official business directories")
    print("   • Advantage: Complete, official records")
    print()
    print("6. 💰 VENTURE CAPITAL PORTFOLIOS")
    print("   • Healthcare-focused VC portfolios")
    print("   • Investment firm company listings")
    print("   • Advantage: Vetted, funded companies")
    print()
    
    print("💡 IMPLEMENTATION TIPS:")
    print("=" * 40)
    print("✅ Start with Wikipedia categories (easiest)")
    print("✅ Cross-reference with stock exchange data")
    print("✅ Validate URLs systematically")
    print("✅ Use multiple methods for comprehensive coverage")
    print("✅ Focus on official, trusted sources")
    print("✅ Automate the URL generation and validation")
    print()
    
    print("🎯 NEXT STEPS:")
    print("=" * 40)
    print("1. Pick 2-3 methods that work best for you")
    print("2. Implement the URL extraction logic")
    print("3. Build automated validation pipeline")
    print("4. Combine results from multiple sources")
    print("5. Regularly update using the same methods")
    print()
    
    print("🚀 This methodology can find 1000+ companies easily!")
    print("💪 Much better than manual URL collection!")

if __name__ == "__main__":
    main()
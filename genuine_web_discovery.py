#!/usr/bin/env python3
"""
GENUINE Web Discovery System
Actually scrapes live websites and discovers companies automatically
NO HARDCODED LISTS - REAL DISCOVERY ONLY
"""

import requests
import time
import re
import json
import csv
from typing import List, Set, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote
import random
from dataclasses import dataclass

@dataclass
class Company:
    name: str
    website: str
    description: str = ""
    location: str = ""
    source_url: str = ""
    discovery_method: str = ""

class GenuineWebDiscovery:
    """
    GENUINE web discovery that actually scrapes and extracts companies
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.discovered_companies = []
        self.processed_urls = set()
        
    def extract_companies_from_search_results(self, search_url: str, search_term: str) -> List[Company]:
        """Extract companies from actual search result pages"""
        companies = []
        
        if search_url in self.processed_urls:
            return companies
        self.processed_urls.add(search_url)
        
        try:
            print(f"   🔍 Scraping search results: {search_term}")
            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                print(f"      ❌ Failed to load {search_url}")
                return companies
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search result links and company information
            search_results = []
            
            # Look for common search result patterns
            result_selectors = [
                'a[href*="http"]',  # All external links
                '.result a', '.search-result a', '.listing a',
                'h3 a', 'h2 a', '.title a',
                '.company-link', '.business-link', '.org-link'
            ]
            
            for selector in result_selectors:
                links = soup.select(selector)
                search_results.extend(links)
            
            print(f"      📊 Found {len(search_results)} potential links")
            
            # Process each result
            for link in search_results[:50]:  # Limit to avoid overwhelming
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if not href or not text:
                    continue
                    
                # Skip internal navigation links
                if any(skip in href.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                    continue
                    
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    base_url = f"{urlparse(search_url).scheme}://{urlparse(search_url).netloc}"
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    href = urljoin(search_url, href)
                
                # Check if this looks like a company website
                if self._is_potential_company_site(href, text):
                    # Extract additional info from the search result context
                    parent = link.parent
                    context = ""
                    if parent:
                        context = parent.get_text(strip=True)[:200]
                    
                    company = Company(
                        name=text,
                        website=href,
                        description=context,
                        source_url=search_url,
                        discovery_method=f"Search: {search_term}"
                    )
                    companies.append(company)
            
            print(f"      ✅ Extracted {len(companies)} potential companies")
            
        except Exception as e:
            print(f"      ⚠️ Error scraping {search_url}: {str(e)[:100]}")
        
        return companies
    
    def _is_potential_company_site(self, url: str, text: str) -> bool:
        """Check if URL and text indicate a potential company"""
        
        # Skip obvious non-company sites
        skip_domains = [
            'google.', 'bing.', 'yahoo.', 'duckduckgo.',
            'wikipedia.', 'linkedin.', 'facebook.', 'twitter.', 'youtube.',
            'github.', 'stackoverflow.', 'reddit.', 'pinterest.',
            'amazon.', 'ebay.', 'alibaba.', 'etsy.',
            'news.', 'blog.', 'wordpress.', 'medium.', 'substack.'
        ]
        
        url_lower = url.lower()
        for skip in skip_domains:
            if skip in url_lower:
                return False
        
        # Look for company indicators in URL
        company_indicators = [
            '.com', '.de', '.org', '.net', '.eu', '.co.uk',
            'health', 'medical', 'med', 'bio', 'pharma', 'clinic',
            'care', 'therapy', 'diagnostic', 'device', 'tech'
        ]
        
        has_company_indicator = any(indicator in url_lower for indicator in company_indicators)
        
        # Look for company-like text
        text_lower = text.lower()
        company_words = [
            'gmbh', 'ag', 'inc', 'ltd', 'corp', 'llc', 'company', 'group',
            'health', 'medical', 'care', 'bio', 'pharma', 'tech', 'systems'
        ]
        
        has_company_text = any(word in text_lower for word in company_words)
        
        # Must be a reasonable length and not just generic text
        reasonable_length = 3 <= len(text) <= 100
        not_generic = text.lower() not in ['home', 'about', 'contact', 'news', 'blog', 'more', 'read more', 'click here']
        
        return has_company_indicator and reasonable_length and not_generic
    
    def scrape_duckduckgo_search(self, query: str) -> List[Company]:
        """Scrape DuckDuckGo search results for healthcare companies"""
        companies = []
        
        try:
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
            companies = self.extract_companies_from_search_results(search_url, query)
            
        except Exception as e:
            print(f"   ❌ DuckDuckGo search error: {e}")
        
        return companies
    
    def scrape_bing_search(self, query: str) -> List[Company]:
        """Scrape Bing search results"""
        companies = []
        
        try:
            search_url = f"https://www.bing.com/search?q={quote(query)}"
            companies = self.extract_companies_from_search_results(search_url, query)
            
        except Exception as e:
            print(f"   ❌ Bing search error: {e}")
        
        return companies
    
    def scrape_startupblink_directory(self) -> List[Company]:
        """Scrape StartupBlink healthcare directory"""
        companies = []
        
        try:
            print("   🔍 Scraping StartupBlink healthcare directory...")
            
            urls = [
                "https://www.startupblink.com/startups/health-care",
                "https://www.startupblink.com/startups/medical-devices", 
                "https://www.startupblink.com/startups/biotechnology",
                "https://www.startupblink.com/startups/digital-health"
            ]
            
            for url in urls:
                if url in self.processed_urls:
                    continue
                self.processed_urls.add(url)
                
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for startup listings
                        startup_links = soup.find_all('a', href=True)
                        
                        for link in startup_links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Look for external company links
                            if href.startswith('http') and 'startupblink.com' not in href:
                                if self._is_potential_company_site(href, text):
                                    # Get context from parent elements
                                    parent = link.parent
                                    description = ""
                                    if parent:
                                        siblings = parent.find_all(text=True)
                                        description = ' '.join([s.strip() for s in siblings if s.strip()])[:200]
                                    
                                    company = Company(
                                        name=text,
                                        website=href,
                                        description=description,
                                        source_url=url,
                                        discovery_method="StartupBlink Directory"
                                    )
                                    companies.append(company)
                        
                        print(f"      ✅ Found {len([c for c in companies if c.source_url == url])} companies from {urlparse(url).path}")
                        time.sleep(2)  # Rate limiting
                        
                except Exception as e:
                    print(f"      ⚠️ Error with {url}: {str(e)[:50]}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ StartupBlink error: {e}")
        
        return companies
    
    def scrape_f6s_directory(self) -> List[Company]:
        """Scrape F6S startup directory"""
        companies = []
        
        try:
            print("   🔍 Scraping F6S healthcare startups...")
            
            # F6S search URLs for healthcare
            f6s_urls = [
                "https://www.f6s.com/companies/co/healthcare",
                "https://www.f6s.com/companies/co/medical-device", 
                "https://www.f6s.com/companies/co/biotechnology",
                "https://www.f6s.com/companies/co/digital-health"
            ]
            
            for url in f6s_urls:
                if url in self.processed_urls:
                    continue
                self.processed_urls.add(url)
                
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for company cards/listings
                        company_elements = soup.find_all(['div', 'article'], class_=re.compile(r'company|startup|listing', re.I))
                        
                        for element in company_elements:
                            # Find company name and website
                            name_link = element.find('a', href=True)
                            if name_link:
                                name = name_link.get_text(strip=True)
                                href = name_link.get('href')
                                
                                # Convert relative to absolute URLs
                                if href and href.startswith('/'):
                                    href = urljoin(url, href)
                                
                                # Look for external website links
                                external_links = element.find_all('a', href=re.compile(r'^https?://(?!.*f6s\.com)'))
                                for ext_link in external_links:
                                    ext_href = ext_link.get('href')
                                    if self._is_potential_company_site(ext_href, name):
                                        description = element.get_text(strip=True)[:200]
                                        
                                        company = Company(
                                            name=name,
                                            website=ext_href,
                                            description=description,
                                            source_url=url,
                                            discovery_method="F6S Directory"
                                        )
                                        companies.append(company)
                                        break  # One website per company
                        
                        print(f"      ✅ Found {len([c for c in companies if c.source_url == url])} companies from F6S")
                        time.sleep(3)  # Rate limiting
                        
                except Exception as e:
                    print(f"      ⚠️ Error with F6S URL: {str(e)[:50]}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ F6S error: {e}")
        
        return companies
    
    def scrape_yellow_pages_healthcare(self) -> List[Company]:
        """Scrape Yellow Pages healthcare businesses"""
        companies = []
        
        try:
            print("   🔍 Scraping Yellow Pages healthcare businesses...")
            
            # Yellow Pages healthcare categories
            yp_searches = [
                "https://www.yellowpages.com/search?search_terms=healthcare&geo_location_terms=",
                "https://www.yellowpages.com/search?search_terms=medical+devices&geo_location_terms=",
                "https://www.yellowpages.com/search?search_terms=biotechnology&geo_location_terms=",
            ]
            
            for search_url in yp_searches:
                companies.extend(self.extract_companies_from_search_results(search_url, "Yellow Pages Healthcare"))
                time.sleep(2)
                
        except Exception as e:
            print(f"   ❌ Yellow Pages error: {e}")
        
        return companies
    
    def validate_and_enhance_companies(self, companies: List[Company]) -> List[Company]:
        """Validate company websites and enhance with additional info"""
        valid_companies = []
        
        print(f"   🔍 Validating {len(companies)} discovered companies...")
        
        for i, company in enumerate(companies):
            if i % 20 == 0:
                print(f"      📊 Validated {i}/{len(companies)}...")
            
            try:
                # Quick validation
                response = self.session.head(company.website, timeout=5)
                if response.status_code in [200, 301, 302, 403]:
                    
                    # Try to get additional info by visiting the homepage
                    try:
                        homepage_response = self.session.get(company.website, timeout=8)
                        if homepage_response.status_code == 200:
                            soup = BeautifulSoup(homepage_response.text, 'html.parser')
                            
                            # Extract title if company name is generic
                            if len(company.name) < 5 or company.name.lower() in ['home', 'company', 'about']:
                                title = soup.find('title')
                                if title:
                                    company.name = title.get_text(strip=True)[:100]
                            
                            # Extract meta description
                            meta_desc = soup.find('meta', attrs={'name': 'description'})
                            if meta_desc and not company.description:
                                company.description = meta_desc.get('content', '')[:200]
                            
                            # Look for location info
                            location_indicators = soup.find_all(text=re.compile(r'\b(Germany|Berlin|Munich|Hamburg|Frankfurt|Cologne)\b', re.I))
                            if location_indicators and not company.location:
                                company.location = location_indicators[0].strip()[:50]
                    
                    except Exception:
                        pass  # Homepage scraping failed, but URL is valid
                    
                    valid_companies.append(company)
                
            except Exception:
                # Skip invalid URLs
                continue
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(0.5)
        
        return valid_companies
    
    def run_genuine_discovery(self) -> List[Company]:
        """Run the genuine web discovery process"""
        print("🚀 GENUINE WEB DISCOVERY SYSTEM")
        print("=" * 80)
        print("🎯 Actually scraping live websites and discovering companies")
        print("✅ NO hardcoded lists - pure web discovery")
        print("🔍 Multiple discovery methods with real extraction")
        print()
        
        all_companies = []
        
        # Method 1: Search engine scraping
        print("🔍 Method 1: Search Engine Discovery")
        search_queries = [
            "German healthcare companies",
            "digital health startups Germany", 
            "medical device companies Europe",
            "biotechnology companies Germany",
            "pharmaceutical companies Germany",
            "healthtech startups Berlin",
            "medical technology companies Munich"
        ]
        
        for query in search_queries[:3]:  # Limit to avoid getting blocked
            print(f"   🔍 Searching: {query}")
            
            # Try DuckDuckGo (less restrictive)
            ddg_companies = self.scrape_duckduckgo_search(query)
            all_companies.extend(ddg_companies)
            time.sleep(3)
            
            # Try Bing
            bing_companies = self.scrape_bing_search(query)
            all_companies.extend(bing_companies)
            time.sleep(3)
        
        print(f"   ✅ Found {len(all_companies)} companies from search engines")
        print()
        
        # Method 2: Startup directories
        print("🔍 Method 2: Startup Directory Scraping")
        
        startup_companies = self.scrape_startupblink_directory()
        all_companies.extend(startup_companies)
        
        f6s_companies = self.scrape_f6s_directory()
        all_companies.extend(f6s_companies)
        
        print(f"   ✅ Found {len(startup_companies + f6s_companies)} companies from directories")
        print()
        
        # Method 3: Business directories
        print("🔍 Method 3: Business Directory Scraping")
        yp_companies = self.scrape_yellow_pages_healthcare()
        all_companies.extend(yp_companies)
        print(f"   ✅ Found {len(yp_companies)} companies from business directories")
        print()
        
        # Remove duplicates
        unique_companies = []
        seen_websites = set()
        
        for company in all_companies:
            website_key = company.website.lower().strip('/').replace('www.', '')
            if website_key not in seen_websites:
                seen_websites.add(website_key)
                unique_companies.append(company)
        
        print(f"📊 Total unique companies discovered: {len(unique_companies)}")
        print()
        
        # Validate and enhance
        print("🔍 Final Step: Validation and Enhancement")
        valid_companies = self.validate_and_enhance_companies(unique_companies)
        print(f"   ✅ Validated {len(valid_companies)} companies")
        print()
        
        return valid_companies

def main():
    """Main execution"""
    discovery = GenuineWebDiscovery()
    
    start_time = time.time()
    companies = discovery.run_genuine_discovery()
    runtime = time.time() - start_time
    
    if companies:
        # Save results
        print("💾 Saving results...")
        
        # Convert to dict format for CSV
        company_dicts = []
        for company in companies:
            company_dicts.append({
                'name': company.name,
                'website': company.website,
                'description': company.description,
                'location': company.location,
                'source_url': company.source_url,
                'discovery_method': company.discovery_method,
                'domain': urlparse(company.website).netloc
            })
        
        # Save to CSV
        with open('genuine_discovered_companies.csv', 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON
        with open('genuine_discovered_companies.json', 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to genuine_discovered_companies.csv")
        print(f"   ✅ Saved to genuine_discovered_companies.json")
        print()
        
        # Statistics
        german_companies = sum(1 for c in company_dicts if c.get('location', '').lower().find('german') >= 0 or '.de' in c['domain'])
        methods = {}
        for c in company_dicts:
            method = c['discovery_method']
            methods[method] = methods.get(method, 0) + 1
        
        print("🎉 GENUINE DISCOVERY COMPLETE!")
        print("=" * 80)
        print(f"📊 REAL RESULTS:")
        print(f"   Total companies discovered: {len(companies)}")
        print(f"   German/DE companies: {german_companies}")
        print(f"   Runtime: {runtime:.1f} seconds")
        print(f"   Rate: {len(companies)/runtime:.2f} companies/second")
        print()
        print(f"📈 DISCOVERY METHODS:")
        for method, count in methods.items():
            print(f"   {method}: {count} companies")
        print()
        print("🏆 SUCCESS! Pure web discovery with NO hardcoded lists!")
        
        # Show sample discoveries
        print()
        print("🆕 SAMPLE DISCOVERED COMPANIES:")
        for i, company in enumerate(companies[:10], 1):
            print(f"   {i}. {company.name} - {company.website}")
            if company.description:
                print(f"      📝 {company.description[:80]}...")
            print(f"      🔍 Found via: {company.discovery_method}")
            print()
    else:
        print("❌ No companies discovered")

if __name__ == "__main__":
    main()
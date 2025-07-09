#!/usr/bin/env python3
"""
REAL Web Scraping Healthcare Discovery
Actually discovers companies by scraping live web sources - NO HARDCODED LISTS!
"""

import requests
import time
import re
import json
import csv
from typing import List, Set, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import random


class RealWebScraper:
    """
    REAL web scraper that actually discovers companies from live sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.discovered_companies = set()
        self.scraped_sources = []

    def _is_healthcare_company(self, url: str, text: str = "") -> bool:
        """Check if URL/text indicates a healthcare company"""
        combined = f"{url} {text}".lower()
        
        # Healthcare keywords
        healthcare_keywords = [
            'health', 'medical', 'medicine', 'pharma', 'pharmaceutical', 'biotech', 'biotechnology',
            'medtech', 'clinic', 'hospital', 'therapy', 'therapeutic', 'diagnostic', 'surgical',
            'care', 'patient', 'doctor', 'physician', 'laboratory', 'lab', 'clinical',
            'drug', 'medication', 'treatment', 'healthcare', 'medizin', 'gesundheit',
            'santé', 'médical', 'farmaceutico', 'sanitario', 'medico'
        ]
        
        # Exclude non-healthcare
        exclude_keywords = [
            'linkedin', 'facebook', 'twitter', 'youtube', 'instagram', 'wikipedia',
            'google', 'amazon', 'microsoft', 'apple', 'news', 'blog', 'forum'
        ]
        
        # Check exclusions first
        for exclude in exclude_keywords:
            if exclude in combined:
                return False
        
        # Check healthcare keywords
        return any(keyword in combined for keyword in healthcare_keywords)

    def _extract_urls_from_text(self, text: str) -> Set[str]:
        """Extract URLs from text content"""
        url_pattern = r'https?://[^\s<>"\']+\.[a-z]{2,}'
        urls = re.findall(url_pattern, text)
        
        clean_urls = set()
        for url in urls:
            # Clean URL
            url = url.rstrip('.,;:!?)')
            try:
                parsed = urlparse(url)
                if parsed.netloc and len(parsed.netloc) > 4:
                    clean_urls.add(url)
            except:
                continue
        
        return clean_urls

    def scrape_google_search(self, query: str, pages: int = 3) -> Set[str]:
        """Scrape Google search results for healthcare companies"""
        print(f"   🔍 Google Search: '{query}'")
        companies = set()
        
        for page in range(pages):
            try:
                start = page * 10
                search_url = f"https://www.google.com/search?q={quote(query)}&start={start}"
                
                response = self.session.get(search_url, timeout=10)
                if response.status_code != 200:
                    print(f"      ⚠️ Google blocked request (page {page+1})")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract URLs from search results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/url?q='):
                        # Extract actual URL from Google redirect
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        try:
                            actual_url = requests.utils.unquote(actual_url)
                            if self._is_healthcare_company(actual_url, link.get_text()):
                                companies.add(actual_url)
                        except:
                            continue
                
                time.sleep(random.uniform(2, 4))  # Random delay to avoid blocking
                
            except Exception as e:
                print(f"      ⚠️ Error on page {page+1}: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_crunchbase_search(self, query: str) -> Set[str]:
        """Scrape Crunchbase for healthcare companies"""
        print(f"   🔍 Crunchbase: '{query}'")
        companies = set()
        
        try:
            # Search Crunchbase
            search_url = f"https://www.crunchbase.com/discover/organization.companies/f/{quote(query)}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract company URLs from Crunchbase results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/organization/' in href:
                        # Get the full company page
                        company_url = urljoin('https://www.crunchbase.com', href)
                        company_info = self._scrape_crunchbase_company(company_url)
                        if company_info:
                            companies.add(company_info)
                
        except Exception as e:
            print(f"      ⚠️ Crunchbase error: {str(e)[:50]}")
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def _scrape_crunchbase_company(self, company_url: str) -> str:
        """Extract company website from Crunchbase company page"""
        try:
            response = self.session.get(company_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for website links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and 'crunchbase.com' not in href:
                        if self._is_healthcare_company(href):
                            return href
            
            time.sleep(1)
        except:
            pass
        
        return None

    def scrape_european_business_directories(self) -> Set[str]:
        """Scrape European business directories for healthcare companies"""
        print("   🔍 European Business Directories")
        companies = set()
        
        directories = [
            "https://www.europages.com/companies/Healthcare.html",
            "https://www.kompass.com/selectcountry/healthcare/",
            "https://www.alibaba.com/catalogs/companies?SearchText=healthcare+europe",
            "https://www.thomasnet.com/browse/healthcare-medical/",
        ]
        
        for directory in directories:
            try:
                print(f"      📋 Scraping: {directory}")
                response = self.session.get(directory, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = urljoin(directory, href)
                        
                        # Check if it's an external company website
                        if (href.startswith('http') and 
                            urlparse(href).netloc != urlparse(directory).netloc and
                            self._is_healthcare_company(href, link.get_text())):
                            companies.add(href)
                    
                    # Also extract URLs from text content
                    text_urls = self._extract_urls_from_text(response.text)
                    for url in text_urls:
                        if self._is_healthcare_company(url):
                            companies.add(url)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"      ⚠️ Directory error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_industry_associations(self) -> Set[str]:
        """Scrape healthcare industry association member directories"""
        print("   🔍 Industry Associations")
        companies = set()
        
        # Real industry association websites with member directories
        associations = [
            "https://www.bio.org/membership/member-directory",
            "https://www.efpia.eu/about-medicines/",
            "https://www.medtecheurope.org/about-medtech/",
            "https://www.eucomed.org/members",
            "https://www.ema.europa.eu/en/partners-networks/organisations",
        ]
        
        for assoc_url in associations:
            try:
                print(f"      🏛️ Scraping: {urlparse(assoc_url).netloc}")
                response = self.session.get(assoc_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for member company links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Convert relative URLs
                        if href.startswith('/'):
                            href = urljoin(assoc_url, href)
                        
                        # Check for external company websites
                        if (href.startswith('http') and 
                            urlparse(href).netloc != urlparse(assoc_url).netloc and
                            self._is_healthcare_company(href, link.get_text())):
                            companies.add(href)
                
                time.sleep(3)  # Longer delay for association sites
                
            except Exception as e:
                print(f"      ⚠️ Association error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_government_databases(self) -> Set[str]:
        """Scrape government health databases for companies"""
        print("   🔍 Government Health Databases")
        companies = set()
        
        # Government health-related pages that might list companies
        gov_sources = [
            "https://www.ema.europa.eu/en/medicines/field_ema_web_categories%253Aname_field/Human/field_ema_medicine_types/field_medicine_therapeutic_area",
            "https://ec.europa.eu/health/medical-devices/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en",
            "https://www.bfarm.de/EN/Medical-devices/_node.html",
            "https://www.ansm.sante.fr/Activites/Medicaments/",
        ]
        
        for gov_url in gov_sources:
            try:
                print(f"      🏛️ Government: {urlparse(gov_url).netloc}")
                response = self.session.get(gov_url, timeout=20)
                
                if response.status_code == 200:
                    # Extract URLs from text content
                    text_urls = self._extract_urls_from_text(response.text)
                    for url in text_urls:
                        if self._is_healthcare_company(url):
                            companies.add(url)
                
                time.sleep(5)  # Longer delay for government sites
                
            except Exception as e:
                print(f"      ⚠️ Government error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def run_real_discovery(self) -> List[str]:
        """Run REAL web scraping discovery"""
        print("🕷️ REAL WEB SCRAPING DISCOVERY - NO HARDCODED LISTS!")
        print("=" * 80)
        print("🔍 Actually scraping live web sources to find companies")
        print("⚠️  Some sources may block or limit requests")
        print("🎯 Finding NEW companies through automated discovery")
        print()
        
        start_time = time.time()
        
        # Search queries for different regions/types
        search_queries = [
            "healthcare companies Germany",
            "pharmaceutical companies Europe", 
            "biotech companies France",
            "medical device companies UK",
            "digital health startups Netherlands",
            "medtech companies Switzerland",
            "healthcare technology Europe",
            "pharmaceutical industry Germany",
            "biotech firms Europe",
            "medical companies Europe site:company.com",
            "healthcare site:health.com",
            "pharma companies site:pharma.com"
        ]
        
        # 1. Google Search Discovery
        print("🔍 Phase 1: Search Engine Discovery")
        for query in search_queries[:6]:  # Limit to avoid too many requests
            try:
                search_results = self.scrape_google_search(query, pages=2)
                self.discovered_companies.update(search_results)
                time.sleep(random.uniform(3, 6))  # Random delay between searches
            except Exception as e:
                print(f"   ⚠️ Search failed for '{query}': {str(e)[:50]}")
                continue
        
        # 2. Business Directory Discovery  
        print("\n🔍 Phase 2: Business Directory Discovery")
        try:
            directory_results = self.scrape_european_business_directories()
            self.discovered_companies.update(directory_results)
        except Exception as e:
            print(f"   ⚠️ Directory scraping failed: {str(e)[:50]}")
        
        # 3. Industry Association Discovery
        print("\n🔍 Phase 3: Industry Association Discovery")
        try:
            association_results = self.scrape_industry_associations()
            self.discovered_companies.update(association_results)
        except Exception as e:
            print(f"   ⚠️ Association scraping failed: {str(e)[:50]}")
        
        # 4. Government Database Discovery
        print("\n🔍 Phase 4: Government Database Discovery")
        try:
            gov_results = self.scrape_government_databases()
            self.discovered_companies.update(gov_results)
        except Exception as e:
            print(f"   ⚠️ Government scraping failed: {str(e)[:50]}")
        
        # 5. Crunchbase Discovery (if not blocked)
        print("\n🔍 Phase 5: Crunchbase Discovery")
        crunchbase_queries = ["healthcare europe", "biotech germany", "medtech france"]
        for query in crunchbase_queries:
            try:
                cb_results = self.scrape_crunchbase_search(query)
                self.discovered_companies.update(cb_results)
                time.sleep(random.uniform(4, 7))
            except Exception as e:
                print(f"   ⚠️ Crunchbase failed for '{query}': {str(e)[:50]}")
                continue
        
        # Convert to list and clean up
        all_companies = list(self.discovered_companies)
        
        # Remove duplicates and invalid URLs
        cleaned_companies = []
        seen_domains = set()
        
        for url in all_companies:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '')
                
                if domain not in seen_domains and len(domain) > 4:
                    seen_domains.add(domain)
                    cleaned_companies.append(url)
            except:
                continue
        
        runtime = time.time() - start_time
        
        print(f"\n🎉 REAL DISCOVERY COMPLETE!")
        print("=" * 80)
        print(f"📊 RESULTS:")
        print(f"   Companies discovered: {len(cleaned_companies)}")
        print(f"   Sources scraped: Google, Directories, Associations, Government, Crunchbase")
        print(f"   Runtime: {runtime:.1f} seconds")
        print(f"   Discovery rate: {len(cleaned_companies)/runtime:.1f} companies/second")
        print(f"   Method: 100% REAL web scraping - NO hardcoded lists!")
        
        if len(cleaned_companies) == 0:
            print("\n⚠️  WARNING: No companies found!")
            print("   This could be due to:")
            print("   - Anti-bot protections blocking requests")
            print("   - Rate limiting by websites")
            print("   - Network connectivity issues")
            print("   - Websites changing their structure")
        
        return cleaned_companies

    def save_results(self, companies: List[str]):
        """Save discovered companies to files"""
        if not companies:
            print("❌ No companies to save")
            return
        
        print(f"\n💾 Saving {len(companies)} discovered companies...")
        
        # Save to CSV
        csv_filename = "real_discovered_companies.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Domain', 'Discovery_Method'])
            
            for url in companies:
                try:
                    domain = urlparse(url).netloc.replace('www.', '')
                    writer.writerow([url, domain, 'Web_Scraping'])
                except:
                    continue
        
        # Save to JSON
        json_filename = "real_discovered_companies.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'discovery_method': 'Real Web Scraping',
                'total_companies': len(companies),
                'companies': companies
            }, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to {csv_filename}")
        print(f"   ✅ Saved to {json_filename}")


if __name__ == "__main__":
    print("🕷️ REAL Web Scraping Healthcare Discovery")
    print("Actually discovers companies by scraping live web sources!")
    print("NO HARDCODED LISTS - Pure automated discovery")
    print()
    
    # Run real discovery
    scraper = RealWebScraper()
    companies = scraper.run_real_discovery()
    
    # Show results
    if companies:
        print(f"\n📊 DISCOVERED COMPANIES (first 20):")
        for i, company in enumerate(companies[:20], 1):
            print(f"{i:2d}. {company}")
        
        if len(companies) > 20:
            print(f"... and {len(companies) - 20} more!")
        
        # Save results
        scraper.save_results(companies)
        
        print(f"\n🎉 SUCCESS!")
        print(f"Actually discovered {len(companies)} companies through web scraping")
        print("🕷️ This is REAL automated discovery - no cheating!")
    else:
        print("\n😞 No companies discovered")
        print("This is the honest truth - web scraping can be limited by:")
        print("- Anti-bot protections")
        print("- Rate limiting")
        print("- Website changes")
        print("- Network issues")